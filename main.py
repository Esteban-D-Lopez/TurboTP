import streamlit as st
from dotenv import load_dotenv
from src.utils.phoenix_tracer import setup_phoenix
from src.ui.styles import inject_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.research_view import render_research_view
from src.ui.composer_view import render_composer_view
from src.ui.assistant_view import render_assistant_view

# Load Environment Variables
load_dotenv()

# Setup Observability
setup_phoenix()

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
    if mode == "Research Center":
        render_research_view()
    elif mode == "Document Composer":
        render_composer_view()
    elif mode == "Agent Assistant":
        render_assistant_view()

if __name__ == "__main__":
    main()
