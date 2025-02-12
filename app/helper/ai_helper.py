from app.helper.llm_helper import GoogleGeminiEmbeddings, GoogleGeminiLLM
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.helper.general_helper import Helper
from app.utils.exception_handler import handle_exception


class AIHelper:
    # Load text from a website, split into chunks, and store in FAISS
    def get_vectorstore_from_url(url):
        try:
            is_valid, error_message = Helper.validate_url(url)
            if not is_valid:
                return None, error_message

            loader = WebBaseLoader(url)
            document = loader.load()
            text_splitter = RecursiveCharacterTextSplitter()
            document_chunks = text_splitter.split_documents(document)

            embeddings = GoogleGeminiEmbeddings()
            vector_store = FAISS.from_documents(document_chunks, embeddings)
            return vector_store, None
        except Exception as e:
            return None, handle_exception(e)


    # Create a context-aware retriever chain
    def get_context_retriever_chain(vector_store):
        try:
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

            return create_history_aware_retriever(llm, retriever, prompt)
        except Exception as e:
            return handle_exception(e)


    # Create a conversational Retrieval-Augmented Generation chain
    def get_conversational_rag_chain(retriever_chain):
        try:
            llm = GoogleGeminiLLM()
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "Answer the user's questions based on the below context:\n\n{context}"),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("user", "{input}"),
                ]
            )
            return create_retrieval_chain(retriever_chain, create_stuff_documents_chain(llm, prompt))
        except Exception as e:
            return handle_exception(e)


    # Generate a response for user input
    def get_response(user_input, chat_history, vector_store):
        try:
            if vector_store is None:
                return "Please load a website first."

            retriever_chain = AIHelper.get_context_retriever_chain(vector_store)
            conversation_rag_chain = AIHelper.get_conversational_rag_chain(retriever_chain)

            response = conversation_rag_chain.invoke({"chat_history": chat_history, "input": user_input})
            return response["answer"]
        except Exception as e:
            return handle_exception(e)
