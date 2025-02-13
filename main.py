import pandas as pd

from strategy import Strategy


def save_to_csv(sell, buy, file_name):
    count = max(len(sell), len(buy))

    sell += [None] * (count - len(sell))
    buy += [None] * (count - len(buy))

    df = pd.DataFrame({
        'SELL': sell,
        'BUY': buy
    })
    df.to_csv(file_name, index=False)


strategy = Strategy()
strategy.download_usa_stocks()
strategy.download_china_stocks()
strategy.download_portfolio_stocks()

_, s_usa, b_usa = strategy.load_usa_stocks()
save_to_csv(list(s_usa.keys()), list(b_usa.keys()), "usa_stocks.csv")

_, s_china, b_china = strategy.load_china_stocks()
save_to_csv(list(s_china.keys()), list(b_china.keys()), "china_stocks.csv")

_, s_portfolio, b_portfolio = strategy.load_portfolio_stocks()
save_to_csv(list(s_portfolio.keys()), list(b_portfolio.keys()), "portfolio_stocks.csv")
