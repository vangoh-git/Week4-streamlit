import os
import asyncio
import streamlit as st
from agents import Agent, FileSearchTool, Runner, WebSearchTool

##from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Ninja Generator",
    page_icon="🤖",
    layout="centered"
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        value=os.environ.get("OPENAI_API_KEY", ""),
        help="Your key is never stored — it lives only in this session."
    )
    st.divider()
    st.markdown("### 💡 Example Goals")
    examples = [
        "Build a customer support AI agent",
        "Create an AI agent that summarizes emails",
        "Build a RAG-based document Q&A agent",
        "Create an AI coding assistant agent",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.selected_goal = example
    st.divider()
    st.caption("Powered by OpenAI Agents SDK + Streamlit")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.title("🤖 AI Ninja Task Generator")
st.write("Describe your AI Ninja goal and get a structured, actionable task plan.")

# Pre-fill input if an example was clicked
default_goal = st.session_state.get("selected_goal", "")

user_goal = st.text_area(
    "What AI Agent do you want to build?",
    value=default_goal,
    height=100,
    placeholder="e.g. Build a Ninja customer support AI agent that handles refund requests..."
)

generate_btn = st.button("🚀 Generate Task Plan", use_container_width=True, type="primary")

# ── Agent logic ────────────────────────────────────────────────────────────────
async def generate_tasks(goal, key):
    os.environ["OPENAI_API_KEY"] = key
    task_generator = Agent(
        name="Task Generator",
        instructions="""You help users break down their specific LLM powered AI Agent goal into small, achievable tasks.
        For any goal, analyze it and create a structured plan with specific actionable steps.
        Each task should be concrete, time-bound when possible, and manageable.
        Organize tasks in a logical sequence with dependencies clearly marked.
        Never answer anything unrelated to AI Agents.""",
    )
    result = await Runner.run(task_generator, goal)
    return result.final_output

# ── On button click ────────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar.")
        st.stop()
    if not user_goal.strip():
        st.warning("⚠️ Please enter a goal before generating.")
        st.stop()

    with st.spinner("🧠 Generating your task plan..."):
        try:
            result = asyncio.run(generate_tasks(user_goal, api_key))

            st.success("✅ Task plan generated!")
            st.divider()

            # Display goal
            st.markdown("### 🎯 Your Goal")
            st.info(user_goal)

            # Display result
            st.markdown("### 📋 Your Task Plan")
            st.markdown(result)

            # Download button
            st.divider()
            st.download_button(
                label="⬇️ Download Task Plan",
                data=f"GOAL:\n{user_goal}\n\nTASK PLAN:\n{result}",
                file_name="task_plan.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.caption("Make sure your API key is valid and the `openai-agents` package is installed.")
