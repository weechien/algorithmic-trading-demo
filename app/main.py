import asyncio
from typing import Optional

from binance import BinanceSocketManager, AsyncClient

from shared.bot import Bot
from utils.helpers import timestamp_to_date
from utils.settings import SYMBOL, CANDLESTICK_WAIT_LEN_BEFORE_SELLING, INTERVAL, CSV_ROW_DATE_FORMAT
from utils.typings import ICandlestick, ICandlestickStream


def parse_stream_to_candlestick(s: ICandlestickStream) -> ICandlestick:
    data = s['k']
    date = timestamp_to_date(data['t']).strftime(CSV_ROW_DATE_FORMAT)
    return {'date': date, 'open': data['o'], 'high': data['h'], 'low': data['l'], 'close': data['c'],
            'volume': data['v'], 'sma20': float('NaN'), 'sma50': float('NaN')}


async def candlestick_listener(client):
    bot = Bot()
    candlestick_sell_timer: Optional[int] = None
    previous_start_time: str = ''
    bsm = BinanceSocketManager(client)

    async with bsm.kline_socket(symbol=SYMBOL, interval=INTERVAL) as stream:
        while True:
            res = await stream.recv()
            candlestick = parse_stream_to_candlestick(res)
            start_time = candlestick['date']

            # New candlestick forming when start time changes
            if previous_start_time != start_time:
                print(candlestick)
                previous_start_time = start_time

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


async def main():
    client = await AsyncClient.create()
    await candlestick_listener(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
