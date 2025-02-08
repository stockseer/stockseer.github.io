import os

import pandas as pd
import yfinance as yf

from indicator import Indicator


class History:

    def __init__(self, folder='stock_data'):
        self.folder = folder
        self.indicators = Indicator()

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
