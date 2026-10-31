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
# 1. UPDATED IMPORTS: Fixes the deprecation warnings


# ==========================================
# 1. Ingestion: Load and Split Documents
# ==========================================
raw_texts = [
    "RAG stands for Retrieval-Augmented Generation. It is a technique that improves Large Language Models (LLMs) by providing them with relevant, up-to-date context from an external knowledge base before they generate an answer.",
    "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
    "The Chroma database is an open-source embedding database designed to make it easy to build LLM apps by making knowledge, facts, and skills pluggable for LLMs."
]

docs = [Document(page_content=text) for text in raw_texts]

# Load from a PDF file if it exists in the same directory
pdf_path = "C:\\Users\\pijush\\Downloads\\OK.pdf"
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

# ==========================================
# 2. Embedding & Vector Storage
# ==========================================
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents=splits, 
    embedding=embedding_model,
    persist_directory="./chroma_db1"
)

# ==========================================
# 3. Retrieval Setup
# ==========================================
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# ==========================================
# 4. Generation: Local LLM Setup
# ==========================================
# 2. FIXED CONNECTION: Added base_url to force IPv4 and fix WinError 10049
llm = ChatOllama(
    model="gemma4:e4b", 
    temperature=0,
    base_url="http://127.0.0.1:11434" # Forces IPv4 instead of 'localhost'
)

def test_ollama_connection():
    try:
        response = llm.invoke("Hello, Ollama!")
        print(f"Ollama response: {response}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")



# ==========================================
# 5. Build the RAG Chain
# ==========================================
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def main():
    template = """Answer the question based ONLY on the following context. 
    If the answer is not in the context, say "I don't know".

    Context: {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    queries = [
    "Explain how K8s handles the heavy lifting for container orchestration?",
    "What programming language emphasizes code readability?",
    "Who invented the telephone?", # This should trigger the "I don't know" fallback
    "Explain the difference between Snowflake's traditional warehouse and its Lakehouse capabilities"
    ]

    for query in queries:
        print(f"Q: {query}")
        response = rag_chain.invoke(query)
        print(f"A: {response}\n" + "-"*50)


if __name__ == "__main__":
    main()
