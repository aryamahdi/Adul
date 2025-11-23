# utils/indicators.py
import pandas as pd
import numpy as np

def ema(series: pd.Series, length: int):
    return series.ewm(span=length, adjust=False).mean()

def atr(df: pd.DataFrame, n=14):
    # df must have 'high','low','close'
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    return atr

def dx(df: pd.DataFrame, n=14):
    # returns ADX series
    high = df['high']
    low = df['low']
    close = df['close']

    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(n).mean()
    plus_di = 100 * (plus_dm.rolling(n).sum() / atr)
    minus_di = 100 * (minus_dm.rolling(n).sum() / atr)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).replace([np.inf, -np.inf], 0).fillna(0)
    adx = dx.rolling(n).mean()
    return adx
