import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Main Container */
        .stApp {
            background-color: #f8fafc;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #0f172a;
            font-family: 'Inter', sans-serif;
        }
        
        /* Cards */
        .stCard {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #2563eb;
            color: white;
            border-radius: 0.375rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border: none;
        }
        .stButton button:hover {
            background-color: #1d4ed8;
        }
        
        /* Inputs */
        .stTextInput input, .stTextArea textarea {
            border-radius: 0.375rem;
            border: 1px solid #cbd5e1;
        }
        </style>
    """, unsafe_allow_html=True)
