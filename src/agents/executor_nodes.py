"""
Executor nodes for Plan-and-Execute architecture.
Executes individual steps of research and drafting plans.
"""
from typing import Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState
from .tools import search_regulations, web_search, youtube_search
from src.utils.file_processor import (
    process_uploaded_file,
    process_multiple_files,
    process_interview_notes,
    parse_excel_benchmarking,
    parse_csv_benchmarking
)
import os
import re

MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def get_llm():
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)

def parse_step_for_tool(step_text: str) -> Tuple[str, str]:
    """
    Parse a plan step to determine which tool to use and what query to execute.
    
    Returns: (tool_name, query)
    """
    step_lower = step_text.lower()
    
    # Detect tool based on explicit tool name or keywords
    if "youtube_search" in step_lower or "youtube" in step_lower or "video" in step_lower:
        tool = "youtube_search"
    elif "web_search" in step_lower or "web" in step_lower or "online" in step_lower or "internet" in step_lower or "site" in step_lower or "google" in step_lower:
        tool = "web_search"
    elif any(x in step_lower for x in ["irs", "oecd", "deloitte", "pwc", "ey", "kpmg"]) and "search" in step_lower:
        # If mentioning specific web sources with "search", likely web search
        tool = "web_search"
    elif "search_regulations" in step_lower or "regulation" in step_lower or "knowledge base" in step_lower:
        tool = "search_regulations"
    else:
        # Default to regulations search
        tool = "search_regulations"
    
    # Extract query (remove tool indicators and step numbers)
    query = re.sub(r'^\d+[\.\)]\s*', '', step_text)  # Remove step number
    query = re.sub(r'\b(using|with|via)\s+(search_regulations|web_search|youtube_search)\b', '', query, flags=re.IGNORECASE)
    query = query.strip()
    
    return tool, query

def research_executor_node(state: AgentState):
    """
    Executes one step of the research plan using appropriate tools.
    
    Reads: plan, current_step
    Executes: the current step
    Updates: step_results, current_step
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    step_results = state.get("step_results", [])
    web_sources = state.get("web_sources", {})
    
    if current_step >= len(plan):
        return state  # Plan complete, no update
    
    step = plan[current_step]
    
    # Parse step to determine tool and query
    tool_name, query = parse_step_for_tool(step)
    
    # Execute with appropriate tool
    try:
        if tool_name == "search_regulations":
            result = search_regulations.invoke(query)
        elif tool_name == "web_search":
            # Get enabled domains
            enabled_domains = []
            domain_map = {
                "IRS": ["irs.gov"],
                "OECD": ["oecd.org"],
                "Deloitte": ["deloitte.com"],
                "PwC": ["pwc.com"],
                "EY": ["ey.com"],
                "KPMG": ["kpmg.com"]
            }
            for source, domains in domain_map.items():
                if web_sources.get(source, False):
                    enabled_domains.extend(domains)
            
            # Add custom domains
            custom_domains = web_sources.get("custom_domains", [])
            if custom_domains:
                enabled_domains.extend(custom_domains)
            
            result = web_search.invoke({"query": query, "domains": enabled_domains if enabled_domains else None})
        elif tool_name == "youtube_search":
            result = youtube_search.invoke(query)
        else:
            result = f"Unknown tool: {tool_name}"
        
        step_results.append({
            "step": step,
            "tool": tool_name,
            "query": query,
            "result": result
        })
        
        return {
            "step_results": step_results,
            "current_step": current_step + 1,
            "needs_replan": False
        }
        
    except Exception as e:
        # Mark for replanning if step fails
        step_results.append({
            "step": step,
            "tool": tool_name,
            "query": query,
            "result": f"ERROR: {str(e)}"
        })
        
        return {
            "step_results": step_results,
            "needs_replan": True
        }

def composer_executor_node(state: AgentState):
    """
    Executes one step of the drafting plan.
    
    Handles:
    - Data extraction from uploaded files
    - Processing and structuring data
    - Drafting text with LLM
    """
    plan = state.get("plan", [])
    current_step = state.get("current_step", 0)
    step_results = state.get("step_results", [])
    data_sources = state.get("data_sources", {})
    
    if current_step >= len(plan):
        return state  # Plan complete
    
    step = plan[current_step]
    step_lower = step.lower()
    
    try:
        result = None
        
        # Determine what this step needs to do based on keywords
        if "extract" in step_lower or "process" in step_lower:
            # Data extraction step
            if "10-k" in step_lower or "10k" in step_lower:
                if "10k_file" in data_sources:
                    source = data_sources["10k_file"]
                    
                    # Handle string (KB file) vs UploadedFile
                    if isinstance(source, str):
                        # It's a filename from the Knowledge Base
                        from src.utils.rag_manager import KNOWLEDGE_BASE_DIR
                        file_path = os.path.join(KNOWLEDGE_BASE_DIR, source)
                        
                        # Use appropriate extractor based on extension
                        if source.lower().endswith('.pdf'):
                            from src.utils.file_processor import extract_text_from_pdf
                            text = extract_text_from_pdf(file_path)
                        elif source.lower().endswith('.docx'):
                            from src.utils.file_processor import extract_text_from_docx
                            text = extract_text_from_docx(file_path)
                        else:
                            # Fallback for text files
                            try:
                                with open(file_path, 'r') as f:
                                    text = f.read()
                            except Exception as e:
                                text = f"Error reading file: {str(e)}"
                    else:
                        # It's a Streamlit UploadedFile
                        text = process_uploaded_file(source)
                        
                    if text.startswith("Error") or text.startswith("Unsupported"):
                        result = f"Failed to extract 10-K: {text}"
                    else:
                        result = f"Extracted 10-K content ({len(text)} characters)"
                else:
                    result = "No 10-K file available"
            
            elif "interview" in step_lower or "notes" in step_lower:
                if "interview_notes" in data_sources:
                    # Handle list of files
                    notes_files = data_sources["interview_notes"]
                    if not isinstance(notes_files, list):
                        notes_files = [notes_files]
                    
                    structured = process_interview_notes(notes_files)
                    result = f"Processed interview notes:\n{structured[:500]}..."
                else:
                    result = "No interview notes available"
            
            elif "benchmark" in step_lower:
                if "benchmarking_set" in data_sources:
                    uploaded_file = data_sources["benchmarking_set"]
                    # Save file first using helper
                    from src.utils.file_processor import save_uploaded_file
                    file_path = save_uploaded_file(uploaded_file)
                    
                    if uploaded_file.name.endswith('.xlsx'):
                        result = parse_excel_benchmarking(file_path)
                    elif uploaded_file.name.endswith('.csv'):
                        result = parse_csv_benchmarking(file_path)
                    else:
                        result = process_uploaded_file(uploaded_file)
                else:
                    result = "No benchmarking data available"
            
            else:
                result = "Data extraction step - generic processing"
        
        elif "draft" in step_lower or "write" in step_lower:
            # Drafting step - use LLM with accumulated context
            llm = get_llm()
            context = "\n\n".join([sr["result"] for sr in step_results if "result" in sr])
            
            # Fetch Regulatory Context (RAG)
            # Determine what to search for based on the step or section
            # We can use the step description itself as a query, or construct one
            reg_query = f"guidelines for {step}"
            regulatory_context = search_regulations.invoke(reg_query)
            
            draft_prompt = f"""You are a Transfer Pricing expert. Draft the following section of a TP report.

**Task:** {step}

**Regulatory Guidelines (Context):**
{regulatory_context}

**Available Data & Analysis:**
{context}

**Instructions:**
1. Write a professional, compliant draft for this section.
2. CITE the regulatory guidelines where appropriate (e.g., "In accordance with OECD Guidelines...").
3. Use the provided data to support your statements.
4. If data is missing, state what is needed rather than making it up.
"""
            
            result = llm.invoke(draft_prompt).content
        
        else:
            # Generic step - just acknowledge
            result = f"Completed: {step}"
        
        step_results.append({
            "step": step,
            "result": result
        })
        
        return {
            "step_results": step_results,
            "current_step": current_step + 1,
            "needs_replan": False
        }
        
    except Exception as e:
        step_results.append({
            "step": step,
            "result": f"ERROR: {str(e)}"
        })
        
        return {
            "step_results": step_results,
            "needs_replan": True
        }
