from db_config import get_db_path
import re
import requests
import sqlite3

"""
creates a scraper for each subreddit which fetches the 
relevant data of each post and returns the title and body of the post and
its comments
"""

class Scraper:
    """ 
    User-Agent identifies who is making the request to the server to help
    avoid being blocked by Reddit
    
    TIMEOUT (in seconds) ensures script is not left hanging waiting for a response
    """
    HEADERS = {"User-Agent": "reddit-stock-tracker/1.0 (by u/grey-otoc)"}
    TIMEOUT = 5

    def __init__(self, subreddit: str, post_count: int, comments_count: int):
        self.__subreddit = subreddit
        self.__post_count = post_count
        self.__comments_count = comments_count
        
    def scrape_data(self) -> str:
        posts = self.fetch_posts()
        for post in posts:
            # removes the need to access "data" with each post's attributes
            post = post["data"]
            
            # if post is new, we must record it and process its content
            if self.validate_and_record_posts(post):
                title_and_body = post["title"] + " " + post["selftext"]
            
                # removes unicode whitespace chars and replaces them with single spaces
                title_and_body = re.sub(r"\s+", " ", title_and_body)
                title_and_body = title_and_body.upper()
                yield title_and_body
            
            # next, if a comment is new, we must record it and process its content
            # comments = self.fetch_comments(post["id"])
    
    def fetch_posts(self) -> str:
        params = {"limit": self.__post_count}
        url = f"https://www.reddit.com/r/{self.__subreddit}/new.json"
        
        response_json = requests.get(
            url, headers=self.HEADERS, params=params, timeout=self.TIMEOUT
        ).json()
        posts = response_json["data"]["children"]
        
        return posts

    def validate_and_record_posts(self, post: dict):
        connection = sqlite3.connect(get_db_path())
        cursor = connection.cursor()
    
        cursor.execute(
            '''SELECT post_id FROM post_cache WHERE post_id = ?''',
            (post["id"],)
        )
        cursor_result = cursor.fetchone()
        if cursor_result is None:
            # insert the new post
            cursor.execute(
                '''INSERT INTO post_cache (post_id, post_timestamp) VALUES (?, ?)''',
                (post["id"], post["created_utc"])
            )

            # check if we have more than n (desired post_count) entries
            cursor.execute('''SELECT COUNT(*) FROM post_cache''')
            current_count = cursor.fetchone()[0]

            if current_count > self.__post_count:
                # delete the post with the smallest (oldest) timestamp
                cursor.execute('''
                    DELETE FROM post_cache 
                    WHERE post_timestamp = (SELECT MIN(post_timestamp) FROM post_cache)
                ''')
            
            connection.commit()
        
        connection.close()    
        return cursor_result is None
    
    def fetch_comments(self, post_id: str) -> str:
        params = {"limit": self.__comments_count}
        # targets the newest comments on the post but reddit paginates comments 
        # and inserts "more" objects after nondescript amounts of comments, so
        # we may not get the comments_count amount of comments, limit, depth,
        # and context parameters do not help with this
        url = f"https://www.reddit.com/r/stocks/comments/{post_id}/.json?sort=new&depth=1"
        
        response_json = requests.get(
            url, headers=self.HEADERS, params=params, timeout=self.TIMEOUT
        ).json()
        comments = response_json[1]["data"]["children"]
        print(len(comments))
        for comment in comments:
            comment = comment["data"]
            print(comment)
            print("\n\n")
            
if __name__ == "__main__":
    scraper = Scraper("stocks", 10, 6)
    #scraper.scrape_data()
    scraper.fetch_comments("1q5y4r5")

# self.__posts[post["id"]] = {
#     "title": post["title"], "body": post["selftext"],
#     "permalink": post["permalink"], "post_time": post["created_utc"],
#     "num_of_comments": post["num_comments"]
# }
