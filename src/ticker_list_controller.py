import csv
from pathlib import Path
import requests

CURRENT_DIR = Path(__file__).resolve()
TICKERS_PATH = CURRENT_DIR.parent.parent / "tickers"

# Nasdaq blocks basic requests calls, so we must mimic a browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/"
}

#TIMEOUT (in seconds) ensures script is not left hanging waiting for a response
TIMEOUT = 5

# API endpoint for https://www.nasdaq.com/market-activity/stocks/screener page,
# found via inspecting network requests and filtering for API calls, includes
# all NYSE, NASDAQ, and AMEX listed stocks
URL = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=0&download=true"
FILE_NAME = "ticker_list.csv"

def fetch_ticker_list():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=TIMEOUT)
        # raises an HTTPError if the response was unsuccessful (400 or 500 codes)
        response.raise_for_status()
        response_json = response.json()

        ticker_rows = response_json["data"]["rows"]
        if not ticker_rows:
            raise ValueError("Received an empty ticker list from Nasdaq API")

        # extract just the symbols
        tickers = [ticker["symbol"] for ticker in ticker_rows]
        load_ticker_list_into_csv(tickers)

        print(f"Successfully retrieved and saved {len(tickers)} tickers.")

    except Exception as e:
        print(f"FATAL ERROR: Failed to retrieve tickers: {e}")
        raise

def load_ticker_list_into_csv(tickers: list[str]):
    try:
        TICKERS_PATH.mkdir(parents=True, exist_ok=True)
        ticker_list_file = TICKERS_PATH / "ticker_list.csv"
        
        with open(ticker_list_file, 'w', newline='') as tickers_csv:
            writer = csv.writer(tickers_csv)
            writer.writerow(["Ticker Symbol"])
            writer.writerows([[ticker] for ticker in tickers])

    except Exception as e:
        print(f"FATAL ERROR: Could not save tickers to CSV: {e}")
        raise
    
def load_ticker_list_from_csv() -> set:
    try:
        ticker_list_file = TICKERS_PATH / "ticker_list.csv"
        tickers = set()

        with open(ticker_list_file, "r", newline='') as tickers_csv:
            reader = csv.reader(tickers_csv)
            # skip header row
            next(reader)
            
            for row in reader:
                ticker = row[0]
                tickers.add(ticker)
                
        return sorted(tickers)
    
    except Exception as e:
        print(f"FATAL ERROR: Could not load tickers from CSV: {e}")
        raise

if __name__ == "__main__":
    #fetch_ticker_list()
    tickers = load_ticker_list_from_csv()
    for _ in range(20):
        print(tickers.pop())
