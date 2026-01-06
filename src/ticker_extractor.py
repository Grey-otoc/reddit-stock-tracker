import re

"""
Takes title and body of post/comment and checks for tickers, then validates
those tickers against api, returning valid tickers
"""

class TickerExtractor:
    """
    PATTERN includes all 1-5 letter strings not preceded or succeeded by a 
    number, letter, or apostrophe. PATTERN is also inclusive of certain ticker 
    formats like "BRK.A" or "BRK-A"
    """
    PATTERN = re.compile(r"(?<![A-Z0-9'])[A-Z]{1,5}(?:[.\-=][A-Z]{1,2})?(?![A-Z0-9'])")
    
    def __init__(self, blacklisted_words: list[str]):
        self.__blacklisted_words = blacklisted_words
    
    def extract(self, title_and_body: str) -> list:
        tickers = set([
            ticker for ticker in self.PATTERN.findall(title_and_body)
            if ticker not in self.__blacklisted_words
        ])
        
        return sorted(list(tickers))
 