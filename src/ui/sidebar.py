import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("TurboTP")
        st.markdown("*AI-Powered Transfer Pricing Assistant*")
        
        st.markdown("---")
        
        # Mode Selection
        mode = st.radio(
            "Mode",
            ["Research Center", "Document Composer", "Agent Assistant"],
            key="mode_selection"
        )
        
        # Store mode in session state
        if mode == "Research Center":
            st.session_state.current_mode = "research"
        elif mode == "Document Composer":
            st.session_state.current_mode = "composer"
        else:
            st.session_state.current_mode = "chat"
        
        st.markdown("---")
        
        # Web source configuration for Research Center
        if mode == "Research Center":
            st.markdown("### Web Sources")
            
            # Initialize web_sources in session state
            if "web_sources" not in st.session_state:
                st.session_state.web_sources = {
                    "IRS": True,
                    "OECD": True,
                    "YouTube": False,
                    "custom_domains": []
                }
            
            # Predefined sources
            st.session_state.web_sources["IRS"] = st.checkbox(
                "IRS (irs.gov)",
                value=st.session_state.web_sources.get("IRS", True)
            )
            st.session_state.web_sources["OECD"] = st.checkbox(
                "OECD (oecd.org)",
                value=st.session_state.web_sources.get("OECD", True)
            )
            
            # Big 4
            st.markdown("**Big 4:**")
            st.session_state.web_sources["Deloitte"] = st.checkbox(
                "Deloitte (deloitte.com)",
                value=st.session_state.web_sources.get("Deloitte", False)
            )
            st.session_state.web_sources["PwC"] = st.checkbox(
                "PwC (pwc.com)",
                value=st.session_state.web_sources.get("PwC", False)
            )
            st.session_state.web_sources["EY"] = st.checkbox(
                "EY (ey.com)",
                value=st.session_state.web_sources.get("EY", False)
            )
            st.session_state.web_sources["KPMG"] = st.checkbox(
                "KPMG (kpmg.com)",
                value=st.session_state.web_sources.get("KPMG", False)
            )
            
            # YouTube
            st.session_state.web_sources["YouTube"] = st.checkbox(
                "YouTube",
                value=st.session_state.web_sources.get("YouTube", False)
            )
            
            # Custom domains
            st.markdown("**Custom Domains:**")
            custom_input = st.text_area(
                "Additional domains (one per line)",
                placeholder="www.example.com\nwww.another-site.com",
                help="Enter custom domains to include in web search",
                key="custom_domains_input",
                height=80
            )
            
            if custom_input:
                custom_domains = [d.strip() for d in custom_input.split('\n') if d.strip()]
                st.session_state.web_sources["custom_domains"] = custom_domains
            else:
                st.session_state.web_sources["custom_domains"] = []
        
        st.markdown("---")
        st.caption("Powered by LangGraph & Gemini")
        
        return st.session_state.current_mode
