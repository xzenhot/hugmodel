
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'