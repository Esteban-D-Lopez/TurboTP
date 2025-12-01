from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
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

# --- Researcher Node ---
def research_node(state: AgentState):
    llm = get_llm()
    topic = state.get("research_topic")
    jurisdiction = state.get("jurisdiction", "General")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite Transfer Pricing Senior Consultant. "
                   "Your goal is to conduct thorough research on the given topic. "
                   "Always cite your sources (IRC 482, OECD Guidelines, etc.)."),
        ("human", f"Research Topic: {topic}\nJurisdiction: {jurisdiction}\n\n"
                  "Use your tools to find relevant regulations and information. "
                  "Summarize your findings in a structured format.")
    ])
    
    tools = [search_regulations, web_search]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    result = agent_executor.invoke({"input": topic})
    findings = result["output"]
    
    return {
        "research_findings": findings,
        "messages": [HumanMessage(content=f"Research Findings: {findings}")]
    }

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
