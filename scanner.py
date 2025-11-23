# scanner.py - Professional Stock Scanner
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from ta.trend import ADXIndicator, MACD, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice, MFIIndicator
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StockScanner:
    def __init__(self):
        self.lookback_period = "6mo"
        self.interval = "1d"
    
    async def comprehensive_analysis(self, ticker):
        """Comprehensive professional analysis"""
        try:
            # Add .JK for Indonesian stocks if not present
            if not ticker.endswith('.JK') and len(ticker) == 4:
                ticker = f"{ticker}.JK"
            
            # Get stock data
            df = self._get_stock_data(ticker)
            if df is None or len(df) < 60:
                return None
            
            # Calculate all indicators
            df = self._calculate_all_indicators(df)
            
            # Perform comprehensive analysis
            analysis = self._perform_analysis(df, ticker)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in comprehensive_analysis for {ticker}: {e}")
            return None
    
    def _get_stock_data(self, ticker):
        """Get historical stock data"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=self.lookback_period, interval=self.interval)
            
            if df.empty:
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting data for {ticker}: {e}")
            return None
    
    def _calculate_all_indicators(self, df):
        """Calculate all technical indicators"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        
        # === TREND INDICATORS ===
        
        # Moving Averages
        df['EMA_9'] = EMAIndicator(close, window=9).ema_indicator()
        df['EMA_20'] = EMAIndicator(close, window=20).ema_indicator()
        df['EMA_50'] = EMAIndicator(close, window=50).ema_indicator()
        df['EMA_200'] = EMAIndicator(close, window=200).ema_indicator()
        
        df['SMA_20'] = SMAIndicator(close, window=20).sma_indicator()
        df['SMA_50'] = SMAIndicator(close, window=50).sma_indicator()
        df['SMA_200'] = SMAIndicator(close, window=200).sma_indicator()
        
        # ADX (Trend Strength)
        adx = ADXIndicator(high, low, close, window=14)
        df['ADX'] = adx.adx()
        df['ADX_POS'] = adx.adx_pos()
        df['ADX_NEG'] = adx.adx_neg()
        
        # MACD
        macd = MACD(close)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # === MOMENTUM INDICATORS ===
        
        # RSI
        df['RSI'] = RSIIndicator(close, window=14).rsi()
        
        # Stochastic
        stoch = StochasticOscillator(high, low, close, window=14, smooth_window=3)
        df['STOCH_K'] = stoch.stoch()
        df['STOCH_D'] = stoch.stoch_signal()
        
        # Williams %R
        df['WILLIAMS_R'] = WilliamsRIndicator(high, low, close, lbp=14).williams_r()
        
        # CCI (Commodity Channel Index)
        df['CCI'] = ta.trend.CCIIndicator(high, low, close, window=20).cci()
        
        # ROC (Rate of Change)
        df['ROC'] = ((close - close.shift(12)) / close.shift(12)) * 100
        
        # === VOLATILITY INDICATORS ===
        
        # Bollinger Bands
        bollinger = BollingerBands(close, window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        df['BB_Mid'] = bollinger.bollinger_mavg()
        df['BB_Width'] = ((df['BB_High'] - df['BB_Low']) / df['BB_Mid']) * 100
        
        # ATR (Average True Range)
        df['ATR'] = AverageTrueRange(high, low, close, window=14).average_true_range()
        
        # Keltner Channels
        keltner = KeltnerChannel(high, low, close, window=20)
        df['KC_High'] = keltner.keltner_channel_hband()
        df['KC_Low'] = keltner.keltner_channel_lband()
        df['KC_Mid'] = keltner.keltner_channel_mband()
        
        # === VOLUME INDICATORS ===
        
        # OBV (On Balance Volume)
        df['OBV'] = OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        df['OBV_EMA'] = EMAIndicator(df['OBV'], window=20).ema_indicator()
        
        # VWAP (Volume Weighted Average Price)
        df['VWAP'] = VolumeWeightedAveragePrice(high, low, close, volume).volume_weighted_average_price()
        
        # Volume SMA
        df['Volume_SMA'] = SMAIndicator(volume, window=20).sma_indicator()
        
        # MFI (Money Flow Index)
        df['MFI'] = MFIIndicator(high, low, close, volume, window=14).money_flow_index()
        
        # === CUSTOM INDICATORS ===
        
        # SuperTrend
        df = self._calculate_supertrend(df)
        
        # Support & Resistance
        df = self._calculate_support_resistance(df)
        
        return df
    
    def _calculate_supertrend(self, df, period=10, multiplier=3):
        """Calculate SuperTrend indicator"""
        hl2 = (df['High'] + df['Low']) / 2
        atr = AverageTrueRange(df['High'], df['Low'], df['Close'], window=period).average_true_range()
        
        upperband = hl2 + (multiplier * atr)
        lowerband = hl2 - (multiplier * atr)
        
        supertrend = [True] * len(df)
        
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > upperband.iloc[i-1]:
                supertrend[i] = True
            elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
                supertrend[i] = False
            else:
                supertrend[i] = supertrend[i-1]
                
                if supertrend[i] and lowerband.iloc[i] < lowerband.iloc[i-1]:
                    lowerband.iloc[i] = lowerband.iloc[i-1]
                if not supertrend[i] and upperband.iloc[i] > upperband.iloc[i-1]:
                    upperband.iloc[i] = upperband.iloc[i-1]
        
        df['SuperTrend'] = supertrend
        df['SuperTrend_Upper'] = upperband
        df['SuperTrend_Lower'] = lowerband
        
        return df
    
    def _calculate_support_resistance(self, df, window=20):
        """Calculate support and resistance levels"""
        df['Resistance'] = df['High'].rolling(window=window).max()
        df['Support'] = df['Low'].rolling(window=window).min()
        
        return df
    
    def _perform_analysis(self, df, ticker):
        """Perform comprehensive analysis"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        analysis = {
            'ticker': ticker.replace('.JK', ''),
            'price': latest['Close'],
            'volume': latest['Volume'],
            'change': ((latest['Close'] - prev['Close']) / prev['Close']) * 100,
        }
        
        # === TREND ANALYSIS ===
        trend_score = 0
        trend_signals = []
        
        # EMA Alignment
        if latest['Close'] > latest['EMA_9'] > latest['EMA_20'] > latest['EMA_50']:
            trend_score += 3
            trend_signals.append("🟢 Perfect EMA alignment - Strong uptrend")
        elif latest['Close'] < latest['EMA_9'] < latest['EMA_20'] < latest['EMA_50']:
            trend_score -= 3
            trend_signals.append("🔴 Bearish EMA alignment - Strong downtrend")
        
        # ADX Strength
        analysis['adx'] = latest['ADX']
        if latest['ADX'] > 25:
            if latest['ADX_POS'] > latest['ADX_NEG']:
                trend_score += 2
                trend_signals.append(f"🟢 Strong uptrend (ADX: {latest['ADX']:.1f})")
            else:
                trend_score -= 2
                trend_signals.append(f"🔴 Strong downtrend (ADX: {latest['ADX']:.1f})")
        else:
            trend_signals.append(f"⚪ Weak trend (ADX: {latest['ADX']:.1f})")
        
        # SuperTrend
        if latest['SuperTrend']:
            trend_score += 1
            trend_signals.append("🟢 SuperTrend: Bullish")
            analysis['supertrend_signal'] = "Bullish"
        else:
            trend_score -= 1
            trend_signals.append("🔴 SuperTrend: Bearish")
            analysis['supertrend_signal'] = "Bearish"
        
        # MACD
        if prev['MACD'] < prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            trend_score += 2
            trend_signals.append("🟢 MACD Bullish Crossover")
        elif prev['MACD'] > prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']:
            trend_score -= 2
            trend_signals.append("🔴 MACD Bearish Crossover")
        
        # === MOMENTUM ANALYSIS ===
        momentum_score = 0
        momentum_signals = []
        
        # RSI
        analysis['rsi'] = latest['RSI']
        if latest['RSI'] < 30:
            momentum_score += 2
            momentum_signals.append(f"🟢 RSI Oversold ({latest['RSI']:.1f})")
        elif latest['RSI'] > 70:
            momentum_score -= 2
            momentum_signals.append(f"🔴 RSI Overbought ({latest['RSI']:.1f})")
        elif 40 <= latest['RSI'] <= 60:
            momentum_signals.append(f"⚪ RSI Neutral ({latest['RSI']:.1f})")
        
        # Stochastic
        analysis['stochastic'] = latest['STOCH_K']
        if latest['STOCH_K'] < 20 and latest['STOCH_K'] > latest['STOCH_D']:
            momentum_score += 2
            momentum_signals.append("🟢 Stochastic oversold & turning up")
        elif latest['STOCH_K'] > 80 and latest['STOCH_K'] < latest['STOCH_D']:
            momentum_score -= 2
            momentum_signals.append("🔴 Stochastic overbought & turning down")
        
        # CCI
        analysis['cci'] = latest['CCI']
        if latest['CCI'] < -100:
            momentum_score += 1
            momentum_signals.append("🟢 CCI Oversold")
        elif latest['CCI'] > 100:
            momentum_score -= 1
            momentum_signals.append("🔴 CCI Overbought")
        
        # Williams %R
        if latest['WILLIAMS_R'] < -80:
            momentum_score += 1
            momentum_signals.append("🟢 Williams %R Oversold")
        elif latest['WILLIAMS_R'] > -20:
            momentum_score -= 1
            momentum_signals.append("🔴 Williams %R Overbought")
        
        # === VOLUME ANALYSIS ===
        volume_score = 0
        volume_signals = []
        
        # Volume vs Average
        if latest['Volume'] > latest['Volume_SMA'] * 1.5:
            volume_score += 2
            volume_signals.append("🟢 High volume confirmation")
        elif latest['Volume'] < latest['Volume_SMA'] * 0.5:
            volume_score -= 1
            volume_signals.append("🔴 Low volume - weak signal")
        
        # OBV Trend
        if latest['OBV'] > latest['OBV_EMA']:
            volume_score += 1
            volume_signals.append("🟢 OBV trending up")
            analysis['obv_trend'] = "Up"
        else:
            volume_score -= 1
            volume_signals.append("🔴 OBV trending down")
            analysis['obv_trend'] = "Down"
        
        # MFI
        analysis['mfi'] = latest['MFI']
        if latest['MFI'] < 20:
            volume_score += 1
            volume_signals.append("🟢 MFI Oversold")
        elif latest['MFI'] > 80:
            volume_score -= 1
            volume_signals.append("🔴 MFI Overbought")
        
        # === VOLATILITY ANALYSIS ===
        volatility_score = 0
        volatility_signals = []
        
        # Bollinger Bands
        if latest['Close'] < latest['BB_Low']:
            volatility_score += 2
            volatility_signals.append("🟢 Price below BB lower - oversold")
        elif latest['Close'] > latest['BB_High']:
            volatility_score -= 2
            volatility_signals.append("🔴 Price above BB upper - overbought")
        
        # BB Width (Volatility)
        if latest['BB_Width'] < 5:
            volatility_signals.append("⚪ Low volatility - potential breakout soon")
        
        # ATR
        atr_pct = (latest['ATR'] / latest['Close']) * 100
        if atr_pct > 3:
            volatility_signals.append(f"⚠️ High volatility (ATR: {atr_pct:.2f}%)")
        
        # === PRICE LEVELS ===
        analysis['resistance'] = latest['Resistance']
        analysis['support'] = latest['Support']
        
        # Distance to support/resistance
        dist_to_resistance = ((latest['Resistance'] - latest['Close']) / latest['Close']) * 100
        dist_to_support = ((latest['Close'] - latest['Support']) / latest['Close']) * 100
        
        if dist_to_support < 2:
            volatility_score += 1
            volatility_signals.append("🟢 Near support level")
        if dist_to_resistance < 2:
            volatility_score -= 1
            volatility_signals.append("🔴 Near resistance level")
        
        # === CALCULATE TOTAL SCORE ===
        total_score = trend_score + momentum_score + volume_score + volatility_score
        analysis['total_score'] = total_score
        analysis['trend_score'] = trend_score
        analysis['momentum_score'] = momentum_score
        analysis['volume_score'] = volume_score
        analysis['volatility_score'] = volatility_score
        
        # === TRADING SIGNAL ===
        if total_score >= 10:
            analysis['trading_signal'] = "STRONG BUY"
        elif total_score >= 5:
            analysis['trading_signal'] = "BUY"
        elif total_score >= -4:
            analysis['trading_signal'] = "HOLD"
        elif total_score >= -9:
            analysis['trading_signal'] = "SELL"
        else:
            analysis['trading_signal'] = "STRONG SELL"
        
        # === ENTRY, TARGET, STOP LOSS ===
        atr = latest['ATR']
        
        if 'BUY' in analysis['trading_signal']:
            # Entry di current atau support
            analysis['entry_point'] = f"Rp {latest['Support']:,.0f} - {latest['Close']:,.0f}"
            
            # Target menggunakan R:R 1:2
            target = latest['Close'] + (2 * atr)
            analysis['target_price'] = f"Rp {target:,.0f}"
            
            # Stop loss di bawah support
            stop_loss = latest['Support'] - atr
            analysis['stop_loss'] = f"Rp {stop_loss:,.0f}"
            
            risk_reward = (target - latest['Close']) / (latest['Close'] - stop_loss)
            analysis['risk_reward'] = f"1:{risk_reward:.2f}"
        else:
            analysis['entry_point'] = "N/A"
            analysis['target_price'] = "N/A"
            analysis['stop_loss'] = "N/A"
            analysis['risk_reward'] = "N/A"
        
        # === STATUS STRINGS ===
        if trend_score >= 4:
            analysis['trend_strength'] = "Strong Uptrend"
        elif trend_score >= 1:
            analysis['trend_strength'] = "Weak Uptrend"
        elif trend_score >= -3:
            analysis['trend_strength'] = "Sideways"
        else:
            analysis['trend_strength'] = "Downtrend"
        
        if momentum_score >= 3:
            analysis['momentum_status'] = "Bullish"
        elif momentum_score <= -3:
            analysis['momentum_status'] = "Bearish"
        else:
            analysis['momentum_status'] = "Neutral"
        
        if volume_score >= 2:
            analysis['volume_status'] = "Strong"
        elif volume_score <= -1:
            analysis['volume_status'] = "Weak"
        else:
            analysis['volume_status'] = "Normal"
        
        # === KEY SIGNALS ===
        all_signals = trend_signals + momentum_signals + volume_signals + volatility_signals
        analysis['key_signals'] = all_signals
        
        return analysis
    
    async def validate_ticker(self, ticker):
        """Validate if ticker exists"""
        try:
            if not ticker.endswith('.JK') and len(ticker) == 4:
                ticker = f"{ticker}.JK"
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return 'regularMarketPrice' in info or 'currentPrice' in info
            
        except:
            return False
    
    async def generate_chart(self, ticker):
        """Generate technical analysis chart"""
        try:
            if not ticker.endswith('.JK') and len(ticker) == 4:
                ticker = f"{ticker}.JK"
            
            df = self._get_stock_data(ticker)
            if df is None:
                return None
            
            df = self._calculate_all_indicators(df)
            
            # Create chart
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
            
            # Price and moving averages
            ax1.plot(df.index, df['Close'], label='Close', linewidth=2)
            ax1.plot(df.index, df['EMA_9'], label='EMA 9', alpha=0.7)
            ax1.plot(df.index, df['EMA_20'], label='EMA 20', alpha=0.7)
            ax1.plot(df.index, df['SMA_50'], label='SMA 50', alpha=0.7)
            ax1.fill_between(df.index, df['BB_High'], df['BB_Low'], alpha=0.1)
            ax1.set_ylabel('Price')
            ax1.set_title(f'{ticker} Technical Analysis')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # RSI
            ax2.plot(df.index, df['RSI'], label='RSI', color='purple')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax2.set_ylabel('RSI')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # MACD
            ax3.plot(df.index, df['MACD'], label='MACD', color='blue')
            ax3.plot(df.index, df['MACD_Signal'], label='Signal', color='red')
            ax3.bar(df.index, df['MACD_Hist'], label='Histogram', alpha=0.3)
            ax3.set_ylabel('MACD')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = f'/tmp/{ticker}_chart.png'
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating chart for {ticker}: {e}")
            return None
