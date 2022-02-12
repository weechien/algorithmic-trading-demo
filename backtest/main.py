import asyncio
from datetime import datetime, timezone
from os.path import join
from typing import Optional

import pandas as pd
from pandas import Timestamp, DataFrame

from shared.bot import Bot
from utils.settings import CANDLESTICK_WAIT_LEN_BEFORE_SELLING, BASE_DIR, CSV_FILE_DIR


def read_csv_file(file_path: str, start_date: Timestamp, end_date: Timestamp) -> DataFrame:
    df = pd.read_csv(file_path, parse_dates=['date'],
                     date_parser=lambda i: datetime.strptime(i, '%d-%m-%y %H:%M').replace(tzinfo=timezone.utc))
    # Filter by start and end dates
    df = df[(df['date'] >= start_date) & (df['date'] < end_date)]
    print(f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} loading data... number of rows: {len(df.index)}")
    return df


def run_backtest(df: DataFrame):
    bot = Bot()
    candlestick_sell_timer: Optional[int] = None

    # Go through each row of the CSV file and process its data
    for _, candlestick in df.iterrows():
        has_crossover = bot.feed_candlestick(dict(candlestick))
        if has_crossover and round(bot.usd):
            # SMA crossover happened, and we still have funds, spend 100% funds to buy BTC
            bot.buy(candlestick['date'], candlestick['close'], bot.usd)
            candlestick_sell_timer = 0
            continue
        if candlestick_sell_timer is not None:
            candlestick_sell_timer += 1
            if candlestick_sell_timer == CANDLESTICK_WAIT_LEN_BEFORE_SELLING:
                # Sell all BTC after some time has passed
                bot.sell(candlestick['date'], candlestick['close'], bot.btc)
                candlestick_sell_timer = None

    # Sell off all btc at the end if there is any left
    bot.btc and bot.sell(df.iloc[-1]['date'], df.iloc[-1]['close'], bot.btc)


async def main():
    csv_file_path = join(BASE_DIR, CSV_FILE_DIR, '01Jan22-00꞉00_to_01Feb22-00꞉00.csv')
    start_date = pd.Timestamp(2022, 1, 1, 0, 0).tz_localize('utc')
    end_date = pd.Timestamp(2022, 2, 1, 0, 0).tz_localize('utc')

    df = read_csv_file(csv_file_path, start_date=start_date, end_date=end_date)
    run_backtest(df)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
