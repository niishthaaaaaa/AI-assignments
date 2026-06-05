"""
content_writing_agent.py
------------------------
A professional Content Writing Agent built with the Microsoft Agent Framework.

The agent reads its behavior rules from `instructions.md` and uses Google
Gemini (gemini-2.5-flash) to generate well-structured written content
(Title, Introduction, Main Content, Conclusion).

Gemini exposes an OpenAI-compatible API, so we use the Agent Framework's
`OpenAIChatClient` and simply point it at Gemini's endpoint.

Run it from the terminal:
    python content_writing_agent.py "Write an essay on the importance of water"

Or run it without arguments to enter interactive mode.
"""

import asyncio
import os
import sys
from pathlib import Path

# `load_dotenv` reads key/value pairs from a local `.env` file into
# environment variables so we never hard-code secrets in the source code.
from dotenv import load_dotenv

# The Microsoft Agent Framework's OpenAI-compatible chat-completions client.
# Gemini exposes an OpenAI-compatible "/chat/completions" endpoint, so this
# client works with it once we provide Gemini's base URL and API key.
# (We use the *ChatCompletion* client specifically, because Gemini does not
# implement OpenAI's newer "/responses" endpoint.)
from agent_framework.openai import OpenAIChatCompletionClient


# Gemini's OpenAI-compatible base URL. The Agent Framework talks to this
# endpoint exactly as it would talk to OpenAI.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# The Gemini model we want to use for content generation.
# gemini-2.5-flash has free-tier quota on this key; transient "503 busy"
# spikes are handled automatically by the retry logic in generate_content().
GEMINI_MODEL = "gemini-2.5-flash"

# Folder that contains this script. Using it guarantees we can locate
# `instructions.md` no matter which directory the script is launched from.
BASE_DIR = Path(__file__).parent


def load_instructions() -> str:
    """Read the agent's behavior rules from `instructions.md`."""
    instructions_path = BASE_DIR / "instructions.md"
    if not instructions_path.exists():
        raise FileNotFoundError(
            f"Could not find instructions file at: {instructions_path}"
        )
    return instructions_path.read_text(encoding="utf-8")


def create_agent():
    """
    Build and return a Content Writing Agent backed by Google Gemini.

    The Gemini API key is read from the GEMINI_API_KEY environment variable
    (loaded from your `.env` file) so secrets never live in the source code.
    """
    instructions = load_instructions()

    # Read the Gemini API key from the environment.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    # Point the OpenAI-compatible client at Gemini's endpoint and model.
    chat_client = OpenAIChatCompletionClient(
        model=GEMINI_MODEL,
        api_key=api_key,
        base_url=GEMINI_BASE_URL,
    )

    # `as_agent` wires the model together with our custom instructions.
    return chat_client.as_agent(
        name="ContentWritingAgent",
        instructions=instructions,
    )


async def generate_content(topic: str, max_retries: int = 5) -> str:
    """
    Send a topic to the agent and return the generated written content.

    Gemini can occasionally return a temporary "503 / high demand" error.
    We retry a few times with an increasing (exponential) wait so these
    transient spikes don't crash the program.
    """
    agent = create_agent()

    for attempt in range(1, max_retries + 1):
        try:
            # `run` performs a single request/response turn with the model.
            result = await agent.run(topic)
            return result.text
        except Exception as error:
            # Only retry on transient "service unavailable / overloaded" errors.
            message = str(error)
            is_transient = "503" in message or "UNAVAILABLE" in message
            if not is_transient or attempt == max_retries:
                raise
            wait_seconds = 2 ** attempt  # 2, 4, 8, 16 seconds ...
            print(
                f"Model busy (attempt {attempt}/{max_retries}). "
                f"Retrying in {wait_seconds}s..."
            )
            await asyncio.sleep(wait_seconds)

    # This line is never reached, but keeps type checkers happy.
    raise RuntimeError("Failed to generate content after retries.")


async def main() -> None:
    """Entry point: take a topic from the command line or prompt the user."""
    # Load .env values from the same folder as this script, so the key is
    # found no matter which directory you run the command from.
    load_dotenv(BASE_DIR / ".env")

    # Topic can be passed as command-line arguments, e.g.
    #   python content_writing_agent.py "Benefits of reading books"
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter the content topic: ").strip()

    if not topic:
        print("No topic provided. Exiting.")
        return

    print("\nGenerating content, please wait...\n")
    content = await generate_content(topic)
    print(content)


if __name__ == "__main__":
    # `asyncio.run` starts the event loop because the agent calls are async.
    asyncio.run(main())
