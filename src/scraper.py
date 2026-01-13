from dataclasses import dataclass
from pydoc import text
from typing import Optional
from db_config import get_db_path
import re
import requests
import sqlite3

"""
creates a scraper for each subreddit which fetches the relevant data of each post
and comment found, implements and maintains a sliding-window cache of recent posts and
comments, and returns the post and comment content to be processed for tickers 
"""

@dataclass
class ScrapedItem:
    text: str
    post_id: str
    timestamp: int
    subreddit: str
    comment_id: Optional[str] = None

class Scraper:
    #User-Agent identifies who is making the request to the server to help
    #avoid being blocked by Reddit
    HEADERS = {"User-Agent": "reddit-stock-tracker/1.0 (by u/grey-otoc)"}
    
    #TIMEOUT (in seconds) ensures script is not left hanging waiting for a response
    TIMEOUT = 5

    def __init__(self, subreddit: str, post_count: int, comments_count: int):
        self.__subreddit = subreddit
        self.__post_count = post_count
        self.__comments_count = comments_count
        
    def scrape_data(self) -> dict:
        posts = self.fetch_posts()
        for post in posts:
            # if post is new, we must record it and process its content
            if self.validate_and_record_posts(post):
                title_and_body = post["title"] + " " + post["selftext"]
            
                # removes URLs to avoid false positives from ticker-like strings within URLs
                title_and_body = re.sub(r"http\S+|www\S+|https\S+", "", title_and_body)
                # removes unicode whitespace chars and replaces them with single spaces
                title_and_body = re.sub(r"\s+", " ", title_and_body)

                yield ScrapedItem(text=title_and_body, post_id=post["id"],
                                  timestamp=post["created_utc"], 
                                  subreddit=self.__subreddit
                )
                #yield "POST"
            
            # next, if a comment is new, we must record it and process its content
            comments = self.fetch_comments(post["id"])
            for comment in comments:
                if comment["author"] == "AutoModerator":
                    continue
                
                if self.validate_and_record_comments(comment, post["id"]):
                    comment_body = comment["body"]
                    # removes URLs to avoid false positives from ticker-like strings within URLs
                    comment_body = re.sub(r"http\S+|www\S+|https\S+", "", comment_body)
                    comment_body = re.sub(r"\s+", " ", comment_body)
                    
                    yield ScrapedItem(text=comment_body, post_id=post["id"],
                                      comment_id=comment["id"],
                                      timestamp=comment["created_utc"],
                                      subreddit=self.__subreddit
                    )
                    #yield f"COMMENT {post["id"]}"
    
    def fetch_posts(self) -> list:
        try:
            params = {"limit": self.__post_count}
            url = f"https://www.reddit.com/r/{self.__subreddit}/new.json"
            
            response = requests.get(
                url, headers=self.HEADERS, params=params, timeout=self.TIMEOUT
            )
            # raises an HTTPError if the response was unsuccessful (400 or 500 codes)
            response.raise_for_status()
            response_json = response.json()
            
            posts = response_json["data"]["children"]
            # removes the need to access "data" with each post
            posts = [post["data"] for post in posts]

            return posts
        
        except Exception as e:
            print(f"FATAL ERROR: Failed to fetch posts from r/{self.__subreddit}: {e}")
            raise

    def validate_and_record_posts(self, post: dict) -> bool:
        """ 
        same logic applies to validate_and_record_comments method below:
        checks if post or comment is already in the db, if not, inserts it,
        then checks if we have exceeded the desired count, and if so deletes
        the oldest entry to maintain a sliding-window cache...every time we scrape
        the subreddit, we only check the n (post_count) newest posts and m (comments_count)
        newest comments on each post, so we only need to retain the n most recent
        posts and m most recent comments per post in the db
        """
        
        # ensures we don't get an UnboundLocalError in the except block
        connection = None
        
        try:
            post_id = post["id"]
            connection = sqlite3.connect(get_db_path())
            cursor = connection.cursor()
        
            cursor.execute(
                '''SELECT post_id FROM post_cache WHERE post_id = ?''',
                (post_id,)
            )
            cursor_result = cursor.fetchone()
            is_new = cursor_result is None
            
            if is_new:
                # insert the new post
                cursor.execute(
                    '''INSERT INTO post_cache (post_id, post_timestamp) VALUES (?, ?)''',
                    (post_id, post["created_utc"])
                )

                # check if we have more than n (desired post_count) entries in the db
                cursor.execute('''SELECT COUNT(*) FROM post_cache''')
                current_post_count = cursor.fetchone()[0]

                if current_post_count > self.__post_count:
                    # delete the post with the smallest (oldest) timestamp
                    cursor.execute('''
                        DELETE FROM post_cache 
                        WHERE post_timestamp = (SELECT MIN(post_timestamp) FROM post_cache)
                    ''')
                
                connection.commit()
            
            return is_new
        
        except Exception as e:
            print(
                f"FATAL ERROR: Failed to validate/record post {post_id} "
                f"in r/{self.__subreddit}: {e}"
            )
            if connection:
                connection.rollback()
            raise
        
        finally:
            if connection:
                connection.close()
    
    def fetch_comments(self, post_id: str) -> list:
        try:
            params = {"limit": self.__comments_count}
            # targets the newest comments on the post but reddit paginates comments 
            # and inserts "more" objects after a nondescript amounts of comments, this
            # means we may not get the comments_count amount of comments -- limit, depth,
            # and context parameters do not help with this
            url = f"https://www.reddit.com/r/{self.__subreddit}/comments/{post_id}/.json?sort=new&depth=1"
            
            response = requests.get(
                url, headers=self.HEADERS, params=params, timeout=self.TIMEOUT
            )
            # raises an HTTPError if the response was unsuccessful (400 or 500 codes)
            response.raise_for_status()
            response_json = response.json()
            
            comments = response_json[1]["data"]["children"]

            # filters out "more" objects to ensure we only access actual comments
            actual_comments = [comm["data"] for comm in comments if comm["kind"] == "t1"]
            
            return actual_comments
        
        except Exception as e:
            print(
                f"FATAL ERROR: Failed to fetch comments for post {post_id} in "
                "r/{self.__subreddit}: {e}"
            )
            raise
        
    def validate_and_record_comments(self, comment: dict, post_id: str) -> bool:
        #ensures we don't get an UnboundLocalError in the except block 
        connection = None
        
        try:
            comment_id = comment["id"]
            connection = sqlite3.connect(get_db_path())
            cursor = connection.cursor()
            
            cursor.execute(
                '''SELECT 1 FROM comment_cache WHERE comment_id = ? AND post_id = ?''', 
                (comment_id, post_id)
            )
            cursor_result = cursor.fetchone()
            is_new = cursor_result is None

            if is_new:
                cursor.execute(
                    '''INSERT INTO comment_cache (comment_id, post_id, comment_timestamp)
                    VALUES (?, ?, ?)''', (comment_id, post_id, comment["created_utc"])
                )
                
                cursor.execute(
                    '''SELECT COUNT(*) FROM comment_cache WHERE post_id = ?''',
                    (post_id,)
                )
                current_comment_count = cursor.fetchone()[0]

                if current_comment_count > self.__comments_count:
                    # delete the comment with the smallest (oldest) timestamp
                    cursor.execute(
                        '''DELETE FROM comment_cache WHERE post_id = ? 
                        AND comment_timestamp = (SELECT MIN(comment_timestamp) 
                        FROM comment_cache WHERE post_id = ?)''',
                        (post_id, post_id)
                    )

                connection.commit()

            return is_new
    
        except Exception as e:
            print(
                f"FATAL ERROR: Failed to validate/record comment {comment_id} "
                f"for post {post_id} in r/{self.__subreddit}: {e}"
            )
            if connection:
                connection.rollback()
            raise
        
        finally:
            if connection:
                connection.close()

if __name__ == "__main__":
    scraper = Scraper("stocks", 10, 6)
    data = scraper.scrape_data()
    for _ in range (2):
        dat = next(data)
        print(dat.text)
        print(dat.post_id, dat.comment_id, dat.timestamp, dat.subreddit)
        print("\n\n")
    #     print(post_or_comment)
    #     print("\n\n")
    # # scraper.fetch_comments("1q5y4r5")
