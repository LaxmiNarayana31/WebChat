import streamlit as st
from app.helper.model_helper import (
    GoogleGeminiEmbeddings,
    GoogleGeminiLLM,
)
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.helper.general_helper import validate_url


# Load text from a website, split into chunks, and store in FAISS
def get_vectorstore_from_url(url):
    # Validate URL first
    is_valid, error_message = validate_url(url)
    if not is_valid:
        st.error(error_message)
        return None

    try:
        loader = WebBaseLoader(url)
        document = loader.load()

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter()
        document_chunks = text_splitter.split_documents(document)

        # Create a vectorstore using Gemini embeddings
        embeddings = GoogleGeminiEmbeddings()
        vector_store = FAISS.from_documents(document_chunks, embeddings)

        return vector_store
    except Exception as e:
        st.error(f"Error processing website: {str(e)}")
        return None


# Create a context-aware retriever chain
def get_context_retriever_chain(vector_store):
    llm = GoogleGeminiLLM()

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            (
                "user",
                "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.",
            ),
        ]
    )

    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain


# Create a conversational Retrieval-Augmented Generation chain
def get_conversational_rag_chain(retriever_chain):
    llm = GoogleGeminiLLM()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user's questions based on the below context:\n\n{context}",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


# Generate a response for user input
def get_response(user_input):
    if st.session_state.selected_chat_index is not None:
        current_chat = st.session_state.chat_histories[
            st.session_state.selected_chat_index
        ]
        chat_history = current_chat.get("messages", [])
        vector_store = current_chat.get("vector_store")
    else:
        # If no selected chat and no vector store, return an error message
        if (
            not hasattr(st.session_state, "vector_store")
            or st.session_state.vector_store is None
        ):
            return "Please load a website first using the sidebar."

        chat_history = st.session_state.current_chat
        vector_store = st.session_state.vector_store

    retriever_chain = get_context_retriever_chain(vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)

    response = conversation_rag_chain.invoke(
        {"chat_history": chat_history, "input": user_input}
    )

    return response["answer"]
