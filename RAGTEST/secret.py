import os
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")
os.environ["POSTGRES_USER"] = os.getenv("POSTGRES_USER")
os.environ["POSTGRES_PASSWORD"] = os.getenv("POSTGRES_PASSWORD")
os.environ["POSTGRES_HOST"] = os.getenv("POSTGRES_HOST")    