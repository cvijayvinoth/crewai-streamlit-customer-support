import os
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from crewai_tools import SerperDevTool

# Load environment variables from .env if present (never hard-code keys)
load_dotenv()

# Ensure default model is set if not specified in environment
os.environ.setdefault("MODEL", "openai/gpt-4o-mini")


# Custom file-writing tool so Entry Agent reliably writes/appends to answers.txt
@tool("Save Support Log to TXT")
def save_answers_to_txt(query: str, assistant_answer: str, web_search_answer: str) -> str:
    """Writes the user query, Assistant answer, and Web Search Assistant answer into answers.txt."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"{'=' * 60}\n"
        f"Timestamp: {timestamp}\n"
        f"Query: {query}\n"
        f"{'-' * 60}\n"
        f"[1] Assistant Answer (Direct Knowledge):\n{assistant_answer}\n\n"
        f"[2] Web Search Assistant Answer (Live Web):\n{web_search_answer}\n"
        f"{'=' * 60}\n\n"
    )
    with open("answers.txt", "a", encoding="utf-8") as f:
        f.write(entry)
    return "Successfully saved query and both answers to answers.txt."


def run_support_crew(user_query: str):
    """Builds and runs the 3-agent sequential support crew."""
    search_tool = SerperDevTool()

    # 1. Assistant — answers directly from internal knowledge
    assistant = Agent(
        role="Assistant",
        goal="Answer the user's support query accurately and clearly using your own knowledge.",
        backstory=(
            "You are a helpful, knowledgeable frontline customer support specialist. "
            "You provide clear, direct, and well-structured answers immediately without external tools."
        ),
        tools=[],
        verbose=True,
    )

    # 2. Web Search Assistant — searches the web and answers from live results
    web_search_assistant = Agent(
        role="Web Search Assistant",
        goal="Search the web for the user's query and provide an accurate, up-to-date answer based on live search results.",
        backstory=(
            "You are a technical support researcher who verifies facts and retrieves the latest "
            "documentation, troubleshooting steps, or news from the web to answer user queries."
        ),
        tools=[search_tool],
        inject_date=True,
        verbose=True,
    )

    # 3. Entry Agent — writes query + both answers to answers.txt and returns both answers
    entry_agent = Agent(
        role="Entry Agent",
        goal="Save the user's query, the Assistant's answer, and the Web Search Assistant's answer to answers.txt, then return both answers.",
        backstory=(
            "You are a meticulous support operations coordinator. You log every support interaction "
            "into answers.txt using your file-saving tool and present both answers clearly to the user."
        ),
        tools=[save_answers_to_txt],
        verbose=True,
    )

    # Sequential Tasks
    direct_answer_task = Task(
        description="Answer the following customer query directly using your own knowledge:\n\nQuery: {query}",
        expected_output="A clear, concise, and helpful direct answer to the user's query.",
        agent=assistant,
    )

    web_answer_task = Task(
        description=(
            "Search the web for the following customer query and generate a comprehensive, "
            "up-to-date answer based on the search results:\n\nQuery: {query}"
        ),
        expected_output="A clear, factual answer grounded in live web search results, with key steps or sources.",
        agent=web_search_assistant,
    )

    entry_logging_task = Task(
        description=(
            "You have received the direct answer from the Assistant and the web-researched answer "
            "from the Web Search Assistant for the query: '{query}'.\n"
            "1. Call 'Save Support Log to TXT' with the exact query, the Assistant's answer, and the Web Search Assistant's answer.\n"
            "2. Return both answers clearly formatted so the user can review both side by side."
        ),
        expected_output=(
            "Both the Assistant's direct answer and the Web Search Assistant's answer clearly presented, "
            "confirming that the entry has been saved to answers.txt."
        ),
        agent=entry_agent,
        context=[direct_answer_task, web_answer_task],
    )

    support_crew = Crew(
        agents=[assistant, web_search_assistant, entry_agent],
        tasks=[direct_answer_task, web_answer_task, entry_logging_task],
        process=Process.sequential,
        verbose=True,
    )

    return support_crew.kickoff(inputs={"query": user_query})


# --- Streamlit User Interface ---
st.set_page_config(page_title="Multi-Agent Customer Support", page_icon="🎧", layout="wide")

st.title("Multi-Agent Customer Support Crew")
st.caption("Sequential CrewAI Pipeline: **Assistant** → **Web Search Assistant** → **Entry Agent**")

# Sidebar status check for API keys
with st.sidebar:
    st.header("Environment Status")
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    serper_ok = bool(os.getenv("SERPER_API_KEY"))
    st.write(f"OPENAI_API_KEY: {'✅ Loaded' if openai_ok else '❌ Missing'}")
    st.write(f"SERPER_API_KEY: {'✅ Loaded' if serper_ok else '❌ Missing'}")
    st.divider()
    st.markdown("**Workflow Order:**")
    st.markdown("1. **Assistant** (Direct knowledge)\n2. **Web Search Assistant** (Live web search)\n3. **Entry Agent** (Logs to `answers.txt` & returns both)")

query = st.text_input(
    "Enter your support query or task:",
    placeholder="e.g., How do I reset my password?",
)

if st.button("Ask Support Crew", type="primary"):
    if not query.strip():
        st.warning("Please enter a query before running the crew.")
    elif not os.getenv("OPENAI_API_KEY") or not os.getenv("SERPER_API_KEY"):
        st.error("Missing API keys. Please set OPENAI_API_KEY and SERPER_API_KEY in your environment.")
    else:
        with st.status("Running 3-agent sequential support crew...", expanded=True) as status:
            st.write("Step 1: **Assistant** is generating a direct answer...")
            st.write("Step 2: **Web Search Assistant** is searching the web...")
            st.write("Step 3: **Entry Agent** is saving everything to `answers.txt`...")
            crew_output = run_support_crew(query.strip())
            status.update(label="All 3 agents completed!", state="complete", expanded=False)

        # Extract individual outputs from each sequential task
        assistant_response = crew_output.tasks_output[0].raw
        web_search_response = crew_output.tasks_output[1].raw
        entry_summary = crew_output.tasks_output[2].raw

        st.success("Query and both answers have been saved to `answers.txt`.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Assistant (Direct Knowledge)")
            st.markdown(assistant_response)

        with col2:
            st.subheader("2. Web Search Assistant (Live Web)")
            st.markdown(web_search_response)

        with st.expander("3. Entry Agent Output & Saved File Preview (`answers.txt`)"):
            st.markdown(entry_summary)
            if os.path.exists("answers.txt"):
                with open("answers.txt", "r", encoding="utf-8") as f:
                    st.text(f.read())
