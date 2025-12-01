import streamlit as st
from dotenv import load_dotenv
from src.ui.styles import inject_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.research_view import render_research_view
from src.ui.composer_view import render_composer_view
from src.ui.assistant_view import render_assistant_view

# Load Environment Variables
load_dotenv()

# Optional Observability Setup (Phoenix)
try:
    from src.utils.phoenix_tracer import setup_phoenix
    setup_phoenix()
    print("✅ Phoenix tracing enabled")
except Exception as e:
    print(f"⚠️ Phoenix tracing disabled: {e}")

# Page Configuration
st.set_page_config(
    page_title="TurboTP - Enterprise Workspace",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Inject CSS
    inject_custom_css()
    
    # Render Sidebar & Get Mode
    mode = render_sidebar()
    
    # Render Main Content
    if mode == "research":
        render_research_view()
    elif mode == "composer":
        render_composer_view()
    elif mode == "chat":
        render_assistant_view()

if __name__ == "__main__":
    main()
