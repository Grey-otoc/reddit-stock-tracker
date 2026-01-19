from db_config import get_db_path
import sqlite3

def grab_posts():
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM post_cache')
    posts = cursor.fetchall()
    for post in posts:
        print(post)
    
    connection.close()

def grab_comments():
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM comment_cache')
    comments = cursor.fetchall()
    for comment in comments:
        print(comment)
        
    connection.close()

def clear_all_tables():
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()
    
    cursor.execute('DELETE FROM post_cache')
    cursor.execute('DELETE FROM comment_cache')
    cursor.execute('DELETE FROM mentions')
    
    connection.commit()
    connection.close()

def get_mentions_by_ticker(ticker: str):
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()

    cursor.execute('''
        SELECT ticker_symbol, post_id, comment_id, mention_timestamp, subreddit 
        FROM mentions
        WHERE ticker_symbol = ?
        ORDER BY mention_timestamp DESC
    ''', (ticker, )
    )
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"${row[0]} mentioned in post {row[1]}, comment {row[2]} in {row[4]} at {row[3]}")
    
    connection.close()

def get_mentions_by_subreddit(subreddit: str):
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()
    
    # Selecting columns and ordering by the newest timestamp
    cursor.execute('''
        SELECT ticker_symbol, post_id, comment_id, mention_timestamp, subreddit 
        FROM mentions
        WHERE subreddit = ?
        ORDER BY mention_timestamp DESC
    ''', (subreddit, )
    )
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"${row[0]} mentioned in post {row[1]}, comment {row[2]} at {row[3]}")
    
    connection.close()

def get_recent_mentions(limit: int = 10):
    connection = sqlite3.connect(get_db_path())
    cursor = connection.cursor()
    
    # Selecting columns and ordering by the newest timestamp
    cursor.execute('''
        SELECT ticker_symbol, post_id, comment_id, mention_timestamp, subreddit 
        FROM mentions 
        ORDER BY mention_timestamp DESC
        LIMIT ?
    ''', (limit,)
    )
    
    rows = cursor.fetchall()
    for row in rows:
        print(f"${row[0]} mentioned in post {row[1]}, comment {row[2]} in {row[4]} at {row[3]}")
    
    connection.close()
    
def get_tickers_by_mention_count(mentions_since: float) -> set[str]:
    connection = None
    
    try:
        connection = sqlite3.connect(get_db_path())
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT ticker_symbol, COUNT(ticker_symbol) as mention_count
            FROM mentions WHERE mention_timestamp > ? GROUP BY ticker_symbol
            ORDER BY mention_count DESC''', (mentions_since,)
        )
        
        ranked_tickers = cursor.fetchall()
        
        return ranked_tickers
        
    except Exception as e:
        print("FATAL ERROR: Failed to retrieve tickers for dashboard: {e}")
        raise
        
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    cmd = input(
        "1: posts, 2: comments, 3: clear all tables, 4: get recent mentions,"
        "5: get ranked tickers, 6: get mentions by sub, 7: get mentions by ticker:  "
    )
    
    if cmd == "1":
        grab_posts()
    elif cmd == "2":
        grab_comments()
    elif cmd == "3":
        clear_all_tables()
    elif cmd == "4":
        get_recent_mentions()
    elif cmd == "5":
        ranked_tickers = get_tickers_by_mention_count(1768421001.0)
        for ticker in ranked_tickers:
            print(f"{ticker[0]} mentioned {ticker[1]} times")
    elif cmd == "6":
        subreddit = input("Subreddit: ")
        get_mentions_by_subreddit(subreddit)
    elif cmd == "7":
        ticker = input("Ticker: ")
        get_mentions_by_ticker(ticker)
