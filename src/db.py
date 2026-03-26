import os 
import psycopg2
from dotenv import load_dotenv

load_dotenv()
# Creates Database conncetion to postgresql server. 
def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )