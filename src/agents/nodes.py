from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .tools import search_regulations, web_search

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

def format_research_output(raw_output: str, topic: str, jurisdiction: str) -> str:
    """
    Clean and format the raw agent output for user-friendly display.
    Removes tool invocation artifacts and structures the output nicely.
    """
    # Remove common artifacts from tool calls
    clean_output = raw_output
    
    # Remove tool call patterns like "Action: tool_name" or "Observation:"
    import re
    clean_output = re.sub(r'Action:.*?\n', '', clean_output)
    clean_output = re.sub(r'Observation:.*?\n', '', clean_output)
    clean_output = re.sub(r'Thought:.*?\n', '', clean_output)
    clean_output = re.sub(r'Final Answer:', '', clean_output)
    
    # Build formatted output
    formatted = f"# Research Findings: {topic}\n\n"
    formatted += f"**Jurisdiction:** {jurisdiction}\n\n---\n\n"
    formatted += clean_output.strip()
    formatted += "\n\n---\n\n"
    formatted += "*Research conducted using Transfer Pricing regulatory knowledge base*"
    
    return formatted

# --- Drafter Node ---
def draft_node(state: AgentState):
    llm = get_llm()
    doc_type = state.get("document_type")
    # In a real app, we would load the uploaded file content here
    # For now, we assume it's in the state or we simulate it
    
    prompt = f"""
    You are an expert Transfer Pricing Drafter.
    Document Type: {doc_type}
    
    Please draft a professional document based on standard templates and the provided context.
    Ensure it is compliant with relevant regulations.
    """
    
    response = llm.invoke([SystemMessage(content=prompt), HumanMessage(content="Generate the draft.")])
    
    return {
        "draft_content": response.content,
        "messages": [HumanMessage(content=f"Draft generated for {doc_type}")]
    }

# --- Assistant Node ---
def assistant_node(state: AgentState):
    llm = get_llm()
    messages = state["messages"]
    
    # Simple chatbot logic
    response = llm.invoke(messages)
    
    return {"messages": [response]}
