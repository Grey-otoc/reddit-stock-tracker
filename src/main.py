from blacklist_loader import load_blacklist_files
from db_config import initialise_db
from scraper import Scraper
from ticker_extractor import TickerExtractor

posts_to_collect = 10
comments_to_collect = 10

def boot_sequence():
    initialise_db()

def execute():
    blacklisted_words = load_blacklist_files()
    scraper = Scraper("stocks", posts_to_collect, comments_to_collect)
    ticker_extractor = TickerExtractor(blacklisted_words)
    post_data = scraper.scrape_data()
    print(ticker_extractor.extract(post_data))
    
if __name__ == "__main__":
    boot_sequence()
    execute()
