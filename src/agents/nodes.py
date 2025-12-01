from typing import Dict, List, Optional
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .tools import search_regulations, web_search
from langgraph.prebuilt import create_react_agent

# Import file processors
from src.utils.file_processor import (
    process_uploaded_file,
    process_multiple_files,
    process_interview_notes,
    parse_excel_benchmarking,
    parse_csv_benchmarking
)


# Model Configuration
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def get_llm():
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)

# --- Supervisor Node ---
def supervisor_node(state: AgentState):
    """
    Routes the workflow based on the current mode and state.
    """
    mode = state.get("current_mode")
    
    if mode == "research":
        # If we have findings, we are done with research
        if state.get("research_findings"):
            return {"next": "__end__"}
        return {"next": "researcher"}
    
    elif mode == "composer":
        # If we have a draft, we are done
        if state.get("draft_content"):
            return {"next": "__end__"}
        return {"next": "drafter"}
        
    elif mode == "chat":
        return {"next": "assistant"}
        
    return {"next": "__end__"}

from langgraph.prebuilt import create_react_agent

# --- Researcher Node ---
def research_node(state: AgentState):
    llm = get_llm()
    topic = state.get("research_topic")
    jurisdiction = state.get("jurisdiction", "General")
    web_sources = state.get("web_sources", {})
    
    system_message = (
        "You are an elite Transfer Pricing Senior Consultant with deep expertise in IRC 482, OECD Guidelines, and international tax regulations. "
        "Your research should be authoritative, well-cited, and actionable.\n\n"
        "When presenting findings:\n"
        "1. Start with a brief executive summary\n"
        "2. Organize findings under clear headings\n"
        "3. Always cite sources in brackets like [IRC §482] or [OECD Guidelines Ch. II]\n"
        "4. Use bullet points for key takeaways\n"
        "5. Be concise but comprehensive"
    )
    
    prompt = (
        f"**Research Request**\n"
        f"Topic: {topic}\n"
        f"Jurisdiction: {jurisdiction}\n\n"
        f"Conduct thorough research using the regulatory knowledge base and provide structured findings."
    )
    
    # Build tool list based on enabled web sources
    from .tools import search_regulations, web_search, youtube_search
    tools = [search_regulations]
    
    # Add web search if any domains are selected
    if any(web_sources.get(source, False) for source in ["IRS", "OECD", "Deloitte", "PwC", "EY", "KPMG"]):
        tools.append(web_search)
    
    # Add YouTube search if enabled
    if web_sources.get("YouTube", False):
        tools.append(youtube_search)
    
    # Create the React Agent (Compiled Graph)
    agent_app = create_react_agent(llm, tools, prompt=system_message)
    
    # Invoke the agent
    result = agent_app.invoke({"messages": [HumanMessage(content=prompt)]})
    
    # Extract the final response
    raw_findings = result["messages"][-1].content
    
    # Format the findings for clean display
    formatted_findings = format_research_output(raw_findings, topic, jurisdiction)
    
    return {
        "research_findings": formatted_findings,
        "messages": [HumanMessage(content=formatted_findings)]
    }

def format_research_output(raw_output, topic: str, jurisdiction: str, sources_used: list = None) -> str:
    """
    Clean and format the raw agent output for user-friendly display.
    Extracts clean content and removes metadata/artifacts.
    """
    import re
    from langchain_core.messages import BaseMessage
    
    # Extract actual text content from various message types
    if isinstance(raw_output, BaseMessage):
        # It's a LangChain message object
        clean_output = raw_output.content
    elif isinstance(raw_output, list):
        # If it's a list, extract content from each item
        content_parts = []
        for item in raw_output:
            if isinstance(item, BaseMessage):
                content_parts.append(str(item.content))
            elif isinstance(item, dict):
                # Extract text from dict, avoiding metadata
                if 'text' in item:
                    content_parts.append(str(item['text']))
                elif 'content' in item:
                    content_parts.append(str(item['content']))
            else:
                content_parts.append(str(item))
        clean_output = "\n".join(content_parts)
    elif isinstance(raw_output, dict):
        # If it's a dict, extract the content field
        if 'text' in raw_output:
            clean_output = str(raw_output['text'])
        elif 'content' in raw_output:
            clean_output = str(raw_output['content'])
        else:
            # Filter out metadata keys like 'extras', 'signature', etc.
            filtered_content = []
            for key, value in raw_output.items():
                if key not in ['extras', 'signature', 'metadata', 'additional_kwargs', 'response_metadata']:
                    filtered_content.append(f"{key}: {value}")
            clean_output = "\n".join(filtered_content)
    else:
        # Assume it's already a string
        clean_output = str(raw_output)
    
    # Remove tool call patterns and artifacts
    clean_output = re.sub(r'Action:.*?\n', '', clean_output, flags=re.IGNORECASE)
    clean_output = re.sub(r'Observation:.*?\n', '', clean_output, flags=re.IGNORECASE)
    clean_output = re.sub(r'Thought:.*?\n', '', clean_output, flags=re.IGNORECASE)
    clean_output = re.sub(r'Final Answer:\s*', '', clean_output, flags=re.IGNORECASE)
    
    # Remove any remaining dict/list artifacts
    clean_output = re.sub(r"'extras':\s*\{[^}]*\}", '', clean_output)
    clean_output = re.sub(r"'signature':\s*'[^']*'", '', clean_output)
    
    # Clean up excessive whitespace
    clean_output = re.sub(r'\n{3,}', '\n\n', clean_output)
    clean_output = clean_output.strip()
    
    # Format sources string
    if sources_used:
        sources_str = ", ".join(sources_used)
    else:
        sources_str = "Transfer Pricing regulatory knowledge base"
    
    formatted = f"""
## {topic.title()}
**Jurisdiction:** {jurisdiction}

---

{clean_output}

---
*Research conducted using: {sources_str}*
"""
    return formatted

# --- Drafter Node ---
def draft_node(state: AgentState):
    llm = get_llm()
    guideline_framework = state.get("guideline_framework", "OECD Guidelines")
    selected_section = state.get("selected_section")
    data_sources = state.get("data_sources", {})
    
    # Process data sources based on section type
    context_data = prepare_drafting_context(selected_section, data_sources)
    
    # Build section-specific prompt
    prompt = build_section_prompt(selected_section, guideline_framework, context_data)
    
    # Generate draft
    draft = llm.invoke(prompt).content
    
    return {
        "draft_content": draft,
        "messages": [HumanMessage(content=f"Draft: {draft}")]
    }

def prepare_drafting_context(section: str, data_sources: dict) -> str:
    """
    Prepare context data for drafting based on uploaded files and sources.
    """
    
    context_parts = []
    
    # Handle prior year documents
    if "prior_year" in data_sources:
        prior_text = process_uploaded_file(data_sources["prior_year"])
        context_parts.append(f"## Prior Year Section\n{prior_text[:2000]}...")
    
    # Section-specific data processing
    if section == "Company Analysis":
        # Handle 10-K file upload
        if "10k_file" in data_sources:
            text = process_uploaded_file(data_sources["10k_file"])
            context_parts.append(f"## 10-K Filing\n{text[:3000]}...")
    
    elif section == "Functional, Risk, Assets":
        # Handle interview notes
        if "interview_notes" in data_sources:
            structured_notes = process_interview_notes(data_sources["interview_notes"])
            context_parts.append(structured_notes)
    
    elif section == "Economic Analysis":
        # Handle benchmarking data
        if "benchmarking_set" in data_sources:
            uploaded_file = data_sources["benchmarking_set"]
            file_path = f"./temp_uploads/{uploaded_file.name}"
            
            if uploaded_file.name.endswith('.xlsx'):
                bench_summary = parse_excel_benchmarking(file_path)
            elif uploaded_file.name.endswith('.csv'):
                bench_summary = parse_csv_benchmarking(file_path)
            else:
                bench_summary = process_uploaded_file(uploaded_file)
            
            context_parts.append(f"## Benchmarking Study\n{bench_summary}")
        
        # Handle agreements
        if "agreements" in data_sources:
            agreements_text = process_multiple_files(data_sources["agreements"])
            context_parts.append(f"## Intercompany Agreements\n{agreements_text[:2000]}...")
    
    elif section == "Industry Analysis":
        # Competitors and reports
        if "competitors" in data_sources:
            competitors = ", ".join(data_sources["competitors"])
            context_parts.append(f"## Competitors to Analyze\n{competitors}")
        
        if "industry_reports" in data_sources:
            reports_text = process_multiple_files(data_sources["industry_reports"])
            context_parts.append(f"## Industry Reports\n{reports_text[:2000]}...")
    
    return "\n\n".join(context_parts) if context_parts else "No additional context provided."

def build_section_prompt(section: str, framework: str, context: str) -> str:
    """
    Build section-specific drafting prompt with guideline framework awareness.
    """
    is_oecd = "OECD" in framework
    
    oecd_reference = 'Reference OECD Transfer Pricing Guidelines chapters (I-IX) and BEPS Actions.' if is_oecd else 'Cite IRC §482 and Treasury Regulations (§1.482-X) throughout.'
    terminology = "Use arm's length principle terminology." if is_oecd else 'Use comparable uncontrolled terminology.'
    
    base_instruction = f"""
You are an expert Transfer Pricing consultant drafting documentation following {framework}.

{oecd_reference}

{terminology}
"""
    
    section_prompts = {
        "Executive Summary": f"""
{base_instruction}

Draft an Executive Summary that includes:
- Company overview and business model
- Related-party transaction summary
- Transfer pricing methodology overview
- Key findings and conclusions

{context}
""",
        
        "Company Analysis": f"""
{base_instruction}

Draft a comprehensive Company Analysis covering:
- Business description and operations
- Organizational structure
- Value chain analysis
- Key related-party relationships

Use the 10-K data and web research provided below.

{context}
""",
        
        "Functional, Risk, Assets": f"""
{base_instruction}

Draft a detailed Functional, Risk, and Assets (FRA) analysis:
- Functions performed by each entity
- Risks assumed by each party
- Assets employed (tangible and intangible)

Use interview notes and meeting summaries provided below.

{context}
""",
        
        "Industry Analysis": f"""
{base_instruction}

Draft an Industry Analysis covering:
- Industry overview and trends
- Competitive landscape
- Key economic factors
- Relevant market conditions

Analyze the competitors and industry data provided below.

{context}
""",
        
        "Economic Analysis": f"""
{base_instruction}

Draft an Economic Analysis for the specified transaction:
- Transaction description
- Transfer pricing method selection and justification
- Benchmarking analysis
- Comparability adjustments
- Conclusion on arm's length pricing

Use the benchmarking study and agreements provided below.

{context}
"""
    }
    
    return section_prompts.get(section, base_instruction + "\n\n" + context)

# --- Assistant Node (ReAct Pattern) ---
def assistant_node(state: AgentState):
    """
    Conversational assistant using ReAct pattern.
    Has access to search tools for answering questions.
    """
    llm = get_llm()
    messages = state["messages"]
    
    system_message = (
        "You are a helpful Transfer Pricing assistant with access to a regulatory knowledge base (which includes IRC 482, OECD Guidelines, AND user-uploaded internal documents) and web search.\n\n"
        "**CORE INSTRUCTIONS:**\n"
        "1. **Check Context First:** Before searching, check the conversation history. If the answer is already there, use it.\n"
        "2. **Internal Docs & Regulations:** If the user asks about internal agreements, policies, or specific regulations, USE the 'search_regulations' tool. This tool searches BOTH external regulations and the internal Knowledge Base.\n"
        "   - **IMPORTANT:** If the user mentions a specific file (e.g., 'check MockCompanyData.docx'), you MUST pass the filename to the `filter_source` argument of `search_regulations` to find it.\n"
        "3. **Tool Usage:** Use 'search_regulations' for domain knowledge/docs, and 'web_search' for real-time info/news.\n"
        "4. **Formatting:** Follow user formatting instructions strictly.\n"
        "5. **Quality:** Provide clear, concise answers. Do NOT claim you don't have access to internal documents without trying to search for them first."
    )
    
    tools = [search_regulations, web_search]
    
    # Create ReAct agent
    agent_app = create_react_agent(llm, tools, prompt=system_message)
    
    # Run agent
    result = agent_app.invoke({"messages": messages})
    
    # Extract response
    response = result["messages"][-1]
    
    return {"messages": [response]}
