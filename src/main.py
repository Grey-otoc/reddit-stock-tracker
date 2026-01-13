from blacklist_loader import load_blacklist_files
from db_config import initialise_db, get_db_path
from scraper import Scraper
import sqlite3
from ticker_extractor import TickerExtractor
from ticker_list_controller import fetch_ticker_list, load_ticker_list_from_csv

POSTS_TO_COLLECT = 5
COMMENTS_TO_COLLECT = 10
SUBREDDITS = ["stocks", "wallstreetbets", "stocks_picks", "value_investing", 
              "stockmarket", "stockstobuytoday"
]
SUBREDDITS_TEST = ["stocks"] 

def boot_sequence():
    initialise_db()
    fetch_ticker_list()
    global BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC
    BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC = load_blacklist_files()

def execute():
    ticker_list = load_ticker_list_from_csv()
    #ticker_str = "I think AAPL is a buy BTW, but ur crazy if you like SIRI right now. I bought some ETF shares for my IRA, LOL. AKA is actually a ticker, unlike aka in this sentence. F is for Ford, not just a grade. PM is pumping but it's 5 pm here."
    
    ticker_extractor = TickerExtractor(BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC, ticker_list)
    ticker_count = 0
    
    for subreddit in SUBREDDITS_TEST:
        scraper = Scraper(subreddit, POSTS_TO_COLLECT, COMMENTS_TO_COLLECT)
        sub_data = scraper.scrape_data()
        for post_or_comment in sub_data:
            tickers = ticker_extractor.extract(post_or_comment.text)
            
            #if tickers:
            ticker_count += len(tickers)
            print(tickers, post_or_comment.post_id, post_or_comment.comment_id, post_or_comment.timestamp)
            print("\n")
            record_mentions(post_or_comment, tickers)
                
    print(f"Recorded {ticker_count} mentions")

def record_mentions(post_or_comment, tickers: set[str]):
    # ensures we don't get an UnboundLocalError if connection in the except block
    connection = None
    
    try:
        connection = sqlite3.connect(get_db_path())
        cursor = connection.cursor()
        
        post_id = post_or_comment.post_id
        comment_id = post_or_comment.comment_id
        timestamp = post_or_comment.timestamp
        subreddit = post_or_comment.subreddit
        
        for ticker in tickers:
            cursor.execute(
                '''SELECT id FROM mentions WHERE post_id = ? AND comment_id IS ? 
                AND ticker_symbol = ?''',
                (post_id, comment_id, ticker)
            )
            cursor_result = cursor.fetchone()
            is_new = cursor_result is None
            
            if is_new:
                cursor.execute(
                    '''INSERT INTO mentions (post_id, comment_id, ticker_symbol,
                    subreddit, mention_timestamp) VALUES (?, ?, ?, ?, ?)''',
                    (post_id, comment_id, ticker, subreddit, timestamp)
                )
            else:
                print("NON-FATAL Error: Scraper returned a previously recorded ScrapedItem")
                
        connection.commit()
        
    except Exception as e:
        print(f"FATAL ERROR: Failed to record ticker mention: {e}")
        
    finally:
        if connection:
            connection.close()
            
if __name__ == "__main__":
    boot_sequence()
    execute()
