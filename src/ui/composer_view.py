import streamlit as st
from langchain_core.messages import HumanMessage
from src.agents.graph import create_graph

def render_composer_view():
    st.header("Document Composer")
    st.markdown("Generate compliant Transfer Pricing documentation.")
    
    uploaded_file = st.file_uploader("Upload Financial Data (CSV/Excel)", type=["csv", "xlsx"])
    
    doc_type = st.selectbox("Document Type", ["Local File - Functional Analysis", "Local File - Economic Analysis", "Master File"])
    
    if st.button("Generate Draft", type="primary"):
        if not uploaded_file:
            st.warning("Please upload a dataset first.")
            return
            
        with st.spinner("Agent is drafting..."):
            # Initialize Graph
            app = create_graph()
            
            # Initial State
            initial_state = {
                "messages": [HumanMessage(content=f"Draft {doc_type}")],
                "current_mode": "composer",
                "document_type": doc_type,
                # In a real app, we'd parse the file content here
            }
            
            # Run Graph
            final_state = app.invoke(initial_state)
            
            # Display Results
            draft = final_state.get("draft_content")
            if draft:
                st.markdown("### Generated Draft")
                st.text_area("Editor", value=draft, height=400)
            else:
                st.error("Drafting failed.")
