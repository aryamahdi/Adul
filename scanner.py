# scanner.py
import pandas as pd
import time
import math
import yfinance as yf

from config import *
from utils.indicators import ema, atr, dx

def fetch_ohlcv(symbol, period='1d', days=120):
    """
    Mengambil data OHLCV via yfinance.
    period examples: '1d', '60m', '1h' (yfinance uses interval param: '1d','60m', etc)
    """
    interval = period
    # yfinance's history uses 'period' and 'interval'
    hist = yf.Ticker(symbol).history(period=f"{days}d", interval=interval)
    if hist.empty:
        raise ValueError(f"No data for {symbol} interval {interval}")
    hist = hist.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
    hist = hist[['open','high','low','close','volume']]
    hist.index = pd.to_datetime(hist.index)
    hist = hist.reset_index()
    return hist

def check_reversal_setup(df: pd.DataFrame):
    """
    Apply rules:
    - ADX < ADX_THRESHOLD
    - Price below EMA20 & EMA50
    - EMA20 flattening (slope small)
    - Presence of bullish reversal candle (hammer or bullish engulf)
    - Volume confirmation
    - ATR not spiking
    """
    df = df.copy()
    df['ema20'] = ema(df['close'], EMA_SHORT)
    df['ema50'] = ema(df['close'], EMA_LONG)
    df['atr'] = atr(df, ATR_LEN)
    df['adx'] = dx(df, ADX_LEN)
    df['vol_sma'] = df['volume'].rolling(VOL_SMA_LEN).mean()

    # work on last bar as potential reversal (most recent completed bar)
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ADX condition
    if pd.isna(last['adx']) or last['adx'] >= ADX_THRESHOLD:
        return None

    # Price below EMAs
    if not (last['close'] < last['ema20'] and last['close'] < last['ema50']):
        return None

    # EMA20 flattening: slope approximate
    ema20_slope = (df['ema20'].iloc[-1] - df['ema20'].iloc[-3]) / 2
    if abs(ema20_slope) > (0.002 * last['close']):  # threshold relative to price; tweakable
        # if slope too big (still trending), skip
        return None

    # Candle patterns: hammer or bullish engulfing
    # Hammer: long lower wick, small body near high
    candle_body = abs(last['close'] - last['open'])
    candle_range = last['high'] - last['low'] if (last['high'] - last['low'])>0 else 1
    lower_wick = min(last['open'], last['close']) - last['low']
    upper_wick = last['high'] - max(last['open'], last['close'])

    is_hammer = (lower_wick > 2 * candle_body) and (upper_wick < candle_body)
    # bullish engulfing
    is_bull_engulf = (last['close'] > last['open']) and (prev['close'] < prev['open']) and (last['close'] > prev['open']) and (last['open'] < prev['close'])

    if not (is_hammer or is_bull_engulf):
        return None

    # Volume confirmation
    if last['volume'] < VOL_MULT * last['vol_sma']:
        return None

    # ATR sanity
    if last['atr'] is None or last['atr'] <= 0:
        return None

    # Compose signal
    entry = last['close']
    sl = min(last['low'], prev['low']) - ATR_SL_MULT * last['atr']
    rr1 = 1.5
    rr2 = 3.0
    t1 = entry + rr1 * (entry - sl)
    t2 = entry + rr2 * (entry - sl)

    # approximate confidence (simple heuristic)
    confidence = 50
    confidence += int((VOL_MULT * last['vol_sma'] / max(1,last['volume'])) * 10)  # not perfect
    confidence += int(max(0, (ADX_THRESHOLD - last['adx'])))  # lower adx better
    confidence = max(30, min(95, confidence))

    return {
        "entry": float(round(entry, 2)),
        "sl": float(round(sl, 2)),
        "t1": float(round(t1, 2)),
        "t2": float(round(t2, 2)),
        "atr": float(round(last['atr'], 4)),
        "adx": float(round(last['adx'], 2)),
        "ema20": float(round(last['ema20'], 2)),
        "ema50": float(round(last['ema50'], 2)),
        "volume": int(last['volume']),
        "vol_sma": int(last['vol_sma']),
        "pattern": "hammer" if is_hammer else "bull_engulf",
        "confidence": confidence,
        "time": str(last.name)  # index was reset; better to return timestamp if needed
    }

def scan_universe(symbols=SYMBOLS):
    signals = []
    for s in symbols:
        try:
            df = fetch_ohlcv(s, period=DATA_PERIOD, days=HIST_DAYS)
            result = check_reversal_setup(df)
            if result:
                result['symbol'] = s
                signals.append(result)
        except Exception as e:
            print(f"[WARN] {s} fetch/scan error: {e}")
    return signals

if __name__ == "__main__":
    found = scan_universe()
    print("Signals found:", found)
