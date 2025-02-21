import os

import pandas as pd
import yfinance as yf

from indicator import Indicator


class History:

    def __init__(self, folder='stock_data'):
        self.folder = folder
        self.indicators = Indicator()

    def download_stock_data(self, stock_symbols, period='3mo'):
        tickers = ' '.join(stock_symbols)
        df = yf.download(tickers=tickers, period=period, interval='1d').dropna(how='all')

        all_data = {}
        os.makedirs(self.folder, exist_ok=True)

        for symbol in df['Close'].columns.tolist():
            data = pd.concat([df['Open'][symbol],
                              df['High'][symbol],
                              df['Low'][symbol],
                              df['Close'][symbol],
                              df['Volume'][symbol]], axis=1, sort=True).dropna()
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not data.empty:
                all_data[symbol] = data
                file_path = f'{self.folder}/{symbol}.csv'
                data.to_csv(file_path)
            else:
                print(f'No data available for {symbol}')
        return all_data

    def load_stock_data_from_csv(self, stock_symbols):
        all_stocks = {}
        sell_stocks = {}
        buy_stocks = {}

        if not os.path.exists(self.folder):
            print(f'Folder "{self.folder}" does not exist.')
            return all_stocks, sell_stocks, buy_stocks

        for symbol in stock_symbols:
            file_path = f'{self.folder}/{symbol}.csv'
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                data['RSI'] = self.indicators.calculate_rsi(data, window=6)
                _, _, _, data['BBP'] = self.indicators.calculate_bollinger_bands(data, window=20)
                all_stocks[symbol] = data

                if self.can_sell(data.iloc[-1], 70, 0.9):
                    sell_stocks[symbol] = data
                if self.can_buy(data.iloc[-1], 30, 0.1):
                    buy_stocks[symbol] = data
            except Exception as e:
                print(f'Failed to load data for {symbol}: {e}')

        sell_stocks_keys = sorted(sell_stocks, key=lambda x: sell_stocks[x].iloc[-1]['RSI'], reverse=True)
        sell_stocks = {k: sell_stocks[k] for k in sell_stocks_keys}
        buy_stocks_keys = sorted(buy_stocks, key=lambda x: buy_stocks[x].iloc[-1]['RSI'])
        buy_stocks = {k: buy_stocks[k] for k in buy_stocks_keys}
        return all_stocks, sell_stocks, buy_stocks

    @staticmethod
    def can_sell(data, rsi, bbp):
        return data['RSI'] >= rsi and data['BBP'] >= bbp

    @staticmethod
    def can_buy(data, rsi, bbp):
        return data['RSI'] <= rsi and data['BBP'] <= bbp
