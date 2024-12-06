import streamlit as st
from app.helper.ai_helper import get_response
from app.helper.general_helper import typewriter


# Main chat interface
def chat_interface():
    _, col2 = st.columns([1, 2.8])
    with col2:
        st.header("WebChat 🌐")

    # Handle chat display based on selected chat or current chat
    if st.session_state.selected_chat_index is not None:
        current_chat = st.session_state.chat_histories[
            st.session_state.selected_chat_index
        ]
        messages = current_chat.get("messages", [])
    else:
        messages = st.session_state.current_chat

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input handling
    user_query = st.chat_input("Type your message...")
    if user_query:
        # Immediately display user message in the main chat area
        with st.chat_message("user"):
            st.markdown(user_query)

        if st.session_state.vector_store is None:
            with st.chat_message("assistant"):
                st.warning("Please load a website first using the sidebar.")
        else:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("Generating response...")
                response = get_response(user_query)
                placeholder.empty()
                typewriter(response, speed=20)

            # Update chat history
            if st.session_state.selected_chat_index is not None:
                current_chat = st.session_state.chat_histories[
                    st.session_state.selected_chat_index
                ]
                current_chat["messages"].append({"role": "user", "content": user_query})
                current_chat["messages"].append(
                    {"role": "assistant", "content": response}
                )
                st.session_state.current_chat = current_chat["messages"]
            else:
                st.session_state.current_chat.append(
                    {"role": "user", "content": user_query}
                )
                st.session_state.current_chat.append(
                    {"role": "assistant", "content": response}
                )

            st.rerun()
