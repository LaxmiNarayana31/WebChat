import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.helper.ai_helper import AIHelper
from app.helper.general_helper import Helper


def main():
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    st.set_page_config(page_title="WebChat", page_icon="🌐")

    if "current_chat" not in st.session_state:
        st.session_state.current_chat = []
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []
    if "selected_chat_index" not in st.session_state:
        st.session_state.selected_chat_index = None
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    sidebar()
    chat_interface()


def sidebar():
    with st.sidebar:
        st.header("Chat with Websites")
        website_url = st.text_input("Enter Website URL")

        if st.button("Load Website"):
            with st.spinner("Processing website..."):
                st.session_state.selected_chat_index = None
                vector_store, error_message = AIHelper.get_vectorstore_from_url(website_url)

                if error_message:
                    st.error(error_message)
                elif vector_store:
                    st.session_state.vector_store = vector_store

                    if "chat_histories" not in st.session_state:
                        st.session_state.chat_histories = []

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

        if st.button("+ New Chat"):
            st.session_state.selected_chat_index = None
            st.session_state.vector_store = None
            st.session_state.current_chat = []

        display_chat_history()


def display_chat_history():
    st.sidebar.header("Chat History")

    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = []

    for idx, history in enumerate(st.session_state.chat_histories):
        website_url = history.get("website_url", "Unknown Website")

        user_messages = [msg for msg in history.get("messages", []) if msg["role"] == "user"]
        chat_preview = get_chat_preview(user_messages[0]["content"]) if user_messages else "No messages"

        if st.sidebar.button(f"{website_url}"):
            st.session_state.selected_chat_index = idx
            st.session_state.vector_store = history.get("vector_store")
            st.session_state.current_chat = history.get("messages", [])


def get_chat_preview(message):
    words = message.split()
    preview = " ".join(words[:7])
    return f"{preview}..." if len(words) > 10 else message


def chat_interface():
    _, col2 = st.columns([1, 2.8])
    with col2:
        st.header("WebChat 🌐")

    if st.session_state.selected_chat_index is not None:
        current_chat = st.session_state.chat_histories[st.session_state.selected_chat_index]
        messages = current_chat.get("messages", [])
    else:
        messages = st.session_state.current_chat

    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_query = st.chat_input("Type your message...")
    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        if st.session_state.vector_store is None:
            with st.chat_message("assistant"):
                st.warning("Please load a website first.")
        else:
            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("Generating response...")
                response = AIHelper.get_response(user_query, st.session_state.current_chat, st.session_state.vector_store)
                placeholder.empty()
                Helper.typewriter_effect(response, speed=20)

            if st.session_state.selected_chat_index is not None:
                current_chat = st.session_state.chat_histories[st.session_state.selected_chat_index]
                current_chat["messages"].append({"role": "user", "content": user_query})
                current_chat["messages"].append({"role": "assistant", "content": response})
                st.session_state.current_chat = current_chat["messages"]
            else:
                st.session_state.current_chat.append({"role": "user", "content": user_query})
                st.session_state.current_chat.append({"role": "assistant", "content": response})

            st.rerun()

