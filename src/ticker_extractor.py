from db_config import get_db_path
import sqlite3
import re

"""
takes title and body of post/comment and checks for tickers, then validates
those tickers against NASDAQ ticker list, returning valid tickers

also handles the recording of valid ticker mentions into the db's mentions table
"""

class TickerExtractor:
    """
    PATTERN includes all 1-5 letter strings not preceded or succeeded by a 
    number, letter, or apostrophe. PATTERN is also inclusive of certain ticker 
    formats like "BRK.A", "BRK/A", etc. I include words succeeded by an apostrophe
    to avoid missing tickers in possessive form, z.b. "I like AAPL's products."
    """
    PATTERN = re.compile(r"(?<![a-zA-Z0-9'’&])[a-zA-Z]{1,5}(?:[./-^][a-zA-Z]{1,2})?(?![a-zA-Z0-9&])")
    
    def __init__(self, blacklisted_words: set[str], regular_words: set[str], random_words_dc: set[str], ticker_list: set[str]):
        self.__blacklisted_words = blacklisted_words
        self.__regular_words = regular_words
        self.__random_words_dc = random_words_dc
        self.__ticker_list = ticker_list
    
    def extract(self, content: str) -> set[str]:
        match_count = 0
        raw_matches = self.PATTERN.findall(content)
        valid_tickers = set()
        
        for word in raw_matches:
            # normalise potential ticker formats to match those in our own ticker list
            normalised_word = word.replace('.', '/').replace('-', '/')
            upper_word = normalised_word.upper()
            
            if upper_word in self.__blacklisted_words:
                continue
            
            if upper_word in self.__ticker_list:
                # only accept a regular or random_dc word ticker if it's fully uppercase,
                # otherwise just skip it, logic here is that if user meant the ticker,
                # they would likely write it in all caps to distinguish it since the
                # word is either a regular word or commonly lowercased abbreviation/slang
                if upper_word in self.__regular_words or upper_word in self.__random_words_dc:
                    if word.isupper():
                        valid_tickers.add(upper_word)
                else:
                    valid_tickers.add(upper_word)

        return valid_tickers
    
    def record_mentions(self, post_or_comment, tickers: set[str]):
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
                    print("NON-FATAL Error: Scraper returned a previously recorded " 
                          f"ScrapedItem from {subreddit}\npost id: {post_id} and "
                          f"comment id: {comment_id}")
                    
            connection.commit()
            
        except Exception as e:
            print(f"FATAL ERROR: Failed to record ticker mention: {e}")
            
        finally:
            if connection:
                connection.close()
        