import re

"""
Takes title and body of post/comment and checks for tickers, then validates
those tickers against api, returning valid tickers
"""

class TickerExtractor:
    """
    PATTERN includes all 1-5 letter strings not preceded or succeeded by a 
    number, letter, or apostrophe. PATTERN is also inclusive of certain ticker 
    formats like "BRK.A", "BRK/A", etc. I include words succeeded by an apostrophe
    to avoid missing tickers in possessive form, z.b. "I like AAPL's products."
    """
    PATTERN = re.compile(r"(?<![a-zA-Z0-9'’])[a-zA-Z]{1,5}(?:[./-^][a-zA-Z]{1,2})?(?![a-zA-Z0-9])")
    
    def __init__(self, blacklisted_words: set[str], common_words: set[str], ticker_list: set[str]):
        self.__blacklisted_words = blacklisted_words
        self.__common_words = common_words
        self.__ticker_list = ticker_list
    
    def extract(self, content: str) -> set: 
        raw_matches = self.PATTERN.findall(content)
        valid_tickers = set()
        
        for word in raw_matches:
            # normalise potential ticker formats to match those in our own ticker list
            normalised_word = word.replace('.', '/').replace('-', '/')
            upper_word = normalised_word.upper()
            
            if upper_word in self.__blacklisted_words:
                continue
            
            if upper_word in self.__ticker_list:
                # only accept a common word if it's fully uppercase, otherwise
                # just skip it
                if upper_word in self.__common_words:
                    if word.isupper():
                        valid_tickers.add(upper_word)
                else:
                    valid_tickers.add(upper_word)

        return valid_tickers
