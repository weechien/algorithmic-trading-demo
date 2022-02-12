import csv
from datetime import datetime, timezone
from os.path import join

import mplfinance as mpf
import pandas as pd

from utils.helpers import date_to_timestamp, split_full_path
from utils.settings import INTERVAL, CSV_ROW_DATE_FORMAT, BASE_DIR, CSV_FILE_DIR


def parse_csv_file(full_path: str) -> str:
    df = pd.read_csv(full_path, sep=',')

    dirpath, filename, ext = split_full_path(full_path)
    new_path = join(dirpath, f'{filename}_{INTERVAL}{ext}')
    with open(new_path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['unix', 'date', 'open', 'high', 'low', 'close', 'volume', 'sma20', 'sma50'])
    for _, row in df.iterrows():
        date = datetime.strptime(row['date'], CSV_ROW_DATE_FORMAT).replace(tzinfo=timezone.utc)
        unix = date_to_timestamp(date)
        _open, high, low, close, volume, sma20, sma50 = \
            row['open'], row['high'], row['low'], row['close'], row['volume'], row['sma20'], row['sma50']

        with open(new_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([unix, date, _open, high, low, close, volume, sma20, sma50])
    return new_path


def plot_from_csv(full_path: str, addplot=None, start=0, limit=None) -> str:
    df = pd.read_csv(full_path, index_col=1, parse_dates=True)
    df = df[start:limit] if limit else df[start:]

    mc = mpf.make_marketcolors(base_mpf_style='binance', vcdopcod=True)
    style = mpf.make_mpf_style(base_mpf_style='binance', marketcolors=mc)
    dirpath, _, _ = split_full_path(full_path)
    save_path = join(dirpath, 'plot.jpg')

    apds = []
    if addplot:
        apds.append(mpf.make_addplot(df[addplot]))
    mpf.plot(df, type='candle', style=style, figratio=(18, 10), addplot=apds, savefig=save_path, volume=True)
    return save_path


if __name__ == '__main__':
    path = join(BASE_DIR, CSV_FILE_DIR, '01Jan22-00꞉00_to_01Feb22-00꞉00.csv')
    parsed_path = parse_csv_file(path)
    plot_from_csv(parsed_path, addplot=['sma20', 'sma50'], start=50, limit=200)
