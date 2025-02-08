import pandas as pd
import requests
from bs4 import BeautifulSoup


class Screener:

    def __init__(self, column='Symbol'):
        self.column = column

    def scrape_most_active_stocks(self, url, element, attributes, file_name):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find_all(element, attributes)
            if table:
                symbol_list = [item.contents[0].strip() for item in table]
                df = pd.DataFrame(symbol_list, columns=[self.column])
                df.to_csv(file_name, index=False)
        except Exception as e:
            print(f"Error scraping data: {e}")

    def scrape_yahoo_most_active_usa_stocks(self, file_name):
        url = "https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=100"
        element = 'span'
        attributes = {'class': 'symbol yf-1m808gl'}
        return self.scrape_most_active_stocks(url, element, attributes, file_name)

    def scrape_tradingview_most_active_usa_stocks(self, file_name):
        url = "https://www.tradingview.com/markets/stocks-usa/market-movers-active/"
        element = 'a'
        attributes = {'class': 'tickerNameBox-GrtoTeat'}
        return self.scrape_most_active_stocks(url, element, attributes, file_name)

    def scrape_tradingview_most_active_china_stocks(self, file_name):
        url = "https://www.tradingview.com/markets/stocks-china/market-movers-active/"
        element = 'a'
        attributes = {'class': 'tickerNameBox-GrtoTeat'}
        return self.scrape_most_active_stocks(url, element, attributes, file_name)

    def read_symbols_from_csv(self, file_name):
        try:
            df = pd.read_csv(file_name, dtype=str)
            if self.column not in df.columns:
                raise ValueError(f"Column '{self.column}' not found in the CSV file.")
            return df[self.column].tolist()
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []
