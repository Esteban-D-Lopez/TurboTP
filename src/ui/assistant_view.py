import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.graph import create_graph

def render_assistant_view():
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
            response = final_state["messages"][-1].content
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
