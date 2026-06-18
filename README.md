# Daily Sync Report Generator (Kanban + GitLab + OpenAI + TTS)

A small automation tool that collects your recent GitLab commit activity and your assigned Kanban tasks, then uses an OpenAI chat model to generate a natural, spoken-style daily standup update
Optionally, it can convert the report into an MP3 using OpenAI Text-to-Speech.

---

## Project Overview

This project is designed to streamline daily standup reporting by automatically:
- Scraping your assigned tasks from a web-based Kanban board (via Playwright session).
- Fetching your recent commits from GitLab and extracting the touched files (diff paths).
- Generating a short, fluent daily update using an LLM prompt tailored for spoken delivery.
- Optionally producing an audio file (`daily_report.mp3`) from the generated report.

---

## Features

- **Kanban task scraping** (Playwright, authenticated session stored in `auth_state.json`)
- **GitLab commit fetching** for one or more branches, filtered by author identity
- **Commit diff extraction** (list of touched file paths per commit)
- **Daily report generation** using OpenAI Chat Completions
- **Text-to-Speech (TTS)** generation with OpenAI (`tts-1`), outputting an MP3
- Async pipeline (Git scraping + report generation + TTS)

---

## Installation

### 1) Prerequisites
- Python 3.10+ recommended (project currently uses async + Playwright)
- A GitLab Personal Access Token with API access to read repository commits/diffs
- An OpenAI API key
- Playwright browser dependencies installed

### 2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4) Install Playwright browsers
```bash
playwright install
```

### 5) Configure environment variables
Copy the example file and fill it in:

```bash
cp .env.example .env
```

`.env.example` contains:
```env
OPENAI_API_KEY=

GITLAB_URL=
KANBAN_BOARD_URL=
KANBAN_LOGIN_URL=
KANBAN_USER=
KANBAN_PASS=
```

You will also need the following (used in code but not listed in `.env.example`):
- `GITLAB_TOKEN` (required)
- `PROJECT_ID` (defaults to `381` if not set)

Example:
```env
OPENAI_API_KEY=your_openai_key

GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=your_gitlab_token
PROJECT_ID=381

KANBAN_BOARD_URL=https://kanban.example.com/board
KANBAN_LOGIN_URL=https://kanban.example.com/login
KANBAN_USER=you@example.com
KANBAN_PASS=your_password
```

---

## Usage

### Run the tool
```bash
python main.py
```

What it does:
1. Refreshes/creates a Kanban authenticated session (`auth_state.json`).
2. Scrapes your tasks from the Kanban board.
3. Fetches your commits since the “last daily” time window for configured branches.
4. Fetches diffs for each commit and compiles touched file paths.
5. Sends all context to the LLM and prints a daily report.
6. Asks whether to generate speech (`Create speech?`). Type `y` to produce `daily_report.mp3`.

### Adjust branches and time window
In `main.py`:
- `branches` controls which Git branches to query
- `get_data(branches, 3)` controls how many days back to look

---

## Project Structure

```text
.
├── main.py                      # Orchestrates scraping, report generation, and optional TTS
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variable template
├── auth_state.json              # Playwright storage state (ignored by git)
├── llm/
│   └── llm.py                   # OpenAI prompt + report generation
├── scrapper/
│   ├── github/
│   │   └── scrapper.py          # GitLab commits + diff extraction
│   └── kanban/
│       ├── scrapper.py          # Kanban task scraper (Playwright)
│       └── sesion.py            # Login + storage_state refresh
└── tts/
    └── tts.py                   # OpenAI TTS wrapper (outputs MP3)
```

---

## Development Notes

### Authentication / session handling (Kanban)
- The Kanban scraper relies on Playwright’s `storage_state` saved to `auth_state.json`.
- **Important:** `scrapper/kanban/sesion.py` currently runs `asyncio.run(auto_login())` at import time, meaning it will attempt to log in whenever the module is imported. This is convenient for quick runs but is not ideal for library-style code. Consider moving that call behind a `if __name__ == "__main__":` guard or only calling `auto_login()` from `main.py`.

### GitLab commit scraping behavior
- Commits are fetched via GitLab API: `/api/v4/projects/{PROJECT_ID}/repository/commits`
- Author filtering is currently hardcoded to a specific email/name.
- `get_commits_since_last_daily()` currently returns inside the loop (after the first branch). If you intend to process multiple branches, move the `return commits` outside the `for branch in branches:` loop.

### Time window logic
- `get_past_date_iso(days_ago)` sets the time to **17:30 UTC** on the computed day. Adjust as needed for your daily schedule and timezone expectations.

### LLM model
- The report generator uses `gpt-3.5-turbo` via `client.chat.completions.create(...)`.
- The prompt is currently written in Spanish and optimized for TTS output formatting rules, but your README requirement is English-only; if you want English spoken output, update the prompt instructions accordingly.

### Text-to-Speech output
- TTS uses `model="tts-1"` and `voice="onyx"`.
- Output defaults to `daily_report.mp3` and is gitignored.

### Security
- Do not commit `.env` or `auth_state.json`. They are already included in `.gitignore`.
- Treat Playwright storage state as sensitive; it may include session cookies.

---