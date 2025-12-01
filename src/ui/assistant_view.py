import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.graph import create_graph
from src.utils.rag_manager import list_documents, add_document_to_kb

def render_assistant_view():
    # Sidebar for Knowledge Base
    with st.sidebar:
        st.header("📚 Knowledge Base")
        st.info("Documents uploaded here are accessible to the Assistant.")
        
        # File Uploader
        uploaded_file = st.file_uploader("Add Document", type=['pdf', 'docx', 'txt', 'md'])
        if uploaded_file:
            with st.spinner("Processing..."):
                result = add_document_to_kb(uploaded_file)
                if "Success" in result:
                    st.success(result)
                else:
                    st.error(result)
        
        st.divider()
        
        # List Documents
        st.subheader("Active Documents")
        docs = list_documents()
        if docs:
            for doc in docs:
                st.text(f"📄 {doc}")
        else:
            st.caption("No documents added yet.")

    st.header("Agent Assistant")
    st.markdown("Chat with the Transfer Pricing expert.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Thinking..."):
            app = create_graph()
            
            # Convert session history to LangChain messages
            history = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    history.append(HumanMessage(content=msg["content"]))
                else:
                    history.append(AIMessage(content=msg["content"]))
            
            initial_state = {
                "messages": history,
                "current_mode": "chat"
            }
            
            # Run Graph
            # Note: In a real chat loop, we'd stream or handle state differently
            # For this MVP, we just invoke once per turn
            final_state = app.invoke(initial_state)
            raw_response = final_state["messages"][-1]
            
            # Ensure we extract just the string content
            if hasattr(raw_response, 'content'):
                content = raw_response.content
                if isinstance(content, list):
                    # Handle list of text blocks (e.g. [{'type': 'text', 'text': '...'}])
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if 'text' in item:
                                text_parts.append(item['text'])
                            elif 'content' in item:
                                text_parts.append(item['content'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    response = "\n".join(text_parts)
                else:
                    response = str(content)
            elif isinstance(raw_response, dict) and 'content' in raw_response:
                response = str(raw_response['content'])
            else:
                response = str(raw_response)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
