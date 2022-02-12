from os.path import abspath, dirname

from utils.constants import CandlestickInterval

BASE_DIR = dirname(dirname(abspath(__file__)))

SYMBOL = 'BTCUSDT'
INTERVAL = CandlestickInterval.MIN15

CSV_ROW_DATE_FORMAT = '%d-%m-%y %H:%M'
CSV_FILE_DIR = 'csv'

STARTING_FUNDS = 10_000
CANDLESTICK_WAIT_LEN_BEFORE_SELLING = 4
