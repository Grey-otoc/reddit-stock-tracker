from blacklist_loader import load_blacklist_files
from scraper import Scraper
from ticker_extractor import TickerExtractor

blacklisted_words = load_blacklist_files()

def execute():
    scraper = Scraper("stocks", 10)
    ticker_extractor = TickerExtractor(blacklisted_words)
    post_data = scraper.fetch_posts()
    print(ticker_extractor.extract(post_data))

execute()
