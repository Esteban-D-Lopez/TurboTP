import streamlit as st
from langchain_core.messages import HumanMessage
from src.agents.graph import create_graph

# Regulatory area mappings by jurisdiction
REGULATORY_AREAS = {
    "US": [
        "IRC Section 482",
        "Treasury Reg §1.482-1: Allocation",
        "Treasury Reg §1.482-2: Loans & Services",
        "Treasury Reg §1.482-3: Tangible Property",
        "Treasury Reg §1.482-4: Intangible Property",
        "Treasury Reg §1.482-5: CPM",
        "Treasury Reg §1.482-6: Profit Split",
        "Treasury Reg §1.482-7: Cost Sharing",
        "Treasury Reg §1.482-8: Examples",
        "Treasury Reg §1.482-9: Services",
        "Treasury Reg §1.6662-6: Penalties",
        "IRS Audit Roadmap",
        "IRS Interquartile Range Paper"
    ],
    "OECD": [
        "Chapter I: Arm's Length Principle",
        "Chapter II: TP Methods",
        "Chapter III: Comparability",
        "Chapter IV: Disputes",
        "Chapter V: Documentation",
        "Chapter VI: Intangibles",
        "Chapter VII: Services",
        "Chapter VIII: CCAs",
        "Chapter IX: Restructurings",
        "BEPS Action 8-10",
        "BEPS Action 13"
    ]
}

def render_research_view():
    st.header("Research Center")
    st.markdown("Conduct deep research on Transfer Pricing topics across jurisdictions.")
    
    # Initialize session state for research
    if "research_active" not in st.session_state:
        st.session_state.research_active = False
    if "research_history" not in st.session_state:
        st.session_state.research_history = []
    
    col1, col2 = st.columns(2)
    with col1:
        jurisdiction = st.selectbox("Jurisdiction", ["US", "OECD"])
    with col2:
        # Dynamic regulatory areas based on jurisdiction
        reg_areas = REGULATORY_AREAS.get(jurisdiction, [])
        reg_area = st.selectbox("Regulatory Area", reg_areas)
        
    topic = st.text_area(
        "Research Topic", 
        height=100, 
        placeholder="e.g., Methods for analyzing intercompany services under the CPM"
    )
    
    if st.button("Start Research", type="primary"):
        if not topic:
            st.warning("Please enter a research topic.")
            return
        
        # Clear previous research
        st.session_state.research_active = False
        st.session_state.research_history = []
        
        # Show streaming research process
        with st.status("🔍 Researching...", expanded=True) as status:
            st.write("Initializing agent...")
            
            # Initialize Graph
            app = create_graph()
            
            # Initial State
            initial_state = {
                "messages": [HumanMessage(content=f"Research: {topic}")],
                "current_mode": "research",
                "research_topic": topic,
                "jurisdiction": jurisdiction,
                "web_sources": st.session_state.get("web_sources", {})
            }
            
            # Stream through execution and show reasoning
            reasoning_steps = []
            final_state = None
            
            try:
                for event in app.stream(initial_state):
                    if isinstance(event, dict):
                        for node_name, node_output in event.items():
                            if node_name != "__end__":
                                step_msg = f"⚙️ **{node_name.title()}** is working..."
                                st.write(step_msg)
                                
                                # Store final state
                                if "research_findings" in node_output:
                                    final_state = node_output
                
                # Update status
                status.update(label="✅ Research Complete!", state="complete", expanded=False)
                
                # Display Results
                if final_state and final_state.get("research_findings"):
                    findings = final_state.get("research_findings")
                    st.session_state.research_active = True
                    st.session_state.research_history.append({
                        "role": "assistant",
                        "content": findings
                    })
                    st.rerun()
                else:
                    st.error("Research failed to produce findings.")
                    
            except Exception as e:
                status.update(label="❌ Research Failed", state="error")
                st.error(f"Error during research: {str(e)}")
    
    # Display research findings
    if st.session_state.research_active and st.session_state.research_history:
        st.markdown("---")
        for message in st.session_state.research_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
        
        # Follow-up questions
        st.markdown("---")
        st.markdown("### Ask Follow-Up Questions")
        
        follow_up = st.chat_input("Ask a follow-up question or request analysis...")
        
        if follow_up:
            # Display user question immediately
            with st.chat_message("user"):
                st.markdown(follow_up)
            
            # Add to history
            st.session_state.research_history.append({
                "role": "user",
                "content": follow_up
            })
            
            # Show agent reasoning in real-time
            with st.chat_message("assistant"):
                reasoning_placeholder = st.empty()
                
                # Build conversation context from history
                from langchain_core.messages import HumanMessage, AIMessage
                conversation_messages = []
                
                for msg in st.session_state.research_history:
                    if msg["role"] == "user":
                        conversation_messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        conversation_messages.append(AIMessage(content=msg["content"]))
                
                # Create state with full conversation context
                app = create_graph()
                follow_up_state = {
                    "messages": conversation_messages,
                    "current_mode": "research",
                    "research_topic": topic,
                    "jurisdiction": jurisdiction,
                    "web_sources": st.session_state.get("web_sources", {})
                }
                
                # Stream the agent's reasoning
                reasoning_steps = []
                final_response = None
                
                try:
                    # Stream through the graph execution
                    for event in app.stream(follow_up_state):
                        # Extract reasoning from events
                        if isinstance(event, dict):
                            for node_name, node_output in event.items():
                                if node_name != "__end__":
                                    # Show which node is executing
                                    reasoning_steps.append(f"🔍 **{node_name.title()}:** Processing...")
                                    reasoning_placeholder.markdown("\n\n".join(reasoning_steps))
                                
                                # If messages were updated, show the latest
                                if "messages" in node_output:
                                    latest_msg = node_output["messages"][-1]
                                    if hasattr(latest_msg, 'content'):
                                        final_response = latest_msg.content
                    
                    # If we got a response, format and display it
                    if final_response:
                        # Clear reasoning steps
                        reasoning_placeholder.empty()
                        
                        # Display final response
                        st.markdown(final_response)
                        
                        # Add to history
                        st.session_state.research_history.append({
                            "role": "assistant",
                            "content": final_response
                        })
                    else:
                        reasoning_placeholder.error("No response received from agent.")
                        
                except Exception as e:
                    reasoning_placeholder.error(f"Error during research: {str(e)}")
                    st.error(f"Details: {str(e)}")

def format_follow_up_response(response: str) -> str:
    """Format follow-up responses cleanly."""
    return f"{response}"
