from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import supervisor_node, assistant_node
from .planner_nodes import research_planner_node, composer_planner_node
from .executor_nodes import research_executor_node, composer_executor_node
from .synthesizer_nodes import (
    research_synthesizer_node,
    composer_synthesizer_node,
    replanner_node,
    should_continue_executing
)

def route_by_mode(state: AgentState) -> str:
    """Route to appropriate planner based on mode."""
    mode = state.get("current_mode")
    messages = state.get("messages", [])
    
    if mode == "research":
        # If we have findings, it's a follow-up -> use Assistant
        if state.get("research_findings"):
            return "assistant"
        # Otherwise, it's a new request -> use Planner
        return "research_planner"
    elif mode == "composer":
        return "composer_planner"
    else:  # chat mode
        return "assistant"

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add supervisor
    workflow.add_node("supervisor", supervisor_node)
    
    # Research nodes (Plan-and-Execute)
    workflow.add_node("research_planner", research_planner_node)
    workflow.add_node("research_executor", research_executor_node)
    workflow.add_node("research_replanner", replanner_node)
    workflow.add_node("research_synthesizer", research_synthesizer_node)
    
    # Composer nodes (Plan-and-Execute)
    workflow.add_node("composer_planner", composer_planner_node)
    workflow.add_node("composer_executor", composer_executor_node)
    workflow.add_node("composer_replanner", replanner_node)
    workflow.add_node("composer_synthesizer", composer_synthesizer_node)
    
    # Assistant node (ReAct)
    workflow.add_node("assistant", assistant_node)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Route from supervisor to mode-specific planners
    workflow.add_conditional_edges(
        "supervisor",
        route_by_mode,
        {
            "research_planner": "research_planner",
            "composer_planner": "composer_planner",
            "assistant": "assistant"
        }
    )
    
    # Research flow: Plan → Execute (loop) → Synthesize
    workflow.add_edge("research_planner", "research_executor")
    workflow.add_conditional_edges(
        "research_executor",
        should_continue_executing,
        {
            "continue": "research_executor",      # Execute next step
            "replan": "research_replanner",       # Revise plan
            "synthesize": "research_synthesizer"  # Done, combine results
        }
    )
    workflow.add_edge("research_replanner", "research_executor")  # After replan, continue executing
    workflow.add_edge("research_synthesizer", END)
    
    # Composer flow: Plan → Execute (loop) → Synthesize
    workflow.add_edge("composer_planner", "composer_executor")
    workflow.add_conditional_edges(
        "composer_executor",
        should_continue_executing,
        {
            "continue": "composer_executor",
            "replan": "composer_replanner",
            "synthesize": "composer_synthesizer"
        }
    )
    workflow.add_edge("composer_replanner", "composer_executor")
    workflow.add_edge("composer_synthesizer", END)
    
    # Assistant flow: Direct to END (ReAct handles internally)
    workflow.add_edge("assistant", END)
    
    return workflow.compile()
