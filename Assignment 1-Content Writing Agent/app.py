"""
app.py
------
A simple Streamlit web UI for the Content Writing Agent.

The user types a blog/content title, clicks a button, and the agent
(powered by Google Gemini through the Microsoft Agent Framework) generates
well-structured written content that is displayed back in the browser.

This UI reuses the exact same logic as the command-line script by importing
`generate_content` from `content_writing_agent.py`, so the agent behaves
identically whether you use the terminal or the web UI.

Run it from the terminal:
    streamlit run app.py
"""

import asyncio
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Reuse the agent logic from the existing script so we have a single source
# of truth for how content is generated.
from content_writing_agent import generate_content

# Folder that contains this script, used to locate the local `.env` file.
BASE_DIR = Path(__file__).parent

# Load the GEMINI_API_KEY (and any other secrets) from the `.env` file that
# lives next to this script, so the key is available no matter where Streamlit
# is launched from.
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Content Writing Agent",
    page_icon="✍️",
    layout="centered",
)

st.title("✍️ Content Writing Agent")
st.caption(
    "Powered by Google Gemini and the Microsoft Agent Framework. "
    "Enter a title and the agent will write structured content for you."
)


# ---------------------------------------------------------------------------
# Input form
# ---------------------------------------------------------------------------
# Using a form means the agent only runs when the user clicks the button
# (not on every keystroke).
with st.form("content_form"):
    title = st.text_input(
        "Blog / Content Title",
        placeholder="e.g. The Importance of Water",
    )
    submitted = st.form_submit_button("Generate Content")


# ---------------------------------------------------------------------------
# Handle submission
# ---------------------------------------------------------------------------
if submitted:
    if not title.strip():
        # Guard against empty input.
        st.warning("Please enter a title to generate content.")
    else:
        # Show a spinner while the (async) agent call runs.
        with st.spinner("Generating content, please wait..."):
            try:
                # `generate_content` is an async function, so we run it inside
                # a fresh event loop with `asyncio.run`.
                content = asyncio.run(generate_content(title.strip()))
                # Render the generated content as Markdown so the agent's
                # headings, bullet points, and formatting display nicely.
                st.markdown(content)
            except Exception as error:
                # Surface any errors (missing API key, quota limits, etc.)
                # to the user instead of crashing the app.
                st.error(f"Something went wrong: {error}")
