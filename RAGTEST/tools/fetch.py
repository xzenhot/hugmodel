import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma

pdf_path = "D:\\temp\\snowflake.pdf"

raw_texts = [
    "RAG stands for Retrieval-Augmented Generation. It is a technique that improves Large Language Models (LLMs) by providing them with relevant, up-to-date context from an external knowledge base before they generate an answer.",
    "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
    "The Chroma database is an open-source embedding database designed to make it easy to build LLM apps by making knowledge, facts, and skills pluggable for LLMs.",
    "Kubernetes (K8s) is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It handles the heavy lifting of orchestrating containers across a cluster of machines, ensuring high availability, load balancing, and efficient resource utilization."
]

def read_doc():
    docs = [Document(page_content=text) for text in raw_texts]
    # Load from a PDF file if it exists in the same directory

    if os.path.exists(pdf_path):
        pdf_loader = PyPDFLoader(pdf_path)
        pdf_docs = pdf_loader.load()
        docs.extend(pdf_docs)
        print(f"Loaded {len(pdf_docs)} pages from {pdf_path}.")
    else:
        print(f"PDF file '{pdf_path}' not found. Skipping PDF ingestion.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} document chunks.\n")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embedding_model,
        persist_directory="d:\\temp\\chroma_db"
    )
    return vectorstore 


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_retriver():
    vectorstore = read_doc()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return retriever