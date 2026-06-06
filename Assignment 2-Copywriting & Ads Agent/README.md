# Assignment 2 — Copywriting & Ads Agent

A professional **Copywriting & Ads Agent** built with the **Microsoft Agent Framework** in **Python**, powered by **Google Gemini**. It writes persuasive, platform-specific ad copy (**Headline, Body, Call-to-Action**) **and** generates a matching advertising **graphic/image** for the topic.

- **Text copy** uses the *same* LLM config as Assignment 1 (Gemini `gemini-2.5-flash` via the OpenAI-compatible endpoint, same `GEMINI_API_KEY`).
- **Images** try Gemini's image model (`gemini-2.5-flash-image`) first, using that same key. Gemini image generation needs a billing-enabled Google project (the free tier returns `limit: 0`), so when it is unavailable the app automatically falls back to a **locally composed ad creative** (built with Pillow) — meaning a topic-specific graphic is **always** produced, with no extra cost.

The agent's behavior rules live in [instructions.md](instructions.md) and are loaded automatically at runtime.

---

## Project structure

| File | Purpose |
|------|---------|
| `copywriting_ads_agent.py` | The ad-copy agent code (self-explanatory, fully commented) |
| `image_generator.py` | Generates the ad graphic/image (Gemini → local Pillow fallback) |
| `app.py` | Streamlit web UI (copy + image demo) |
| `instructions.md` | The rules / system prompt for the agent |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your credentials (copy to `.env`) |

---

## Prerequisites

- **Python 3.10 or higher** — check with `python --version`
- A **Google Gemini API key** — the **same one used in Assignment 1** (get one free at <https://aistudio.google.com/apikey>)

---

## Step-by-step setup

### 1. Open a terminal in the project folder

```powershell
cd "Assignment 2-Copywriting & Ads Agent"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> On macOS / Linux use: `source .venv/bin/activate`

### 3. Install the dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure your credentials

Copy the example environment file and use the **same key as Assignment 1**:

```powershell
copy .env.example .env
```

Then open `.env` and set your Gemini API key:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
```

---

## Run the agent (command line)

```powershell
python copywriting_ads_agent.py
```

You'll be prompted for the product, audience, platform, key points, and brand tone, and the agent prints the ad copy.

## Run the demo UI (copy + image)

```powershell
streamlit run app.py
```

Fill in the brief, keep **"Also generate an ad graphic/image"** checked, and the app shows the generated **ad copy** and a matching **graphic** (with a download button).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: agent_framework` / `google.genai` | Activate the venv and run `pip install -r requirements.txt` again |
| Authentication / 401 error | Check that `GEMINI_API_KEY` in `.env` is the valid key from Assignment 1 |
| `instructions.md` not found | Run the command from inside the project folder |
| Image model returns no image | The free Gemini tier has no image quota; the app automatically falls back to the local Pillow ad creative. To get AI photo images, enable billing on your Google project |
