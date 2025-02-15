import pandas as pd

from strategy import Strategy


def save_to_csv(sell, buy, file_name):
    count = max(len(sell), len(buy))

    sell_keys = list(sell.keys())
    buy_keys = list(buy.keys())
    sell_keys += [None] * (count - len(sell_keys))
    buy_keys += [None] * (count - len(buy_keys))

    df = pd.DataFrame({
        'SELL': sell_keys,
        'SELL RSI': [round(sell[k]['RSI_7'].iloc[-1], 2) if k else None for k in sell_keys],
        'SELL BBP': [round(sell[k]['BBP'].iloc[-1], 2) if k else None for k in sell_keys],
        'BUY': buy_keys,
        'BUY RSI': [round(buy[k]['RSI_7'].iloc[-1], 2) if k else None for k in buy_keys],
        'BUY BBP': [round(buy[k]['BBP'].iloc[-1], 2) if k else None for k in buy_keys]
    })
    df.to_csv(file_name, index=False)


strategy = Strategy()
strategy.download_usa_stocks()
strategy.download_china_stocks()
strategy.download_portfolio_stocks()

_, s_usa, b_usa = strategy.load_usa_stocks()
save_to_csv(s_usa, b_usa, "usa_stocks.csv")

_, s_china, b_china = strategy.load_china_stocks()
save_to_csv(s_china, b_china, "china_stocks.csv")

_, s_portfolio, b_portfolio = strategy.load_portfolio_stocks()
save_to_csv(s_portfolio, b_portfolio, "portfolio_stocks.csv")
