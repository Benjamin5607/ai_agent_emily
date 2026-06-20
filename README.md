# Emily AI: PM Agent

**Emily** is a Streamlit-based AI project management agent that turns a project idea into a structured plan, architecture notes, optional code snippets, social media drafts, and Notion workspace cards — powered by the Groq API.

Version referenced in the app: **v5.7 (Global Edition)**

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [User Manual](#user-manual)
  - [1. Launch the app](#1-launch-the-app)
  - [2. Configure the sidebar](#2-configure-the-sidebar)
  - [3. Enter your project idea](#3-enter-your-project-idea)
  - [4. Run Emily PM](#4-run-emily-pm)
  - [5. Review outputs](#5-review-outputs)
- [Notion Integration Setup](#notion-integration-setup)
- [Groq API Setup](#groq-api-setup)
- [Agent Workflow](#agent-workflow)
- [Notion Output Structure](#notion-output-structure)
- [Configuration Reference](#configuration-reference)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [License](#license)

---

## Overview

Emily acts as a multi-role AI assistant for early-stage project planning. You describe a goal (in Korean or English), choose a PM methodology, and Emily orchestrates several specialized agent steps:

1. **Project Manager** — actionable task breakdown using your chosen methodology
2. **System Architect** — tech stack and database schema recommendations
3. **Lead Software Engineer** *(optional)* — frontend/backend code snippets
4. **Growth Marketer** *(optional)* — X (Twitter) thread and LinkedIn post drafts

When Notion is connected, Emily can automatically write wiki-style document cards and structured task cards (with RACI, tools, timeline, and sub-task checklists) into a database you select.

All AI-generated project content is produced in **English**, regardless of the UI language or input language.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI framework** | [Streamlit](https://streamlit.io/) | Web app shell, sidebar settings, progress UI, file upload |
| **LLM provider** | [Groq API](https://groq.com/) via `groq` Python SDK | Fast inference for all agent steps |
| **Project management** | Notion REST API (`requests`) | Database search, property setup, page/card creation |
| **HTTP client** | `requests` | Direct Notion API calls (no Notion SDK) |
| **Standard library** | `base64`, `json`, `datetime` | Image encoding, task JSON parsing, date handling |
| **Language** | Python 3.8+ | Application runtime |

### Python Dependencies

```
streamlit
groq
requests
```

Install with:

```bash
pip install -r requirements.txt
```

### External APIs

| API | Required? | Used for |
|-----|-----------|----------|
| **Groq API** | Yes | Model listing, chat completions for all agent roles |
| **Notion API** | No | Auto-creating wiki docs and task cards in a selected database |

### Supported Groq Models

The app dynamically lists available Groq models when a valid API key is entered. Models containing `whisper` or `preview` in the ID are filtered out. If the key is missing or invalid, a fallback list is shown.

Default fallback models:
- `llama3-70b-8192`
- `llama3-8b-8192`

### Notion API Version

The app uses Notion API version **`2022-06-28`**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI (app.py)                    │
│  Sidebar: API keys, model, temperature, theme, PM method   │
│  Main: project idea input, options, run button, results      │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │  Groq API   │  │ Notion API  │  │ Session     │
   │  (LLM)      │  │ (optional)  │  │ State       │
   └─────────────┘  └─────────────┘  └─────────────┘
```

**Data flow:**

1. User input (idea + PM method) becomes `full_context`.
2. Each agent step appends its output to `full_context` for downstream steps.
3. Optional Notion sync creates document cards from each step's markdown output.
4. A separate JSON extraction prompt generates 5–7 task cards with RACI, tools, and dates.

---

## Features

### Bilingual UI (Korean / English)

The interface labels, warnings, and status messages support **한국어** and **English**. AI outputs are always in English.

### Bring Your Own Key (BYOK)

API credentials are entered in the sidebar and stored in Streamlit session state. They are not persisted to disk by the app.

### PM Methodologies

Choose one of four approaches before running:

| Method | Typical use |
|--------|-------------|
| **Agile** | Iterative delivery, flexible scope |
| **Scrum** | Sprint-based development |
| **Kanban** | Continuous flow, WIP limits |
| **Waterfall** | Sequential phases |

The selected method influences planning prompts and task naming (e.g., `[Sprint 1]`, `[Phase 2]`).

### Customizable AI Behavior

- **Model selection** — pick any available Groq chat model
- **Temperature** — slider from `0.0` (deterministic) to `1.0` (creative); default `0.7`
- Task JSON extraction uses a lower temperature (`0.2`) for structured output

### UI Customization

- Upload a local image (PNG, JPG, JPEG) as a full-page background
- Or pick a solid background color (default `#F0F2F6`)

### Optional Outputs

| Checkbox | Output |
|----------|--------|
| **Generate Core Feature Code (FE/BE)** | Adds a Lead Software Engineer step with code snippets |
| **Generate X/LinkedIn Promo Posts** | Adds a Growth Marketer step (enabled by default) |

### Notion Workspace Automation

When a Notion token and database are configured, Emily:

1. Patches the database schema to add `RACI`, `Required Tool`, and `Timeline` properties
2. Creates wiki document cards for each agent step
3. Creates 5–7 task cards with user stories, to-do sub-tasks, RACI, tools, and date ranges

---

## Prerequisites

- **Python 3.8 or higher**
- **Groq API key** — [https://console.groq.com](https://console.groq.com)
- **Notion integration token** *(optional)* — [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
- A Notion database with at least one **title** property, shared with your integration

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Streamlit opens the app in your browser (default: `http://localhost:8501`).

---

## User Manual

### 1. Launch the app

Run `streamlit run app.py` and open the URL shown in the terminal.

### 2. Configure the sidebar

Work through the sidebar from top to bottom:

#### Language

Select **한국어** or **English** for UI text.

#### API Integration (BYOK)

| Field | Required | Description |
|-------|----------|-------------|
| **Groq API Key** | Yes | Your Groq API key. Without it, the app cannot run agents. |
| **Notion Secret Token** | No | Enables automatic Notion workspace creation. |

After entering a Notion token, the app searches your workspace for accessible databases. Select one from the dropdown. If none appear, invite the integration to the target page (see [Notion Integration Setup](#notion-integration-setup)).

#### Agent Brain Settings

| Setting | Description |
|---------|-------------|
| **Select Model** | Groq model used for all agent steps |
| **Creativity Level (Temperature)** | `0.0`–`1.0`; higher = more varied responses |

#### Background Customization

- Upload an image, **or**
- Choose a background color with the color picker

#### Project Management Method

Select **Agile**, **Scrum**, **Kanban**, or **Waterfall**.

### 3. Enter your project idea

In the main panel, describe your project in the text area. Examples:

- `Plan and launch an AI-powered diet tracking app`
- `AI 기반 다이어트 앱 기획 및 런칭` *(input in Korean is fine; output will be English)*

Optional checkboxes:

- **Generate Core Feature Code (FE/BE)** — include engineering code snippets
- **Generate X/LinkedIn Promo Posts** — include social media drafts

### 4. Run Emily PM

Click **✨ Start Emily PM!** (or the Korean equivalent).

**Validation:**

- Groq API key must be set → otherwise an error is shown
- Project idea must not be empty → otherwise a warning is shown

A progress bar tracks completion across agent steps and Notion sync.

### 5. Review outputs

Results appear in expandable sections on the page:

| Step | Role | Content |
|------|------|---------|
| 1 | Project Manager (PM) | Methodology-based project plan and tasks |
| 2 | System Architect | Tech stack and database schema |
| 3 *(optional)* | Lead Software Engineer | FE/BE code snippets |
| 4 *(optional)* | Growth Marketer | X thread + LinkedIn post |

If Notion is connected, wiki cards and task cards are created in your selected database. Success and failure messages are shown inline.

On completion, a success message and balloon animation confirm the run finished.

---

## Notion Integration Setup

### Step 1: Create a Notion integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New integration**
3. Name it (e.g., `Emily PM Agent`)
4. Copy the **Internal Integration Secret** — this is your Notion token

### Step 2: Create or choose a database

Create a Notion database (table or board view) that will hold Emily's output. It must have a **title** property (default `Name` works).

### Step 3: Share the database with the integration

1. Open the database page in Notion
2. Click **⋯** (top right) → **Connections** or **Add connections**
3. Select your Emily integration

Without this step, the app will show: *"No accessible DB found. Invite Emily to your Notion page!"*

### Step 4: Paste the token in Emily

Enter the secret in the sidebar **Notion Secret Token** field, then select your database from the dropdown.

### Properties Emily adds automatically

When syncing, Emily patches your database with:

| Property | Type | Used for |
|----------|------|----------|
| `RACI` | Rich text | Responsible / Accountable roles per task |
| `Required Tool` | Multi-select | Technologies and tools |
| `Timeline` | Date | Start and end dates per task |

---

## Groq API Setup

1. Sign up at [https://console.groq.com](https://console.groq.com)
2. Create an API key under **API Keys**
3. Paste the key into the sidebar **Groq API Key** field

The app validates the key by listing models. Invalid keys fall back to a static model list and agent calls will fail at runtime.

---

## Agent Workflow

```
User Idea + PM Method
        │
        ▼
┌───────────────────┐
│ Project Manager   │  Plan tasks using selected methodology
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ System Architect  │  Tech stack + DB schema
└─────────┬─────────┘
          ▼
┌───────────────────┐     (if "Generate Code" checked)
│ Lead SW Engineer  │  FE/BE code snippets
└─────────┬─────────┘
          ▼
┌───────────────────┐     (if "Generate SNS" checked, default on)
│ Growth Marketer   │  X + LinkedIn drafts
└─────────┬─────────┘
          ▼
┌───────────────────┐     (if Notion token + DB selected)
│ Notion Sync       │  Wiki cards + 5–7 task cards
└───────────────────┘
```

Each step receives the accumulated context from all prior steps. System prompts instruct agents to respond as Silicon Valley-tier specialists and output strictly in English with markdown formatting.

---

## Notion Output Structure

### Wiki document cards

| Agent | Card title prefix |
|-------|-------------------|
| Project Manager | `📋 [Master Plan] Project Wiki` |
| System Architect | `🏗️ [Architecture & DB] Project Wiki` |
| Lead Software Engineer | `💻 [Core Code Snippets] Project Wiki` |
| Growth Marketer | `📱 [Marketing Drafts] Project Wiki` |

Content is split into paragraph blocks (max ~1900 characters per block; up to 100 blocks per page).

### Task cards

Each task card includes:

- **Title** — methodology-prefixed task name (e.g., `[Sprint 1] Implement Sign-up API`)
- **Properties** — RACI, Required Tool (multi-select), Timeline (date range)
- **Page body:**
  - `📝 Task Details (User Story)` — description
  - `✅ Sub-tasks (To-Do)` — unchecked checklist items

Tasks are generated via a dedicated JSON prompt requesting 5–7 items based on the project and today's date.

---

## Configuration Reference

| Setting | Location | Default | Notes |
|---------|----------|---------|-------|
| UI language | Sidebar | `한국어` | Korean or English labels only |
| Groq API key | Sidebar | empty | Required to run |
| Notion token | Sidebar | empty | Optional |
| Model | Sidebar | First available Groq model | Cached 1 hour (`@st.cache_data`) |
| Temperature | Sidebar | `0.7` | Agent creativity |
| Background | Sidebar | `#F0F2F6` | Image overrides color |
| PM method | Sidebar | `Agile` | Agile / Scrum / Kanban / Waterfall |
| Generate code | Main panel | unchecked | Adds engineer step |
| Generate SNS | Main panel | checked | Adds marketer step |
| Page layout | `st.set_page_config` | `wide` | Full-width layout |

---

## Project Structure

```
.
├── app.py              # Main Streamlit application (UI, agents, Notion sync)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

All application logic lives in a single `app.py` file (~330 lines). There are no separate modules, tests, or deployment configs in this repository.

---

## Troubleshooting

| Issue | Likely cause | Solution |
|-------|--------------|----------|
| `Please enter your Groq API Key` | Key not set | Add key in sidebar |
| `Please enter a project idea` | Empty text area | Describe your project |
| `(API 키를 입력하세요)` in model list | Invalid or missing Groq key | Verify key at Groq console |
| `Invalid Token` (Notion) | Wrong or expired token | Regenerate integration secret |
| `No accessible DB found` | Integration not invited | Share database with integration |
| `Cannot read the structure of the selected DB` | No title property | Ensure database has a title column |
| `JSON Parsing Error` | Model returned invalid JSON | Try a different/larger model (e.g., `llama3-70b-8192`) |
| `Failed: <card title>` | Notion API error | Check integration permissions and property limits |
| Agent step shows `Error: ...` | Groq API failure | Check quota, model availability, network |

### Tips

- Use a larger model (e.g., 70B) for more reliable JSON task extraction.
- Keep project descriptions specific — clearer input yields better plans and tasks.
- Notion page creation is limited to 100 content blocks per wiki card; very long outputs may be truncated.

---

## Security Notes

- API keys are held in **Streamlit session state** only and are not written to files by this app.
- Keys are entered via password-masked input fields in the sidebar.
- Do not commit API keys to version control.
- For production deployment, use environment variables or a secrets manager instead of sidebar text inputs.

---

## License

No license file is included in this repository. Contact the repository owner for usage terms.
