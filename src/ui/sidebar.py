import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("TurboTP")
        st.markdown("### Enterprise Workspace")
        
        mode = st.radio(
            "Select Mode",
            ["Research Center", "Document Composer", "Agent Assistant"],
            index=0,
            key="app_mode"
        )
        
        st.markdown("---")
        st.markdown("### Status")
        st.success("System Online")
        st.info("Model: Gemini 2.5 Flash")
        
        return mode
