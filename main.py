import streamlit as st
from dotenv import load_dotenv
from components.sidebar import sidebar
from components.chat import chat_interface


def main():
    load_dotenv()
    st.set_page_config(page_title="WebChat", page_icon="🌐")

    # Initialize session state variables
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


if __name__ == "__main__":
    main()
