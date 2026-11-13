# Multi-Agent Customer Support System (CrewAI + Streamlit)

A three-agent sequential customer support system built with **CrewAI** and **Streamlit**. When a user submits a support query, three specialized agents collaborate in sequence to generate a direct knowledge response, a live web-searched response, and a persistent log file (`answers.txt`) while displaying both answers side-by-side in the UI.

---

## Architecture & Sequential Process Flow

```text
┌───────────────────┐
│   User Query UI   │  (Streamlit Input)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  1. Assistant     │  Answers directly from internal LLM knowledge (tools=[])
└─────────┬─────────┘
          │  context=[direct_answer_task]
          ▼
┌───────────────────┐
│ 2. Web Search     │  Searches live web via SerperDevTool & synthesizes answer
│    Assistant      │
└─────────┬─────────┘
          │  context=[direct_answer_task, web_answer_task]
          ▼
┌───────────────────┐
│  3. Entry Agent   │  Logs query + both answers to answers.txt (@tool) & returns both
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  Streamlit UI     │  Displays Answer 1, Answer 2, and answers.txt preview
└───────────────────┘
```

### Agent Roles & Responsibilities

| Order | Agent Role | Tools | Responsibility |
| :--- | :--- | :--- | :--- |
| **1** | **Assistant** | None (`tools=[]`) | Provides an immediate, direct answer using its built-in knowledge. |
| **2** | **Web Search Assistant** | `SerperDevTool` | Searches the live internet for up-to-date facts, guides, or troubleshooting steps. |
| **3** | **Entry Agent** | `save_answers_to_txt` (`@tool`) | Receives both upstream outputs via `context=[...]`, writes the query and both answers to `answers.txt`, and returns both answers to the UI. |

---

## Tech Stack & Requirements

* **Python:** 3.10+
* **CrewAI (`crewai`, `crewai-tools`):** Multi-agent orchestration (`Process.sequential`), explicit context handoffs, custom `@tool` integration, and `SerperDevTool` web search.
* **Streamlit (`streamlit`):** Interactive web interface with real-time execution status and dual-column answer comparison.
* **Environment Management (`python-dotenv`):** Loads `OPENAI_API_KEY`, `SERPER_API_KEY`, and `MODEL` securely from `.env`.

---

## Step-by-Step Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/cvijayvinoth/crewai-streamlit-customer-support.git
cd crewai-streamlit-customer-support
```

### 2. Create & Activate a Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```
```env
OPENAI_API_KEY=your-openai-api-key
SERPER_API_KEY=your-serper-api-key
MODEL=openai/gpt-4o-mini
```

### 5. Run the Streamlit Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## How It Works (Example Run)

1. Enter a query such as: `How do I reset my password?`
2. Click **Ask Support Crew**.
3. **Assistant** generates a standard step-by-step password reset response.
4. **Web Search Assistant** queries live search results and provides an updated, web-grounded response.
5. **Entry Agent** appends the timestamped query and both answers to `answers.txt` and displays both responses side-by-side in the Streamlit interface.

<img width="1530" height="518" alt="image" src="https://github.com/user-attachments/assets/a9fe6f09-4a7a-438c-b590-f1e77e73ddc2" />

