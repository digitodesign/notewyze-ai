import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def drop_all_tables():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # Drop all tables
    tables = ['questions', 'quizzes', 'recordings', 'users', 'alembic_version']
    for table in tables:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"Dropped table {table}")
        except Exception as e:
            print(f"Error dropping {table}: {str(e)}")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    drop_all_tables()
