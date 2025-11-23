# config.py
# Ubah sesuai preferensi dan market-mappingmu

TELEGRAM_BOT_TOKEN = "8395891979:AAHK_mrf5wTp8p1mTmz9tq1hecn55dEkhqE"
TELEGRAM_CHAT_ID = "7721925871"

# Scanner universe (blue-chip / big-cap) — masukkan simbol sesuai exchange
SYMBOLS = [
    "BBCA.JK" # contoh IDX; sesuaikan prefix sesuai source
]

# Data source config
DATA_PERIOD = "60m"   # bisa '1d', '60m', '240m' dst — scanner pakai daily + lower TF confirmation
HIST_DAYS = 120      # berapa hari historis diambil untuk indikator

# Indicators
EMA_SHORT = 20
EMA_LONG = 50
ADX_LEN = 14
ATR_LEN = 14
VOL_SMA_LEN = 20

# Thresholds / rules
ADX_THRESHOLD = 20       # adx < 20 untuk non-trending / siap reversal
VOL_MULT = 1.2           # volume bullish candle minimal 1.2x avg
ATR_SL_MULT = 1.3        # SL = low - ATR * multiplier
SL_RISK_PERCENT = 0.02   # risk per trade as fraction of equity (for position sizing)
MIN_AVG_VOLUME = 1_000_000  # minimal avg volume (adjust per market)
CONFIRMATION_CANDLES = 1  # use 1 next candle confirmation optional

# Position sizing defaults (for message suggestion)
DEFAULT_EQUITY = 100_000_000  # contoh: 100,000,000 IDR

# Misc
ENV = "production"
