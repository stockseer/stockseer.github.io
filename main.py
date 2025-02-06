from stockseer import Strategy

strategy = Strategy()
strategy.download_usa_stocks()
strategy.download_china_stocks()

all_usa, sell_usa, buy_usa = strategy.load_usa_stocks()
all_china, sell_china, buy_china = strategy.load_china_stocks()
