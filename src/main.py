from apscheduler.schedulers.background import BackgroundScheduler
from blacklist_loader import load_blacklist_files
from datetime import datetime
from db_config import initialise_db
from scraper import Scraper
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
    global BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC
    BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC = load_blacklist_files()

def update_tickers():
    print(f"[{datetime.now()}] Updating ticker list from source...")
    fetch_ticker_list()

def execute_scrape():
    print(f"[{datetime.now()}] Starting scrape of {SUBREDDITS}...")
    
    ticker_list = load_ticker_list_from_csv()
    ticker_extractor = TickerExtractor(BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC, ticker_list)
    ticker_count = 0
    
    for subreddit in SUBREDDITS:
        scraper = Scraper(subreddit, POSTS_TO_COLLECT, COMMENTS_TO_COLLECT)
        sub_data = scraper.scrape_data()
        for post_or_comment in sub_data:
            tickers = ticker_extractor.extract(post_or_comment.text)
            
            ticker_count += len(tickers)
            # print(tickers, post_or_comment.post_id, post_or_comment.comment_id, post_or_comment.timestamp)
            # print("\n")
            ticker_extractor.record_mentions(post_or_comment, tickers)

    print(f"[{datetime.now()}] Recorded {ticker_count} mentions.")
            
if __name__ == "__main__":
    boot_sequence()
    execute_scrape()
