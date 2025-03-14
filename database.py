
import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv
import uuid

load_dotenv()

# Initialize connection pool
db_pool = SimpleConnectionPool(1, 10, os.getenv('DATABASE_URL'))

def init_db():
    """Initialize database tables"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    id SERIAL PRIMARY KEY,
                    cache_id UUID NOT NULL,
                    user_token UUID,
                    api_path TEXT NOT NULL,
                    response TEXT NOT NULL,
                    is_predefined BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
    finally:
        db_pool.putconn(conn)

def store_cache(user_token: str, api_path: str, response: str, is_predefined: bool = False):
    """Store cache entry"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO api_cache (cache_id, user_token, api_path, response, is_predefined)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING cache_id
                """,
                (uuid.uuid4(), user_token, api_path, response, is_predefined)
            )
            result = cur.fetchone()
            conn.commit()
            return result[0]
    finally:
        db_pool.putconn(conn)

def get_cache(user_token: str, api_path: str):
    """Get cache entry"""
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT response
                FROM api_cache
                WHERE (user_token = %s OR is_predefined = true)
                AND api_path = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (user_token, api_path)
            )
            result = cur.fetchone()
            return result[0] if result else None
    finally:
        db_pool.putconn(conn)
