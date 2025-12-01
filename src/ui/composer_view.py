import streamlit as st
from langchain_core.messages import HumanMessage
from src.agents.graph import create_graph

# Section configurations
SECTIONS = {
    "Executive Summary": {
        "description": "High-level overview of the company and transfer pricing position",
        "data_sources": ["prior_year", "company_overview"]
    },
    "Company Analysis": {
        "description": "Detailed analysis of company structure and operations",
        "data_sources": ["10k", "web_search", "prior_year"]
    },
    "Functional, Risk, Assets": {
        "description": "FRA analysis with sub-sections",
        "data_sources": ["interview_notes", "prior_year"],
        "sub_sections": ["Functional Analysis", "Risk Analysis", "Assets Analysis", "Complete FRA"]
    },
    "Industry Analysis": {
        "description": "Analysis of industry dynamics and competitive landscape",
        "data_sources": ["competitors", "web_search", "industry_reports", "prior_year"]
    },
    "Economic Analysis": {
        "description": "Transaction-based economic analysis with benchmarking",
        "data_sources": ["transaction_details", "benchmarking", "agreements", "prior_year"]
    }
}

TP_METHODS = [
    "CUP (Comparable Uncontrolled Price)",
    "CPM (Comparable Profits Method)",
    "TNMM (Transactional Net Margin Method)",
    "Profit Split Method",
    "Cost Plus Method",
    "Resale Price Method"
]

def render_composer_view():
    st.header("Document Composer")
    st.markdown("Generate compliant Transfer Pricing documentation with AI assistance.")
    
    # Configuration Section
    st.markdown("### Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        guideline_framework = st.radio(
            "Guideline Framework",
            ["OECD Guidelines", "US Regulations (IRC §482)"],
            help="Select the regulatory framework for drafting"
        )
    
    with col2:
        selected_section = st.selectbox(
            "Section to Draft",
            list(SECTIONS.keys()),
            help=SECTIONS[list(SECTIONS.keys())[0]]["description"]
        )
    
    # Update help text dynamically
    st.caption(f"📋 {SECTIONS[selected_section]['description']}")
    
    st.markdown("---")
    
    # Dynamic Data Source Panel
    st.markdown("### Data Sources")
    
    data_config = {}
    
    # Section-specific inputs
    if selected_section == "Executive Summary":
        render_exec_summary_inputs(data_config)
    
    elif selected_section == "Company Analysis":
        render_company_analysis_inputs(data_config)
    
    elif selected_section == "Functional, Risk, Assets":
        render_fra_inputs(data_config)
    
    elif selected_section == "Industry Analysis":
        render_industry_analysis_inputs(data_config)
    
    elif selected_section == "Economic Analysis":
        render_economic_analysis_inputs(data_config)
    
    st.markdown("---")
    
    # Generate Button
    if st.button("Generate Draft", type="primary"):
        if not validate_inputs(selected_section, data_config):
            st.warning("Please provide required data sources.")
            return
        
        with st.spinner(f"Drafting {selected_section}..."):
            app = create_graph()
            
            initial_state = {
                "messages": [HumanMessage(content=f"Draft {selected_section}")],
                "current_mode": "composer",
                "guideline_framework": guideline_framework,
                "selected_section": selected_section,
                "data_sources": data_config
            }
            
            final_state = app.invoke(initial_state)
            
            draft = final_state.get("draft_content")
            if draft:
                st.markdown("### Generated Draft")
                st.markdown(draft)
                
                # Download button
                st.download_button(
                    label="Download Draft",
                    data=draft,
                    file_name=f"{selected_section.replace(' ', '_')}_draft.md",
                    mime="text/markdown"
                )
            else:
                st.error("Drafting failed.")

def render_exec_summary_inputs(data_config):
    """Executive Summary data sources"""
    col1, col2 = st.columns(2)
    
    with col1:
        prior_year = st.file_uploader(
            "Prior Year Executive Summary (optional)",
            type=["pdf", "docx", "md"],
            key="exec_prior"
        )
        if prior_year:
            data_config["prior_year"] = prior_year
    
    with col2:
        company_overview = st.checkbox(
            "Include Company Overview from Web",
            value=True,
            help="Auto-fetch company overview from authoritative sources"
        )
        data_config["company_overview"] = company_overview

def render_company_analysis_inputs(data_config):
    """Company Analysis data sources"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**10-K Report**")
        uploaded_10k = st.file_uploader(
            "Upload 10-K Report",
            type=["pdf"],
            key="10k_upload",
            help="Upload the company's latest 10-K filing"
        )
        
        if uploaded_10k:
            data_config["10k_file"] = uploaded_10k
    
    with col2:
        st.markdown("**Web Research**")
        web_sources = st.multiselect(
            "Select domains for research",
            ["Company Website", "SEC Filings", "News Sources", "Industry Publications"],
            default=["Company Website", "SEC Filings"]
        )
        data_config["web_sources"] = web_sources
        
        prior_year = st.file_uploader(
            "Prior Year Section (optional)",
            type=["pdf", "docx", "md"],
            key="company_prior"
        )
        if prior_year:
            data_config["prior_year"] = prior_year

def render_fra_inputs(data_config):
    """Functional, Risk, Assets data sources"""
    col1, col2 = st.columns(2)
    
    with col1:
        sub_section = st.radio(
            "Sub-Section",
            SECTIONS["Functional, Risk, Assets"]["sub_sections"],
            help="Select which analysis to draft"
        )
        data_config["sub_section"] = sub_section
        
        interview_notes = st.file_uploader(
            "Interview/Meeting Notes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="interview_notes"
        )
        if interview_notes:
            data_config["interview_notes"] = interview_notes
    
    with col2:
        prior_year = st.file_uploader(
            "Prior Year FRA Section (optional)",
            type=["pdf", "docx", "md"],
            key="fra_prior"
        )
        if prior_year:
            data_config["prior_year"] = prior_year

def render_industry_analysis_inputs(data_config):
    """Industry Analysis data sources"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Competitors**")
        competitors = st.text_area(
            "List competitors (comma-separated)",
            placeholder="Company A, Company B, Company C",
            help="Add competitors to analyze alongside industry trends"
        )
        if competitors:
            data_config["competitors"] = [c.strip() for c in competitors.split(",")]
        
        web_domains = st.multiselect(
            "Web search domains",
            ["Industry Reports", "News Sources", "Market Research", "Trade Publications"],
            default=["Industry Reports", "Market Research"]
        )
        data_config["web_domains"] = web_domains
    
    with col2:
        industry_reports = st.file_uploader(
            "Industry Reports (optional)",
            type=["pdf"],
            accept_multiple_files=True,
            key="industry_reports"
        )
        if industry_reports:
            data_config["industry_reports"] = industry_reports
        
        prior_year = st.file_uploader(
            "Prior Year Section (optional)",
            type=["pdf", "docx", "md"],
            key="industry_prior"
        )
        if prior_year:
            data_config["prior_year"] = prior_year

def render_economic_analysis_inputs(data_config):
    """Economic Analysis data sources"""
    st.markdown("**Transaction Details**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        transaction_name = st.text_input(
            "Transaction Name",
            placeholder="e.g., Sale of Widgets to UK Subsidiary"
        )
        data_config["transaction_name"] = transaction_name
        
        tp_method = st.selectbox(
            "Transfer Pricing Method",
            TP_METHODS
        )
        data_config["tp_method"] = tp_method
    
    with col2:
        benchmarking_set = st.file_uploader(
            "Benchmarking Study/Set",
            type=["xlsx", "csv", "pdf"],
            help="Upload benchmarking analysis results"
        )
        if benchmarking_set:
            data_config["benchmarking_set"] = benchmarking_set
        
        agreements = st.file_uploader(
            "Intercompany Agreements",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload relevant intercompany agreements"
        )
        if agreements:
            data_config["agreements"] = agreements
    
    prior_year = st.file_uploader(
        "Prior Year Economic Analysis (optional)",
        type=["pdf", "docx", "md"],
        key="econ_prior"
    )
    if prior_year:
        data_config["prior_year"] = prior_year

def validate_inputs(section, data_config):
    """Validate that required inputs are provided"""
    if section == "Company Analysis":
        return "10k_file" in data_config
    elif section == "Functional, Risk, Assets":
        return "interview_notes" in data_config
    elif section == "Industry Analysis":
        return "competitors" in data_config or "industry_reports" in data_config
    elif section == "Economic Analysis":
        return "transaction_name" in data_config and "tp_method" in data_config
    return True
