import os
os.environ["ANONYMIZED_TELEMETRY"] = "False" # Force disable at the OS level
from langchain_groq import ChatGroq
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceInferenceAPIEmbeddings
from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from colorama import Fore, Style, init
from dotenv import load_dotenv
import warnings

"""
This module provides a Retrieval-Augmented Generation (RAG) system for customer support.
It uses Groq for the LLM and Hugging Face Inference API for embeddings (to save memory in cloud deployment).
"""

warnings.filterwarnings("ignore")
init(autoreset=True)
load_dotenv()

template: str = """/
    You are a customer support specialist /
    question: {question}. 
    You assist users with general inquiries based on {context} /
    and  technical issues. /
    """

# Global variables for lazy initialization
_llm = None
_embeddings = None

def get_llm():
    """Lazy initialization of the Groq LLM."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(model_name="llama-3.1-8b-instant")
    return _llm

def get_embeddings_model():
    """Lazy initialization of the Hugging Face Inference API embeddings model."""
    global _embeddings
    if _embeddings is None:
        # Using Inference API to save memory (Render 512MB limit)
        _embeddings = HuggingFaceInferenceAPIEmbeddings(
            api_key=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
            model_name="BAAI/bge-small-en-v1.5"
        )
    return _embeddings

def get_embedding(text_to_embed):
    """
    Generate an embedding for the given text.

    Args:
        text_to_embed (str): The text to generate an embedding for.

    Returns:
        list: The generated embedding vector.
    """
    embeddings = get_embeddings_model()
    response = embeddings.embed_query(text_to_embed)
    print(Fore.YELLOW + "Generated Cloud Embedding")
    return response


# define prompt
system_message_prompt_template = SystemMessagePromptTemplate.from_template(template)
human_message_prompt_template = HumanMessagePromptTemplate.from_template(input_variables=["question", "context"], template ="{question}")

chat_prompt_template = ChatPromptTemplate.from_messages([system_message_prompt_template, human_message_prompt_template])


#indexing - Load and Split the documents using DocumentLoader and TextSplitter
def load_split_documents():
    """ 
    Load a document from a file path and split it into several smaller chunks.

    Returns:
        list[Document]: A list of document chunks.
    """
    raw_text = TextLoader("./docs/faq.txt").load()
    text_splitter = CharacterTextSplitter(chunk_size=30, chunk_overlap=0, separator=".")
    chunks = text_splitter.split_documents(raw_text)
    print(f"Number of chunks: {len(chunks)}")
    return chunks
    
# convert to embeddings - cover the split documents into embeddings (documents are converted into vectors), docuemnts are coming from load_split_documents()
def load_embeddings(documents, user_query):
    """
    Create a vector store from a set of documents and perform a similarity search.

    Args:
        documents (list): The list of document chunks to load into the vector store.
        user_query (str): The user's question to perform a similarity search with.

    Returns:
        VectorStoreRetriever: A retriever object for the vector store.
    """
    db = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings_model(),
        persist_directory="./.chroma_db",
        client_settings=Settings(anonymized_telemetry=False)
    )
    docs = db.similarity_search(user_query, k=2)
    # get_embedding(user_query) # Optional: verify cloud connection
    print(Fore.GREEN + Style.BRIGHT + user_query+ Style.RESET_ALL)
    return db.as_retriever()



def generate_response(retriever, query):
    """
    Generate a response to a user query using a RAG chain.

    Args:
        retriever (VectorStoreRetriever): The retriever to use for fetching context.
        query (str): The user's question.

    Returns:
        str: The generated response from the LLM.
    """
    chain = ( 
        {"context": retriever, "question": RunnablePassthrough() }
        | chat_prompt_template
        | get_llm()
        | StrOutputParser()
    )
    return chain.invoke(query)


def query(query):
    """
    The main entry point for querying the RAG system.

    Args:
        query (str): The user's question.

    Returns:
        str: The generated response.
    """
    documents = load_split_documents()
    retriever = load_embeddings(documents, query)
    return generate_response(retriever, query)
