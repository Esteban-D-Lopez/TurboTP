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
            
        with st.spinner("Agent is researching..."):
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
            
            # Run Graph
            final_state = app.invoke(initial_state)
            
            # Display Results
            findings = final_state.get("research_findings")
            if findings:
                st.session_state.research_active = True
                st.session_state.research_history.append({
                    "role": "assistant",
                    "content": findings
                })
            else:
                st.error("Research failed to produce findings.")
    
    # Display research findings
    if st.session_state.research_active and st.session_state.research_history:
        st.markdown("---")
        for message in st.session_state.research_history:
            with st.container():
                st.markdown(message["content"])
        
        # Follow-up questions
        st.markdown("---")
        st.markdown("### Ask Follow-Up Questions")
        
        follow_up = st.chat_input("Ask a follow-up question or request analysis...")
        
        if follow_up:
            # Add user question to history
            st.session_state.research_history.append({
                "role": "user",
                "content": follow_up
            })
            
            with st.spinner("Analyzing..."):
                app = create_graph()
                
                # Convert history to messages
                messages = []
                for msg in st.session_state.research_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                
                follow_up_state = {
                    "messages": messages,
                    "current_mode": "research",
                    "research_topic": topic,
                    "jurisdiction": jurisdiction
                }
                
                result = app.invoke(follow_up_state)
                response = result["messages"][-1].content
                
                # Format follow-up response
                formatted_response = format_follow_up_response(response)
                
                st.session_state.research_history.append({
                    "role": "assistant",
                    "content": formatted_response
                })
                
                st.rerun()

def format_follow_up_response(response: str) -> str:
    """Format follow-up responses cleanly."""
    return f"**Analysis:**\n\n{response}"
