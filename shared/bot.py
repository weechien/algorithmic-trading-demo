from typing import Optional, Literal

import pandas as pd
from ta.trend import SMAIndicator

from utils.settings import STARTING_FUNDS
from utils.typings import ICandlestick

REQUIRED_CANDLESTICK_LEN = 200


class Bot:
    candlesticks: list[ICandlestick] = None
    btc: float = 0
    usd: float = 0
    last_bought_amount_in_usd: float = 0
    cumulative_pnl: float = 0

    def __init__(self):
        self.candlesticks = []
        self.btc = 0
        self.usd = STARTING_FUNDS
        self.last_bought_amount_in_usd = 0
        self.cumulative_pnl = 0

    def feed_candlestick(self, candlestick: ICandlestick) -> Optional[bool]:
        self.candlesticks.append(candlestick)
        self.candlesticks = self.candlesticks[-REQUIRED_CANDLESTICK_LEN:]

        candlestick['sma20'] = self.get_sma(self.candlesticks, window=20)
        candlestick['sma50'] = self.get_sma(self.candlesticks, window=50)

        # SMA calculation requires a certain amount of candlesticks
        if len(self.candlesticks) < REQUIRED_CANDLESTICK_LEN:
            return

        return self.check_sma_crossover()

    def check_sma_crossover(self) -> bool:
        previous_sma20 = self.candlesticks[-2]['sma20']
        previous_sma50 = self.candlesticks[-2]['sma50']
        current_sma20 = self.candlesticks[-1]['sma20']
        current_sma50 = self.candlesticks[-1]['sma50']
        return previous_sma20 < previous_sma50 and current_sma20 > current_sma50

    def buy(self, date: str, current_btc_price: float, amount_in_usd: float):
        amount_in_usd_to_deduct = min(amount_in_usd, self.usd)
        self.last_bought_amount_in_usd = amount_in_usd_to_deduct
        self.usd -= amount_in_usd_to_deduct
        self.btc += amount_in_usd_to_deduct / current_btc_price
        self.log(date, 'buy', current_btc_price, amount_in_usd)

    def sell(self, date: str, current_btc_price: float, amount_in_btc: float):
        amount_in_btc_to_deduct = min(amount_in_btc, self.btc)
        self.btc -= amount_in_btc_to_deduct
        self.usd += amount_in_btc_to_deduct * current_btc_price
        pnl = self.usd - self.last_bought_amount_in_usd
        self.cumulative_pnl += pnl
        self.log(date, 'sell', current_btc_price, amount_in_btc, pnl)

    def log(self, date: str, action: Literal['buy', 'sell'], price: float, amount: float, pnl: float = None):
        action_title = 'BOUGHT' if action == 'buy' else 'SOLD'
        amount_denominator = 'USD' if action == 'buy' else 'BTC'
        pnl_row = f"{'PNL':<15}: {pnl:.4f} USD\n" if pnl else ''
        cumulative_pnl_row = f"{'Cumulative PNL':<15}: {self.cumulative_pnl:.4f} USD\n" if pnl else ''
        print(f"{date}\n"
              f"{action_title} BTC\n"
              f"--------------------------\n"
              f"{'Price':<15}: {price:.2f} USD\n"
              f"{'Amount':<15}: {amount:.2f} {amount_denominator}\n"
              f"{'BTC bal':<15}: {self.btc:.2f} BTC\n"
              f"{'USD bal':<15}: {self.usd:.2f} USD\n"
              f"{pnl_row}"
              f"{cumulative_pnl_row}"
              f"--------------------------\n")

    @staticmethod
    def get_sma(candlesticks: list[ICandlestick], window: int) -> float:
        close_price_list = pd.Series([c['close'] for c in candlesticks])
        sma_list = SMAIndicator(close=close_price_list, window=window).sma_indicator()
        return sma_list.iloc[-1] if len(sma_list) else float('NaN')
