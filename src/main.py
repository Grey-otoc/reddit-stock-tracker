from blacklist_loader import load_blacklist_files
from db_config import initialise_db
from scraper import Scraper
from ticker_extractor import TickerExtractor
from ticker_list_controller import fetch_ticker_list, load_ticker_list_from_csv

POSTS_TO_COLLECT = 10
COMMENTS_TO_COLLECT = 10
SUBREDDITS = ["stocks", "wallstreetbets", "stocks_picks", "value_investing", 
              "stockmarket", "stockstobuytoday"
]
SUBREDDITS_TEST = ["stocks"] 

def boot_sequence():
    initialise_db()
    fetch_ticker_list()

def execute():
    blacklisted_words, common_words = load_blacklist_files()
    ticker_list = load_ticker_list_from_csv()
    #ticker_str = "I'm thinking of buying BRK.B and JW-A today. I know AAPL's price is high, but it is better than CAN. Most people think TSLA is a car company, but don't I've aren't AREN'Ttsla is really an AI play. Also, check out RAC/WS—I hope it doesn't GAP down like GME did."
    
    ticker_extractor = TickerExtractor(blacklisted_words, common_words, ticker_list)
    # print(ticker_extractor.extract(ticker_str))
    for subreddit in SUBREDDITS_TEST:
        scraper = Scraper(subreddit, POSTS_TO_COLLECT, COMMENTS_TO_COLLECT)
        sub_data = scraper.scrape_data()
        for i in range(6):
            print(ticker_extractor.extract(next(sub_data)))
    
if __name__ == "__main__":
    boot_sequence()
    execute()
