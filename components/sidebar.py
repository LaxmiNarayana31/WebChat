import streamlit as st
from app.helper.ai_helper import get_vectorstore_from_url


# Create sidebar with URL input and chat management
def sidebar():
    with st.sidebar:
        st.header("Chat with Websites")

        website_url = st.text_input("Enter Website URL")

        # Process URL button
        if st.button("Load Website"):
            with st.spinner("Processing website..."):
                # Reset selected chat index
                st.session_state.selected_chat_index = None

                # Create vector store from URL
                vector_store = get_vectorstore_from_url(website_url)

                # Only proceed if vector store is successfully created
                if vector_store:
                    st.session_state.vector_store = vector_store

                    if not hasattr(st.session_state, "chat_histories"):
                        st.session_state.chat_histories = []

                    # Add current chat to history
                    current_chat = {
                        "website_url": website_url,
                        "vector_store": vector_store,
                        "messages": [
                            {
                                "role": "assistant",
                                "content": f"Hello! I'm ready to answer questions about {website_url}",
                            }
                        ],
                    }
                    st.session_state.chat_histories.insert(0, current_chat)
                    st.session_state.current_chat = current_chat["messages"]
                    st.success("Website loaded successfully!")

        # New Chat button
        if st.button("+ New Chat"):
            st.session_state.selected_chat_index = None
            st.session_state.vector_store = None
            st.session_state.current_chat = []

        display_chat_history()


def display_chat_history():
    """Display chat history in the sidebar."""
    st.sidebar.header("Chat History")

    # Ensure chat_histories exists
    if not hasattr(st.session_state, "chat_histories"):
        st.session_state.chat_histories = []

    for idx, history in enumerate(st.session_state.chat_histories):
        website_url = history.get("website_url", "Unknown Website")

        user_messages = [
            msg for msg in history.get("messages", []) if msg["role"] == "user"
        ]
        chat_preview = (
            get_chat_preview(user_messages[0]["content"])
            if user_messages
            else "No messages"
        )

        if st.sidebar.button(f"{website_url}"):
            st.session_state.selected_chat_index = idx
            st.session_state.vector_store = history.get("vector_store")
            st.session_state.current_chat = history.get("messages", [])


# Get a preview of the chat message
def get_chat_preview(message):
    words = message.split()
    preview = " ".join(words[:7])
    return f"{preview}..." if len(words) > 10 else message
