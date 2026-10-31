import os
from langchain_ollama import ChatOllama

LLM = ChatOllama(
    model="gemma4:e4b", 
    temperature=0,
    base_url="http://127.0.0.1:11434" # Forces IPv4 instead of 'localhost'
)

def test_ollama_connection():
    try:
        response = LLM.invoke("Hello, Ollama!")
        print(f"Ollama response: {response}")
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")

