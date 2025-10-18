#!/usr/bin/env python3
"""Enhanced Streamlit wrapper for smolnima with agent activity panel."""

import streamlit as st
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import io

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import Config
from streamlit_agent import create_streamlit_agent
from streamlit_logger import StreamlitAgentLogger, display_agent_logs
st.set_page_config(
    page_title="smolnima - Dr. NIMA",
    page_icon="⚛️",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

if "logger" not in st.session_state:
    st.session_state.logger = StreamlitAgentLogger()

if "plots" not in st.session_state:
    st.session_state.plots = {}

if "code_blocks" not in st.session_state:
    st.session_state.code_blocks = {}

if "executed_code" not in st.session_state:
    st.session_state.executed_code = []

if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = {}

if "agent_output" not in st.session_state:
    st.session_state.agent_output = []

# Sidebar
with st.sidebar:
    st.title("⚛️ smolnima")
    st.markdown("**Nuclear Imaging with Multi-Agents**")
    st.markdown("*Powered by smolagents*")

    st.divider()

    api_key = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Enter your Google API key or set GOOGLE_API_KEY env var"
    )

    model_name = st.selectbox(
        "Model",
        ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"],
        help="Select Gemini model"
    )

    st.subheader("Settings")
    max_steps = st.number_input("Max Steps", 5, 20, 10)
    temperature = st.number_input("Temperature", 0.0, 1.0, 0.3, 0.1)
    pdfs_dir = st.text_input("PDFs Directory", "./pdfs")

    if st.button("🚀 Initialize Agent", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter API key")
        else:
            try:
                with st.spinner("Initializing agent..."):
                    config = Config(
                        api_key=api_key,
                        model_name=model_name,
                        pdfs_dir=pdfs_dir,
                        max_steps=max_steps,
                        temperature=temperature,
                        verbose=True
                    )
                    st.session_state.agent = create_streamlit_agent(config)
                    st.session_state.logger.clear()
                    st.session_state.logger.success("Agent initialized successfully!", "system")
                st.success("✅ Agent ready!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.logger.error(f"Initialization failed: {e}", "system")

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.plots = {}
        st.session_state.code_blocks = {}
        st.session_state.executed_code = []
        st.session_state.agent_outputs = {}
        st.session_state.agent_output = []
        st.session_state.logger.clear()
        st.rerun()

    st.divider()
    st.subheader("📚 Example Queries")
    examples = [
        "What is the mass of a proton in MeV?",
        "Calculate Lorentz factor for v=0.9c",
        "Generate 1000 physics events",
        "What are the properties of a muon?",
        "Visualize quark distributions",
        "Calculate binding energy of Carbon-12",
    ]

    for example in examples:
        if st.button(example, key=f"ex_{hash(example)}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": example})
            st.rerun()

    st.divider()
    if st.session_state.agent:
        st.success("🟢 Agent Active")
    else:
        st.warning("🟡 Agent Not Initialized")

# Main layout: Chat on left, Activity on right
col_chat, col_activity = st.columns([2, 1])

with col_chat:
    st.title("⚛️ Dr. NIMA")
    st.markdown("Ask questions about particle and nuclear physics!")
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display agent verbose output (Thoughts, Code, Observations, Execution logs)
            output_key = f"msg_{msg_idx}"
            if output_key in st.session_state.agent_outputs:
                with st.expander("🔍 Agent Process (Thoughts & Execution)", expanded=False):
                    sections = st.session_state.agent_outputs[output_key]
                    for section in sections:
                        if section['type'] == 'thought':
                            st.markdown("**💭 Thought:**")
                            st.info(' '.join(section['content']))
                        elif section['type'] == 'code':
                            st.markdown("**📝 Code:**")
                            code_text = '\n'.join(section['content'])
                            st.code(code_text, language='python')
                        elif section['type'] == 'observation':
                            st.markdown("**👁️ Observation:**")
                            st.success(' '.join(section['content']))
                        elif section['type'] == 'execution':
                            st.markdown("**⚙️ Execution Logs:**")
                            st.text('\n'.join(section['content']))
                        elif section['type'] == 'final':
                            st.markdown("**✅ Final Answer:**")
                            st.success(' '.join(section['content']))

            # Display executed code if any
            code_key = f"msg_{msg_idx}"
            if code_key in st.session_state.code_blocks:
                with st.expander("📝 View Executed Code", expanded=False):
                    for code_idx, code in enumerate(st.session_state.code_blocks[code_key]):
                        st.code(code, language="python")

            # Display plots if any
            plot_key = f"msg_{msg_idx}"
            if plot_key in st.session_state.plots:
                for plot_idx, plot_data in enumerate(st.session_state.plots[plot_key]):
                    st.image(plot_data, width="stretch")

    # Check for unprocessed user message from example button
    prompt = None
    needs_processing = False

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        prompt = st.session_state.messages[-1]["content"]
        needs_processing = True
    if chat_prompt := st.chat_input("Ask about particle or nuclear physics..."):
        if st.session_state.agent is None:
            st.error("❌ Please initialize the agent in the sidebar first!")
        else:
            prompt = chat_prompt
            needs_processing = True
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
    if needs_processing and prompt and st.session_state.agent:
        msg_idx = len(st.session_state.messages) - 1

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    st.session_state.logger.info(f"Processing query: {prompt[:50]}...", "system")
                    plt.close('all')

                    # Clear data from previous run
                    st.session_state.executed_code = []
                    st.session_state.agent_output = []

                    # Run the agent
                    response = st.session_state.agent.run(prompt)
                    st.markdown(response)

                    # Store agent verbose output
                    output_key = f"msg_{msg_idx + 1}"
                    if st.session_state.agent_output:
                        # Flatten all sections from multiple runs
                        all_sections = []
                        for output in st.session_state.agent_output:
                            if isinstance(output, list):
                                all_sections.extend(output)

                        st.session_state.agent_outputs[output_key] = all_sections

                        # Display agent process with nice formatting
                        with st.expander("🔍 Agent Process (Thoughts & Execution)", expanded=True):
                            for section in all_sections:
                                if section['type'] == 'thought':
                                    st.markdown("**💭 Thought:**")
                                    st.info(' '.join(section['content']))
                                elif section['type'] == 'code':
                                    st.markdown("**📝 Code:**")
                                    code_text = '\n'.join(section['content'])
                                    st.code(code_text, language='python')
                                elif section['type'] == 'observation':
                                    st.markdown("**👁️ Observation:**")
                                    st.success(' '.join(section['content']))
                                elif section['type'] == 'execution':
                                    st.markdown("**⚙️ Execution Logs:**")
                                    st.text('\n'.join(section['content']))
                                elif section['type'] == 'final':
                                    st.markdown("**✅ Final Answer:**")
                                    st.success(' '.join(section['content']))

                    # Store executed code blocks
                    code_key = f"msg_{msg_idx + 1}"
                    if st.session_state.executed_code:
                        st.session_state.code_blocks[code_key] = st.session_state.executed_code.copy()
                        st.session_state.logger.success(f"Executed {len(st.session_state.executed_code)} code block(s)", "agent")

                        # Display executed code
                        with st.expander("📝 View Executed Code", expanded=False):
                            for code_idx, code in enumerate(st.session_state.executed_code):
                                st.code(code, language="python")

                    # Capture and display plots
                    plot_key = f"msg_{msg_idx + 1}"
                    if plt.get_fignums():
                        st.session_state.logger.success("Generated visualization(s)", "agent")
                        plots = []
                        for fig_num in plt.get_fignums():
                            fig = plt.figure(fig_num)
                            buf = io.BytesIO()
                            fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
                            buf.seek(0)
                            plots.append(buf.getvalue())
                            st.image(buf.getvalue(), width="stretch")

                        st.session_state.plots[plot_key] = plots
                        plt.close('all')

                    st.session_state.logger.success("Query completed successfully", "system")
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Error: {error_msg}")
                    st.session_state.logger.error(f"Error: {error_msg}", "system")

                    if "rate" in error_msg.lower() or "quota" in error_msg.lower():
                        st.warning("⚠️ Rate limit reached. Please wait and try again.")
                        st.info("💡 Tip: Use a less complex query or wait a minute between requests.")

                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {error_msg}"})
    elif needs_processing and not st.session_state.agent:
        st.error("❌ Please initialize the agent in the sidebar first!")

with col_activity:
    st.subheader("🔍 Agent Activity")

    if st.session_state.agent:
        st.metric("Messages", len(st.session_state.messages) // 2)
        st.metric("Active Logs", len(st.session_state.logger.get_logs()))

    st.divider()

    with st.container(height=600):
        display_agent_logs(st.session_state.logger)

    if st.button("Clear Activity Log", key="clear_activity"):
        st.session_state.logger.clear()
        st.rerun()

if st.session_state.agent is None:
    st.info("👈 Configure settings and click '🚀 Initialize Agent' in the sidebar to start")
else:
    with st.expander("💡 Tips for Better Results"):
        st.markdown("""
        **Avoiding Rate Limits:**
        - Break complex queries into smaller steps
        - Wait 1-2 minutes between heavy computations

        **For Plots:**
        - Specify plot requirements clearly
        - Plots appear automatically below responses

        **Agent Activity:**
        - Watch the right panel for step-by-step progress
        - Green checkmarks indicate successful steps
        """)
