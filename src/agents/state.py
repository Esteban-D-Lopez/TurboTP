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
    web_sources: Optional[dict]  # Enabled web sources for research
    # Composer-specific fields
    guideline_framework: Optional[str]  # 'OECD Guidelines' or 'US Regulations (IRC §482)'
    selected_section: Optional[str]  # Section being drafted
    data_sources: Optional[dict]  # Section-specific data sources
    transaction_details: Optional[dict]  # For economic analysis
