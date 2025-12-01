from typing import TypedDict, Annotated, List, Union, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    next: str
    current_mode: str  # 'research', 'composer', 'chat'
    research_topic: Optional[str]
    research_findings: Optional[str]
    document_type: Optional[str]
    draft_content: Optional[str]
    jurisdiction: Optional[str]
