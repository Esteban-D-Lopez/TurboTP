"""
Synthesizer and replanner nodes for Plan-and-Execute architecture.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from .state import AgentState
from .nodes import format_research_output
import os

MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def get_llm():
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)

def research_synthesizer_node(state: AgentState):
    """
    Combines all step results into final research findings.
    Formats output cleanly for display.
    """
    llm = get_llm()
    step_results = state.get("step_results", [])
    topic = state.get("research_topic")
    jurisdiction = state.get("jurisdiction", "General")
    
    # Combine all results and track sources
    combined_findings = []
    sources_used = set(["Regulatory Knowledge Base"])  # Always start with RAG
    
    for i, result in enumerate(step_results, 1):
        combined_findings.append(f"### Step {i}: {result['step']}\n{result['result']}\n")
        
        # Track sources based on tools ACTUALLY used in results
        tool = result.get("tool", "").lower()
        if "web" in tool and "search" in tool:
            sources_used.add("Web Search")
        elif "youtube" in tool:
            sources_used.add("YouTube")
    
    context = "\n\n".join(combined_findings)
    
    # Synthesize into structured output
    synthesis_prompt = f"""You are synthesizing Transfer Pricing research findings.

**Topic:** {topic}
**Jurisdiction:** {jurisdiction}

**Research Steps Completed:**
{context}

**IMPORTANT: Output ONLY in clean Markdown format. Do NOT use HTML tags.**

Create a comprehensive research summary that:
1. Starts with an executive summary paragraph
2. Organizes findings under clear ### headings (use markdown ###, NOT HTML)
3. Cites sources in brackets like [IRC §482] or [OECD Guidelines Ch. X]
4. Uses bullet points (-) for key takeaways
5. Is concise but comprehensive

Focus on actionable insights and regulatory compliance. Use ONLY markdown formatting.
"""
    
    raw_synthesis = llm.invoke(synthesis_prompt).content
    
    # Format for clean display
    # Format for clean display
    formatted_findings = format_research_output(raw_synthesis, topic, jurisdiction, list(sources_used))
    
    from langchain_core.messages import AIMessage
    
    return {
        "research_findings": formatted_findings,
        "messages": [AIMessage(content=formatted_findings)]
    }

def composer_synthesizer_node(state: AgentState):
    """
    Combines all drafting step results into final document section.
    """
    step_results = state.get("step_results", [])
    section = state.get("selected_section")
    
    # Find the actual draft content (usually in last few steps)
    draft_content = None
    for result in reversed(step_results):
        if "draft" in result.get("step", "").lower() or len(result.get("result", "")) > 500:
            draft_content = result["result"]
            break
    
    if not draft_content:
        # Combine all results if no clear draft step
        draft_content = "\n\n".join([r["result"] for r in step_results])
    
    from langchain_core.messages import AIMessage
    
    return {
        "draft_content": draft_content,
        "messages": [AIMessage(content=draft_content)]
    }

def replanner_node(state: AgentState):
    """
    Analyzes failures and revises the plan.
    
    Triggers when needs_replan is True (usually from executor failures).
    """
    llm = get_llm()
    plan = state.get("plan", [])
    step_results = state.get("step_results", [])
    current_step = state.get("current_step", 0)
    
    # Get the failed step
    if step_results and "ERROR" in step_results[-1].get("result", ""):
        failed_step = step_results[-1]
        
        replan_prompt = f"""A research/drafting step has failed:

**Failed Step:** {failed_step['step']}
**Error:** {failed_step['result']}

**Original Plan:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(plan))}

**Completed Steps:** {len(step_results) - 1}

Revise the remaining plan to:
1. Work around this failure
2. Try alternative approaches
3. Ensure we still achieve the goal

Provide only the revised remaining steps as a numbered list.
"""
        
        revised_plan_text = llm.invoke(replan_prompt).content
        
        # Parse revised plan
        from .planner_nodes import parse_plan
        revised_steps = parse_plan(revised_plan_text)
        
        # Replace remaining steps in plan
        new_plan = plan[:current_step] + revised_steps
        
        return {
            "plan": new_plan,
            "needs_replan": False
        }
    
    # No replanning needed
    return {"needs_replan": False}

def should_continue_executing(state: AgentState) -> str:
    """
    Routing function to determine next node in Plan-Execute loop.
    
    Returns:
    - "continue": Execute next step
    - "replan": Need to revise plan due to failure
    - "synthesize": All steps complete, combine results
    """
    current_step = state.get("current_step", 0)
    plan = state.get("plan", [])
    needs_replan = state.get("needs_replan", False)
    
    if needs_replan:
        return "replan"
    elif current_step >= len(plan):
        return "synthesize"
    else:
        return "continue"
