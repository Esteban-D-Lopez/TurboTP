import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("📊 TurboTP")
        st.markdown("**Enterprise Workspace**")
        st.markdown("---")
        
        # Mode Selection
        mode = st.radio(
            "Select Mode",
            ["Research Center", "Document Composer", "Agent Assistant"],
            index=0
        )
        
        st.markdown("---")
        
        # Web Search Sources (only visible in Research Center)
        if mode == "Research Center":
            st.markdown("### Web Search Sources")
            st.caption("Select authoritative sources for web research")
            
            # Initialize session state for web sources
            if "web_sources" not in st.session_state:
                st.session_state.web_sources = {
                    "IRS": True,
                    "OECD": True,
                    "Deloitte": False,
                    "PwC": False,
                    "EY": False,
                    "KPMG": False,
                    "YouTube": False
                }
            
            # Checkboxes for each source
            st.session_state.web_sources["IRS"] = st.checkbox(
                "IRS Website", 
                value=st.session_state.web_sources["IRS"]
            )
            st.session_state.web_sources["OECD"] = st.checkbox(
                "OECD Website", 
                value=st.session_state.web_sources["OECD"]
            )
            st.session_state.web_sources["Deloitte"] = st.checkbox(
                "Deloitte", 
                value=st.session_state.web_sources["Deloitte"]
            )
            st.session_state.web_sources["PwC"] = st.checkbox(
                "PwC", 
                value=st.session_state.web_sources["PwC"]
            )
            st.session_state.web_sources["EY"] = st.checkbox(
                "EY", 
                value=st.session_state.web_sources["EY"]
            )
            st.session_state.web_sources["KPMG"] = st.checkbox(
                "KPMG", 
                value=st.session_state.web_sources["KPMG"]
            )
            st.session_state.web_sources["YouTube"] = st.checkbox(
                "YouTube Videos", 
                value=st.session_state.web_sources["YouTube"]
            )
            
            st.markdown("---")
        
        # Status
        st.markdown("### Status")
        st.success("✅ Connected")
        st.caption(f"Current Mode: **{mode}**")
    
    return mode
