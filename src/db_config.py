from pathlib import Path
import sqlite3

"""
initialises the database and creates mentions, post_cache and comment_cache
tables if they do not exist
"""

CURRENT_DIR = Path(__file__).resolve()
# even if file is not yet made, establish the path to give to sqlite3
DB_PATH = CURRENT_DIR.parent.parent / "database" / "reddit_ticker_data.db"

def initialise_db():
    # Create the 'database' folder if it doesn't exist, if it does no error raised
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # "reddit_ticker_data.db" file created and/or opened
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker_symbol TEXT NOT NULL,
            subreddit TEXT NOT NULL,
            mention_timestamp REAL NOT NULL
        ) 
    ''')
    
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS post_cache (
            post_id TEXT PRIMARY KEY,
            post_timestamp REAL NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment_cache (
            comment_id TEXT NOT NULL,
            post_id TEXT NOT NULL,
            comment_timestamp REAL NOT NULL,
            PRIMARY KEY (comment_id, post_id)
        )                   
    ''')

    connection.commit()
    connection.close()

def get_db_path() -> Path:
    if not DB_PATH.exists():
        raise FileNotFoundError("Database file not found. Please run initialise_db() first.")

    return DB_PATH

if __name__ == "__main__":
    initialise_db()
