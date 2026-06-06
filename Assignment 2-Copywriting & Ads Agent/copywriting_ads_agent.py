"""
copywriting_ads_agent.py
------------------------
A professional Copywriting & Ads Agent built with the Microsoft Agent Framework.

The agent reads its behavior rules from `instructions.md` and uses Google
Gemini (gemini-2.5-flash) to generate persuasive, platform-specific ad copy
(Headline, Body, Call-to-Action).

Gemini exposes an OpenAI-compatible API, so we reuse the *exact same* LLM
configuration as Assignment 1: the Agent Framework's OpenAI-compatible
chat-completions client pointed at Gemini's endpoint, using the same
GEMINI_API_KEY.

Run it from the terminal:
    python copywriting_ads_agent.py
"""

import asyncio
import os
from pathlib import Path

# `load_dotenv` reads key/value pairs from a local `.env` file into
# environment variables so we never hard-code secrets in the source code.
from dotenv import load_dotenv

# The Microsoft Agent Framework's OpenAI-compatible chat-completions client.
# Gemini exposes an OpenAI-compatible "/chat/completions" endpoint, so this
# client works with it once we provide Gemini's base URL and API key.
# (Same client/config as Assignment 1.)
from agent_framework.openai import OpenAIChatCompletionClient


# Gemini's OpenAI-compatible base URL (identical to Assignment 1).
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# The Gemini text model used for copy generation (identical to Assignment 1).
# gemini-2.5-flash has free-tier quota; transient "503 busy" spikes are
# handled automatically by the retry logic in generate_ad_copy().
GEMINI_MODEL = "gemini-2.5-flash"

# Folder that contains this script. Using it guarantees we can locate
# `instructions.md` and `.env` no matter which directory the script runs from.
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
    Build and return a Copywriting & Ads Agent backed by Google Gemini.

    The Gemini API key is read from the GEMINI_API_KEY environment variable
    (loaded from your `.env` file) so secrets never live in the source code.
    This is the same key and the same LLM config used in Assignment 1.
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
        name="CopywritingAdsAgent",
        instructions=instructions,
    )


def build_brief(
    product: str,
    audience: str,
    platform: str,
    key_points: str = "",
    brand_tone: str = "",
) -> str:
    """
    Assemble a clear advertising brief from the structured inputs that
    `instructions.md` expects (product, audience, platform, key points,
    optional brand tone). This single string is what we send to the agent.
    """
    lines = [
        "Please write ad copy based on the following brief:",
        f"- Product/Service: {product}",
        f"- Target Audience: {audience}",
        f"- Advertising Platform: {platform}",
    ]
    if key_points.strip():
        lines.append(f"- Key Points / Benefits: {key_points}")
    if brand_tone.strip():
        lines.append(f"- Brand Tone/Voice: {brand_tone}")
    return "\n".join(lines)


async def generate_ad_copy(
    product: str,
    audience: str,
    platform: str,
    key_points: str = "",
    brand_tone: str = "",
    max_retries: int = 5,
) -> str:
    """
    Send an advertising brief to the agent and return the generated ad copy
    (Headline, Body, Call-to-Action).

    Gemini can occasionally return a temporary "503 / high demand" error.
    We retry a few times with an increasing (exponential) wait so these
    transient spikes don't crash the program.
    """
    agent = create_agent()
    brief = build_brief(product, audience, platform, key_points, brand_tone)

    for attempt in range(1, max_retries + 1):
        try:
            # `run` performs a single request/response turn with the model.
            result = await agent.run(brief)
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
    raise RuntimeError("Failed to generate ad copy after retries.")


async def main() -> None:
    """Entry point: collect the advertising brief interactively from the user."""
    # Load .env values from the same folder as this script (same key as
    # Assignment 1), so the key is found no matter which directory you run from.
    load_dotenv(BASE_DIR / ".env")

    print("=== Copywriting & Ads Agent ===\n")
    product = input("Product / Service: ").strip()
    audience = input("Target Audience: ").strip()
    platform = input("Platform (Facebook / Google / LinkedIn): ").strip()
    key_points = input("Key Points / Benefits (optional): ").strip()
    brand_tone = input("Brand Tone/Voice (optional): ").strip()

    if not product or not audience or not platform:
        print("\nProduct, audience, and platform are required. Exiting.")
        return

    print("\nGenerating ad copy, please wait...\n")
    copy = await generate_ad_copy(
        product, audience, platform, key_points, brand_tone
    )
    print(copy)


if __name__ == "__main__":
    # `asyncio.run` starts the event loop because the agent calls are async.
    asyncio.run(main())
