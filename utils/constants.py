class CandlestickInterval:
    MIN1 = "1m"
    MIN3 = "3m"
    MIN5 = "5m"
    MIN15 = "15m"
    MIN30 = "30m"
    HOUR1 = "1h"
    HOUR2 = "2h"
    HOUR4 = "4h"
    HOUR6 = "6h"
    HOUR8 = "8h"
    HOUR12 = "12h"
    DAY1 = "1d"
    DAY3 = "3d"
    WEEK1 = "1w"
    MON1 = "1m"
    INVALID = None


CANDLESTICK_INTERVAL_TO_MS_MAP = {
    CandlestickInterval.MIN1: 60000,
    CandlestickInterval.MIN3: 180000,
    CandlestickInterval.MIN5: 300000,
    CandlestickInterval.MIN15: 900000,
    CandlestickInterval.MIN30: 1800000,
    CandlestickInterval.HOUR1: 3600000,
    CandlestickInterval.HOUR2: 7200000,
    CandlestickInterval.HOUR4: 14400000,
    CandlestickInterval.HOUR6: 21600000,
    CandlestickInterval.HOUR8: 28800000,
    CandlestickInterval.HOUR12: 43200000,
    CandlestickInterval.DAY1: 86400000,
    CandlestickInterval.DAY3: 259200000,
    CandlestickInterval.WEEK1: 604800000,
}
