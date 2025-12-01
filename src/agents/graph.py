from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import supervisor_node, research_node, draft_node, assistant_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("drafter", draft_node)
    workflow.add_node("assistant", assistant_node)
    
    # Set Entry Point
    workflow.set_entry_point("supervisor")
    
    # Add Edges
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "researcher": "researcher",
            "drafter": "drafter",
            "assistant": "assistant",
            "__end__": END
        }
    )
    
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("drafter", "supervisor")
    workflow.add_edge("assistant", END) # Chat usually ends after one turn in this simple model, or loops back
    
    return workflow.compile()
