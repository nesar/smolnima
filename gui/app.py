#!/usr/bin/env python3
"""Enhanced Streamlit wrapper for smolnima with agent activity panel."""

import streamlit as st
import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import io

# Add parent directory to path for imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from config import Config
from gui.streamlit_agent import create_streamlit_agent
from gui.streamlit_logger import StreamlitAgentLogger, display_agent_logs
from experiment_tracker import ExperimentTracker

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

if "experiment_tracker" not in st.session_state:
    st.session_state.experiment_tracker = ExperimentTracker()

if "save_experiments" not in st.session_state:
    st.session_state.save_experiments = True

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
        [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp"
        ],
        help="Select Gemini model (2.5 models recommended for 2025)"
    )

    st.subheader("Settings")
    max_steps = st.number_input("Max Steps", 5, 20, 10)
    temperature = st.number_input("Temperature", 0.0, 1.0, 0.3, 0.1)
    pdfs_dir = st.text_input("PDFs Directory", "./pdfs")

    st.session_state.save_experiments = st.checkbox(
        "Save Experiments",
        value=st.session_state.save_experiments,
        help="Save code, plots, and outputs to experiments/ directory"
    )

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
        "Calculate Lorentz factor for v=0.1c, 0.2c, 0.4c, 0.5c. Show them in a scatter plot.",
        "Plot the parton distribution functions for deep inelastic scattering process, inclusive deep inelastic scattering and semi-inclusive deep inelastic scattering processes.",
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

                    # Start experiment tracking if enabled
                    if st.session_state.save_experiments:
                        exp_dir = st.session_state.experiment_tracker.start_experiment(prompt[:50])
                        st.session_state.logger.info(f"Experiment started: {exp_dir.name}", "system")

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

                    # Save experiment artifacts if enabled
                    if st.session_state.save_experiments:
                        tracker = st.session_state.experiment_tracker
                        exp_path = tracker.get_experiment_path()

                        # Save query and response
                        tracker.save_output(f"Query: {prompt}\n\nResponse: {response}", "query_and_response.txt")

                        # Save executed code blocks
                        if st.session_state.executed_code:
                            tracker.save_codes(st.session_state.executed_code)

                        # Save plots
                        if plot_key in st.session_state.plots:
                            tracker.save_plots(st.session_state.plots[plot_key])

                        # Save metadata
                        tracker.save_metadata("query", prompt)
                        tracker.save_metadata("response", response)
                        tracker.save_metadata("num_code_blocks", len(st.session_state.executed_code))
                        tracker.save_metadata("num_plots", len(st.session_state.plots.get(plot_key, [])))

                        tracker.finish_experiment()
                        if exp_path:
                            st.session_state.logger.success(f"Artifacts saved to experiments/{exp_path.name}", "system")

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

        **Experiment Tracking:**
        - Enable "Save Experiments" in settings to save all artifacts
        - Each run creates a timestamped folder in experiments/
        - Saves code, plots, outputs, and metadata for reproducibility
        """)
