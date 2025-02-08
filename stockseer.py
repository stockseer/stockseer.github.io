import os

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup


class Indicators:

    def __init__(self, column='Adj Close'):
        self.column = column

    def calculate_sma(self, data, window=5):
        return data[self.column].rolling(window=window).mean()

    def calculate_ema(self, data, window=5):
        return data[self.column].ewm(span=window, adjust=False).mean()

    def calculate_rsi(self, data, window=7):
        prices = np.array(data[self.column])

        deltas = np.diff(prices)
        gains = np.zeros_like(deltas)
        losses = np.zeros_like(deltas)
        gains[deltas > 0] = deltas[deltas > 0]
        losses[deltas < 0] = -deltas[deltas < 0]

        avg_gain = np.zeros_like(prices)
        avg_loss = np.zeros_like(prices)
        avg_gain[window] = np.mean(gains[:window])
        avg_loss[window] = np.mean(losses[:window])

        for i in range(window + 1, len(prices)):
            avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gains[i - 1]) / window
            avg_loss[i] = (avg_loss[i - 1] * (window - 1) + losses[i - 1]) / window

        rs = avg_gain[window:] / (avg_loss[window:] + 0.1e-10)
        rsi = 100 - (100 / (1 + rs))
        rsi_full = np.full_like(prices, np.nan)
        rsi_full[window:] = rsi
        return rsi_full

    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        short_ema = self.calculate_ema(data, short_window)
        long_ema = self.calculate_ema(data, long_window)
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_window, adjust=False).mean()
        return macd, signal

    def calculate_bollinger_bands(self, data, window=20):
        sma = self.calculate_sma(data, window)
        std_dev = data[self.column].rolling(window=window).std()
        upper_band = sma + (2 * std_dev)
        lower_band = sma - (2 * std_dev)
        bbp = (data[self.column] - lower_band) / (upper_band - lower_band)
        return sma, upper_band, lower_band, bbp


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


class History:

    def __init__(self, folder='stock_data'):
        self.folder = folder
        self.indicators = Indicators()

    def download_stock_data(self, stock_symbols, period='1y'):
        tickers = ' '.join(stock_symbols)
        df = yf.download(tickers=tickers, period=period, interval='1d').dropna(how='all')

        all_data = {}
        os.makedirs(self.folder, exist_ok=True)

        for symbol in df['Adj Close'].columns.tolist():
            data = pd.concat([df['Open'][symbol],
                              df['High'][symbol],
                              df['Low'][symbol],
                              df['Close'][symbol],
                              df['Adj Close'][symbol],
                              df['Volume'][symbol]], axis=1, sort=True).dropna()
            data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            if not data.empty:
                all_data[symbol] = data
                file_path = f"{self.folder}/{symbol}.csv"
                data.to_csv(file_path)
            else:
                print(f"No data available for {symbol}")
        return all_data

    def load_stock_data_from_csv(self, stock_symbols):
        all_stocks = {}
        sell_stocks = {}
        buy_stocks = {}

        if not os.path.exists(self.folder):
            print(f"Folder '{self.folder}' does not exist.")
            return all_stocks, sell_stocks, buy_stocks

        for symbol in stock_symbols:
            file_path = f"{self.folder}/{symbol}.csv"
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                data['SMA_20'] = self.indicators.calculate_sma(data, window=20)
                data['SMA_50'] = self.indicators.calculate_sma(data, window=50)
                data['SMA_200'] = self.indicators.calculate_sma(data, window=200)
                data['RSI_7'] = self.indicators.calculate_rsi(data, window=7)
                data['RSI_14'] = self.indicators.calculate_rsi(data, window=14)
                data['RSI_21'] = self.indicators.calculate_rsi(data, window=21)
                data['RSI_C'] = data['RSI_7'] / data['Adj Close']
                data['MACD'], data['Signal'] = self.indicators.calculate_macd(data)
                data['BB'], data['BBU'], data['BBL'], data['BBP'] = self.indicators.calculate_bollinger_bands(data)
                all_stocks[symbol] = data

                if self.can_sell(data.iloc[-1]):
                    sell_stocks[symbol] = data
                if self.can_buy(data.iloc[-1]):
                    buy_stocks[symbol] = data
            except Exception as e:
                print(f"Failed to load data for {symbol}: {e}")
        return all_stocks, sell_stocks, buy_stocks

    @staticmethod
    def can_sell(data):
        margin = data['BBU'] - data['BBL']
        return data['RSI_7'] >= 80 and data['Adj Close'] >= (data['BBU'] - margin)

    @staticmethod
    def can_buy(data):
        margin = data['BBU'] - data['BBL']
        return data['RSI_7'] <= 20 and data['Adj Close'] <= (data['BBL'] + margin)


class Strategy:

    def __init__(self):
        self.y_usa_stocks = "y_usa_stocks.csv"
        self.tv_usa_stocks = "tv_usa_stocks.csv"
        self.tv_china_stocks = "tv_china_stocks.csv"
        self.screener = Screener()
        self.history = History()

    def download_usa_stocks(self):
        self.screener.scrape_yahoo_most_active_usa_stocks(self.y_usa_stocks)
        self.screener.scrape_tradingview_most_active_usa_stocks(self.tv_usa_stocks)

        symbols = self.load_usa_symbols()
        if symbols:
            self.history.download_stock_data(symbols)

    def load_usa_symbols(self):
        symbols = self.screener.read_symbols_from_csv(self.y_usa_stocks)
        symbols += self.screener.read_symbols_from_csv(self.tv_usa_stocks)
        return list(set(symbols))

    def load_usa_stocks(self):
        symbols = self.load_usa_symbols()
        if symbols:
            return self.history.load_stock_data_from_csv(symbols)
        return {}, {}, {}

    def download_china_stocks(self):
        self.screener.scrape_tradingview_most_active_china_stocks(self.tv_china_stocks)

        symbols = self.load_china_symbols()
        if symbols:
            self.history.download_stock_data(symbols)

    def load_china_symbols(self):
        symbols = self.screener.read_symbols_from_csv(self.tv_china_stocks)
        return [
            s + ".SS" if s.startswith("6") else
            s + ".SZ" if s.startswith(("0", "3")) else
            s
            for s in symbols
        ]

    def load_china_stocks(self):
        symbols = self.load_china_symbols()
        if symbols:
            return self.history.load_stock_data_from_csv(symbols)
        return {}, {}, {}
