import numpy as np


class Indicator:

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
