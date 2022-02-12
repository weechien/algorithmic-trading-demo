from typing import TypedDict, Optional


class ICandlestick(TypedDict):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    sma20: Optional[float]
    sma50: Optional[float]


class ICandlestickStreamData(TypedDict):
    t: int  # Kline start time
    T: int  # Kline close time
    s: str  # Symbol
    i: str  # Interval
    f: int  # First trade ID
    L: int  # Last trade ID
    o: float  # Open price
    c: float  # Close price
    h: float  # High price
    l: float  # Low price
    v: float  # Base asset volume
    n: int  # Number of trades
    x: bool  # Is this kline closed?
    q: float  # Quote asset volume
    V: float  # Taker buy base asset volume
    Q: float  # Taker buy quote asset volume
    B: int  # Ignore


class ICandlestickStream(TypedDict):
    e: str  # Event type
    E: int  # Event time
    s: str  # Symbol
    k: ICandlestickStreamData
