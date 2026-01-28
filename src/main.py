from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR
from blacklist_loader import load_blacklist_files
from datetime import datetime, time
from db_config import initialise_db
import os
from scraper import Scraper
from ticker_extractor import TickerExtractor
from ticker_list_controller import fetch_ticker_list, load_ticker_list_from_csv

POSTS_TO_COLLECT = 5
COMMENTS_TO_COLLECT = 10
SUBREDDITS = [
    "stocks", "wallstreetbets", "stocks_picks", "ValueInvesting", 
    "stockmarket", "stockstobuytoday"
]
SCRAPER_EXTRACTOR_DELAY = 30    # minute(s)
TICKER_LIST_UPDATER_DELAY = 1   # day(s)

def boot_sequence():
    initialise_db()
    global BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC
    BLACKLISTED_WORDS, REGULAR_WORDS, RANDOM_WORDS_DC = load_blacklist_files()

def update_ticker_list():
    print(f"[{datetime.now()}] Updating ticker list...")
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
            # print(
            #     tickers, post_or_comment.post_id, post_or_comment.comment_id, 
            #     post_or_comment.subreddit, post_or_comment.timestamp
            # )
            
            if tickers:
                ticker_count += len(tickers)
                ticker_extractor.record_mentions(post_or_comment, tickers)

    print(f"[{datetime.now()}] Successfully recorded {ticker_count} mentions.")
    
def crash_on_error(event):
    '''
    ensures that any fatal error within the scheduled jobs will crash the program
    as expected
    '''
    if event.exception:
        # prints the specific error that happened inside the job
        print(f"\n[{datetime.now()}] JOB FATAL ERROR: {event.job_id}")
        print(event.traceback)
        
        os._exit(1)

def start_scheduler():
    scheduler = BlockingScheduler()
    
    scheduler.add_listener(crash_on_error, EVENT_JOB_ERROR)
    
    # run immediately on start to ensure ticker list is available before scraper
    # ever starts
    update_ticker_list()
    
    scheduler.add_job(
        update_ticker_list, 
        'interval', 
        days=TICKER_LIST_UPDATER_DELAY,
        id='ticker_update',
        replace_existing=True
    )

    scheduler.add_job(
        execute_scrape, 
        'interval', 
        minutes=SCRAPER_EXTRACTOR_DELAY, 
        next_run_time=datetime.now(),
        id='subreddit_scrape',
        replace_existing=True
    )

    try:
        scheduler.start()
        
    except (KeyboardInterrupt, SystemExit):
        print("\nShutting down...")
        scheduler.shutdown()
        
    except Exception as e:
        print(f"Unexpected error: {e}. Shutting down...")
            
if __name__ == "__main__":
    boot_sequence()
    start_scheduler()
    # update_ticker_list()
    # execute_scrape()
        