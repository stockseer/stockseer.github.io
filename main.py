import pandas as pd

from strategy import Strategy


def save_to_csv(sell, buy, file_name):
    if len(sell) > len(buy):
        buy += [None] * (len(sell) - len(buy))
    if len(sell) < len(buy):
        sell += [None] * (len(buy) - len(sell))
    df = pd.DataFrame({
        'SELL': sell,
        'BUY': buy
    })
    df.to_csv(file_name, index=False)


strategy = Strategy()
strategy.download_usa_stocks()
strategy.download_china_stocks()
strategy.download_portfolio_stocks()

_, sell_usa, buy_usa = strategy.load_usa_stocks()
save_to_csv(list(sell_usa.keys()), list(buy_usa.keys()), "usa_stocks.csv")
_, sell_china, buy_china = strategy.load_china_stocks()
save_to_csv(list(sell_china.keys()), list(buy_china.keys()), "china_stocks.csv")
_, sell_portfolio, buy_portfolio = strategy.load_portfolio_stocks()
save_to_csv(list(sell_portfolio.keys()), list(buy_portfolio.keys()), "portfolio_stocks.csv")
