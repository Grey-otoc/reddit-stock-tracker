import re
import requests

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
    
    def __init__(self, subreddit: str, post_count: int):
        self.__subreddit = subreddit
        self.__post_count = post_count
        self.__posts = {}
        
    def fetch_posts(self) -> str:
        params = {"limit": self.__post_count}
        url = f"https://www.reddit.com/r/{self.__subreddit}/new.json"
        
        response_json = requests.get(url, headers=self.HEADERS, params=params, timeout=self.TIMEOUT).json()
        posts = response_json["data"]["children"]
        for post in posts:
            post = post["data"] # removes the need to access "data" with each datapoint
            
            self.__posts[post["id"]] = {
                "title": post["title"], "body": post["selftext"],
                "permalink": post["permalink"], "post_time": post["created_utc"],
                "num_of_comments": post["num_comments"]
            }
        
        for post in self.__posts.values():
            title_and_body = post["title"] + " " + post["body"]
            
            # removes unicode whitespace chars and replaces them with single spaces
            title_and_body = re.sub(r"\s+", " ", title_and_body)
            title_and_body = title_and_body.upper()
            return title_and_body
            