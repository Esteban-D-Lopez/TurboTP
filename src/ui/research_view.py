import streamlit as st
from langchain_core.messages import HumanMessage
from src.agents.graph import create_graph

def render_research_view():
    st.header("Research Center")
    st.markdown("Conduct deep research on Transfer Pricing topics across jurisdictions.")
    
    col1, col2 = st.columns(2)
    with col1:
        jurisdiction = st.selectbox("Jurisdiction", ["US", "OECD", "Italy", "UK", "Germany"])
    with col2:
        reg_area = st.selectbox("Regulatory Area", ["General", "Section 482", "BEPS Action 13", "Intangibles"])
        
    topic = st.text_area("Research Topic", height=100, placeholder="e.g., Penalty for late filing of Local File in Italy")
    
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
                "jurisdiction": jurisdiction
            }
            
            # Run Graph
            final_state = app.invoke(initial_state)
            
            # Display Results
            findings = final_state.get("research_findings")
            if findings:
                st.markdown("### Research Findings")
                st.markdown(findings)
            else:
                st.error("Research failed to produce findings.")
