from history import History
from screener import Screener


class Strategy:

    def __init__(self):
        self.y_usa_stocks = "stock_data/symbols/y_usa_stocks.csv"
        self.tv_usa_stocks = "stock_data/symbols/tv_usa_stocks.csv"
        self.tv_china_stocks = "stock_data/symbols/tv_china_stocks.csv"
        self.portfolio_stocks = "stock_data/symbols/portfolio_stocks.csv"
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

    def download_portfolio_stocks(self):
        symbols = self.load_portfolio_symbols()
        if symbols:
            return self.history.download_stock_data(symbols)

    def load_portfolio_symbols(self):
        symbols = self.screener.read_symbols_from_csv(self.portfolio_stocks)
        return list(set(symbols))

    def load_portfolio_stocks(self):
        symbols = self.load_portfolio_symbols()
        if symbols:
            return self.history.load_stock_data_from_csv(symbols)
        return {}, {}, {}
