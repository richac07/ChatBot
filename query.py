import os
os.environ["ANONYMIZED_TELEMETRY"] = "False" # Force disable at the OS level
from langchain_groq import ChatGroq
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
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
It uses Groq for the LLM (for cloud deployment), HuggingFace for embeddings, and ChromaDB for vector storage.
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

# init model - Using Groq for free cloud-based inference
# model possibilities: "llama-3.1-8b-instant", "llama-3.3-70b-versatile"
llm = ChatGroq(model_name="llama-3.1-8b-instant")

# init embeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

def get_embedding(text_to_embed):
    """
    Generate an embedding for the given text.

    Args:
        text_to_embed (str): The text to generate an embedding for.

    Returns:
        list: The generated embedding vector.
    """
    response = embeddings.embed_query(text_to_embed)
    print(response)
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
    print(chunks[0])
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
        embedding=embeddings,
        persist_directory="./.chroma_db",
        client_settings=Settings(anonymized_telemetry=False)
    )
    docs = db.similarity_search(user_query, k=2)
    get_embedding(user_query)
    _ = [get_embedding(doc.page_content) for doc in docs]
    print(Fore.CYAN + f"{_}")  
    # print(f"Retrieved {len(docs)} documents")
    # print(Fore.CYAN + f"Retrieved: {docs[0].page_content}" + Style.RESET_ALL) 
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
        | llm
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
 #   load_split_documents()
    documents = load_split_documents()
    retriever = load_embeddings(documents, query)
    return generate_response(retriever, query)


#query("What is the return policy?")
