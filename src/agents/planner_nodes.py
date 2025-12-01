"""
Planner nodes for Plan-and-Execute architecture.
Creates step-by-step execution plans for research and drafting tasks.
"""
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState
import os
import re

MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def get_llm():
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)

def parse_plan(plan_text: str) -> List[str]:
    """
    Parse LLM plan output into list of steps.
    Handles numbered lists like:
    1. Step one
    2. Step two
    """
    lines = plan_text.strip().split('\n')
    steps = []
    for line in lines:
        line = line.strip()
        # Match lines starting with number followed by period or parenthesis
        if line and (re.match(r'^\d+[\.\)]', line) or line.startswith('-')):
            # Remove number prefix
            step = re.sub(r'^\d+[\.\)]\s*', '', line)
            step = step.lstrip('- ')
            if step:
                steps.append(step)
    return steps

def research_planner_node(state: AgentState):
    """
    Creates a step-by-step research plan.
    
    Input: research_topic, jurisdiction, web_sources
    Output: plan (list of steps), current_step (0)
    """
    llm = get_llm()
    topic = state.get("research_topic")
    jurisdiction = state.get("jurisdiction", "General")
    web_sources = state.get("web_sources", {})
    
    # Determine available tools
    tools_available = ["search_regulations (regulatory knowledge base)"]
    
    if any(web_sources.get(source, False) for source in ["IRS", "OECD", "Deloitte", "PwC", "EY", "KPMG"]):
        tools_available.append("web_search (domain-restricted web search)")
    
    if web_sources.get("YouTube", False):
        tools_available.append("youtube_search (educational videos)")
    
    planning_prompt = f"""You are a Transfer Pricing research planner.

Create a 3-5 step research plan for the following request:

**Topic:** {topic}
**Jurisdiction:** {jurisdiction}

**Available Tools:**
{chr(10).join(f'- {tool}' for tool in tools_available)}

**Requirements:**
- Each step should specify WHAT to search and WHY
- Use appropriate tools for each step
- Start with regulatory knowledge base, then expand to web/video if needed
- Final step should be synthesis/formatting

Format as a numbered list. Be specific and actionable.
"""
    
    plan_text = llm.invoke(planning_prompt).content
    steps = parse_plan(plan_text)
    
    return {
        "plan": steps,
        "current_step": 0,
        "step_results": [],
        "needs_replan": False
    }

def composer_planner_node(state: AgentState):
    """
    Creates a step-by-step drafting plan.
    
    Input: selected_section, data_sources, guideline_framework
    Output: plan (list of steps), current_step (0)
    """
    llm = get_llm()
    section = state.get("selected_section")
    framework = state.get("guideline_framework", "OECD Guidelines")
    sources = state.get("data_sources", {})
    
    # List available data sources
    available_data = []
    if "10k_file" in sources:
        available_data.append("10-K report")
    if "interview_notes" in sources:
        available_data.append("Interview/meeting notes")
    if "benchmarking_set" in sources:
        available_data.append("Benchmarking study")
    if "agreements" in sources:
        available_data.append("Intercompany agreements")
    if "prior_year" in sources:
        available_data.append("Prior year section")
    if "competitors" in sources:
        available_data.append(f"Competitor list: {', '.join(sources['competitors'][:3])}")
    
    planning_prompt = f"""You are a Transfer Pricing documentation planner.

Create a 4-6 step drafting plan for the following section:

**Section:** {section}
**Framework:** {framework}
**Available Data:** {', '.join(available_data) if available_data else 'None'}

**Requirements:**
- First steps: Extract/process available data sources
- Middle steps: Analyze and structure findings
- Final steps: Draft section following {framework} guidelines and add citations
- Ensure compliance with regulatory requirements

Format as a numbered list. Be specific about what each step accomplishes.
"""
    
    plan_text = llm.invoke(planning_prompt).content
    steps = parse_plan(plan_text)
    
    return {
        "plan": steps,
        "current_step": 0,
        "step_results": [],
        "needs_replan": False
    }
