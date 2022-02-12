import asyncio
import codecs
from datetime import datetime, timezone
from os.path import join

import pandas as pd
from binance import AsyncClient
from ta.trend import SMAIndicator

from utils.constants import CandlestickInterval
from utils.helpers import date_to_timestamp, timestamp_to_date, interval_in_ms
from utils.settings import SYMBOL, INTERVAL, CSV_ROW_DATE_FORMAT, CSV_FILE_DIR, BASE_DIR

INDICATORS = ['sma20', 'sma50']
CSV_HEADERS = f"date,open,high,low,close,volume,{','.join(INDICATORS)}\n"
CSV_FILENAME_DATE_FORMAT = '%d%b%y-%H{}%M'

FETCH_LIMIT = 1000
CANDLESTICK_LIMIT_FOR_INDICATOR = 499


def make_get_indicators():
    candlesticks = []

    def get_indicators(candlestick) -> tuple[float, float]:
        nonlocal candlesticks

        candlesticks.append(candlestick)
        candlesticks = candlesticks[-CANDLESTICK_LIMIT_FOR_INDICATOR:]
        series = pd.Series([c[4] for c in candlesticks])  # Close
        sma20 = SMAIndicator(series, window=20).sma_indicator().iloc[-1]
        sma50 = SMAIndicator(series, window=50).sma_indicator().iloc[-1]
        return sma20, sma50

    return get_indicators


async def gen_candlestick_csv_data(client: AsyncClient, interval: CandlestickInterval, start_date: datetime,
                                   end_date: datetime):
    start_timestamp = date_to_timestamp(start_date)
    end_timestamp = date_to_timestamp(end_date)

    start_date_str = start_date.strftime(CSV_FILENAME_DATE_FORMAT).format('꞉')
    end_date_str = end_date.strftime(CSV_FILENAME_DATE_FORMAT).format('꞉')
    filename = f"{start_date_str}_to_{end_date_str}"

    csv_file_path = join(BASE_DIR, CSV_FILE_DIR, f'{filename}.csv')
    with codecs.open(csv_file_path, 'w', 'utf-8') as f:
        f.write(CSV_HEADERS)

    get_indicators = make_get_indicators()
    while start_timestamp < end_timestamp:
        candlesticks = await client.get_klines(symbol=SYMBOL, interval=INTERVAL, limit=FETCH_LIMIT,
                                               startTime=start_timestamp, endTime=end_timestamp)
        with codecs.open(csv_file_path, 'a', 'utf-8') as f:
            for candlestick in candlesticks:
                open_time, _open, high, low, close, volume = \
                    candlestick[0], candlestick[1], candlestick[2], candlestick[3], candlestick[4], candlestick[5]
                if open_time == end_timestamp:
                    break
                indicators = get_indicators(candlestick)

                separator = ',' if len(indicators) else ''
                indicators_str = f"{separator}{','.join([str(i) for i in indicators])}"
                formatted_date = timestamp_to_date(open_time).strftime(CSV_ROW_DATE_FORMAT)
                line = f"{formatted_date},{_open},{high},{low},{close},{volume}{indicators_str}"
                f.write(line)
                f.write('\n')
        start_timestamp = candlesticks[-1][0]
        if start_timestamp >= end_timestamp:
            break
        start_timestamp += interval_in_ms(interval)
        await asyncio.sleep(1)
    print(f'done generating csv file:\n{csv_file_path}')


async def main():
    client = await AsyncClient.create()
    await gen_candlestick_csv_data(
        client=client,
        interval=INTERVAL,
        start_date=datetime(2022, 1, 1, 0, 0, tzinfo=timezone.utc),
        end_date=datetime(2022, 2, 1, 0, 0, tzinfo=timezone.utc)
    )
    await client.close_connection()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
