import os
import warnings
from colorama import Fore, Style, init
from dotenv import load_dotenv

"""
This module provides a Retrieval-Augmented Generation (RAG) system for customer support.
Optimized for ultra-fast startup on Render by using lazy imports.
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
_chat_prompt_template = None

def get_chat_prompt_template():
    """Lazy initialization of the chat prompt template."""
    global _chat_prompt_template
    if _chat_prompt_template is None:
        from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
        system_message_prompt_template = SystemMessagePromptTemplate.from_template(template)
        human_message_prompt_template = HumanMessagePromptTemplate.from_template(input_variables=["question", "context"], template ="{question}")
        _chat_prompt_template = ChatPromptTemplate.from_messages([system_message_prompt_template, human_message_prompt_template])
    return _chat_prompt_template

def get_llm():
    """Lazy initialization of the Groq LLM."""
    global _llm
    if _llm is None:
        from langchain_groq import ChatGroq
        _llm = ChatGroq(model_name="llama-3.1-8b-instant")
    return _llm

def get_embeddings_model():
    """Lazy initialization of the Hugging Face Inference API embeddings model."""
    global _embeddings
    if _embeddings is None:
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        _embeddings = HuggingFaceEndpointEmbeddings(
            api_key=os.environ.get("HUGGINGFACEHUB_API_TOKEN"),
            model_name="BAAI/bge-small-en-v1.5"
        )
    return _embeddings

def get_embedding(text_to_embed):
    """
    Generate an embedding for the given text.
    """
    embeddings = get_embeddings_model()
    response = embeddings.embed_query(text_to_embed)
    print(Fore.YELLOW + "Generated Cloud Embedding")
    return response

def load_split_documents():
    """ 
    Load and split the FAQ document.
    """
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import CharacterTextSplitter
    
    raw_text = TextLoader("./docs/faq.txt").load()
    text_splitter = CharacterTextSplitter(chunk_size=30, chunk_overlap=0, separator=".")
    chunks = text_splitter.split_documents(raw_text)
    return chunks
    
def load_embeddings(documents, user_query):
    """
    Create a vector store and return a retriever.
    """
    from langchain_community.vectorstores import Chroma
    from chromadb.config import Settings
    
    db = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings_model(),
        client_settings=Settings(anonymized_telemetry=False)
    )
    print(Fore.GREEN + Style.BRIGHT + user_query + Style.RESET_ALL)
    return db.as_retriever()

def generate_response(retriever, query_text):
    """
    Generate a response using the RAG chain.
    """
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    
    chain = ( 
        {"context": retriever, "question": RunnablePassthrough() }
        | get_chat_prompt_template()
        | get_llm()
        | StrOutputParser()
    )
    return chain.invoke(query_text)

def query(query_text):
    """
    Main entry point for querying the RAG system.
    """
    documents = load_split_documents()
    retriever = load_embeddings(documents, query_text)
    return generate_response(retriever, query_text)
