from db_config import get_db_path
import sqlite3

''''
contains all of the queries used by any part of the backend or UI of the project
'''

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
        print("FATAL ERROR: Failed to retrieve tickers by mention count for dashboard: {e}")
        raise
        
    finally:
        if connection:
            connection.close()
            
def get_mentions_by_ticker(ticker: str):
    connection = None
    
    try:
        connection = sqlite3.connect(get_db_path())
        cursor = connection.cursor()

        cursor.execute('''
            SELECT ticker_symbol, post_id, comment_id, mention_timestamp, subreddit 
            FROM mentions
            WHERE ticker_symbol = ?
            ORDER BY mention_timestamp DESC
        ''', (ticker, )
        )
        
        mentions = cursor.fetchall()
        return mentions
    
    except Exception as e:
        print("FATAL ERROR: Failed to retrieve mentions by ticker for dashboard: {e}")
        raise
    
    finally:
        if connection:
            connection.close()

