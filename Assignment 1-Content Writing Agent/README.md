# Assignment 1 — Content Writing Agent

A professional **Content Writing Agent** built with the **Microsoft Agent Framework** in **Python**, powered by **Google Gemini (gemini-2.5-flash)**. It generates well-structured written content (Title, Introduction, Main Content, Conclusion) in simple language suitable for students.

The agent's behavior rules live in [instructions.md](instructions.md) and are loaded automatically at runtime.

You can use the agent two ways:

- **Web UI** — a [Streamlit](https://streamlit.io/) app (`app.py`) where you type a title and see the content in your browser.
- **Command line** — run `content_writing_agent.py` directly in the terminal.

Both interfaces call the **same** `generate_content()` function, so the agent behaves identically no matter how you run it.

---

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web UI for the agent |
| `content_writing_agent.py` | The agent code (self-explanatory, fully commented) |
| `instructions.md` | The rules / system prompt for the agent |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your credentials (copy to `.env`) |

---

## Prerequisites

- **Python 3.10 or higher** — check with `python --version`
- A **Google Gemini API key** — get one free at <https://aistudio.google.com/apikey>

---

## Step-by-step setup

### 1. Open a terminal in the project folder

```powershell
cd "Assignment 1-Content Writing Agent"
```

### 2. Create and activate a virtual environment

```powershell
# Create the virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

> On macOS / Linux use: `source .venv/bin/activate`

### 3. Install the dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure your credentials

Copy the example environment file and fill in your value:

```powershell
copy .env.example .env
```

Then open `.env` and set your Gemini API key:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
```

---

## Run the agent

### Option A — Web UI (Streamlit, recommended)

Launch the web app from inside the project folder:

```powershell
streamlit run app.py
```

Streamlit opens the app in your browser at <http://localhost:8501>. Enter a
blog/content title, click **Generate Content**, and the structured content is
rendered on the page.

> Only one Streamlit app can use port `8501` at a time. If the page shows a
> different app, stop the old session first (press `Ctrl+C` in its terminal),
> then relaunch from this folder.

### Option B — Command line

Pass a topic directly:

```powershell
python content_writing_agent.py "Write an essay on the importance of water"
```

Or run without arguments to be prompted for a topic:

```powershell
python content_writing_agent.py
```

The agent prints the generated content (Title, Introduction, Main Content with points, and Conclusion) to the terminal.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: agent_framework` | Make sure the virtual environment is activated and run `pip install -r requirements.txt` again |
| `streamlit: command not found` | Activate the virtual environment, then run `pip install -r requirements.txt` (Streamlit is listed there) |
| Browser shows the wrong app / port `8501` busy | Stop the other Streamlit session (`Ctrl+C` in its terminal) and relaunch `streamlit run app.py` from this folder |
| Authentication / 401 error | Check that `GEMINI_API_KEY` in `.env` is valid (get one at <https://aistudio.google.com/apikey>) |
| `instructions.md` not found | Run the command from inside the project folder |
