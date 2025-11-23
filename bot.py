# bot.py - Main Bot File
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from scanner import StockScanner
from sectors_api import SectorsAPI, ManualPortfolio
from datetime import datetime, time as dt_time
import asyncio

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
SECTORS_API_KEY = os.getenv('SECTORS_API_KEY')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

# Initialize
scanner = StockScanner()
sectors = SectorsAPI(SECTORS_API_KEY)

# Watchlist and Portfolio databases
user_watchlists = {}
user_portfolios = {}  # Store ManualPortfolio instances

class TradingBot:
    def __init__(self):
        self.scanner = scanner
        self.stockbit = stockbit
        self.is_scanning = False
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /start"""
        user_id = update.effective_user.id
        
        if user_id not in user_watchlists:
            user_watchlists[user_id] = []
        
        welcome = f"""
🤖 *Bot Scanner Saham Professional*
Powered by Stockbit API

👋 Selamat datang {update.effective_user.first_name}!

🎯 *Fitur Utama:*
• Scanner 20+ indikator teknikal profesional
• Analisis swing trading setup lengkap
• Alert real-time untuk entry/exit point
• Integrasi dengan Stockbit portfolio
• Auto-scan setiap jam trading

📊 *Indikator yang Digunakan:*
✓ Trend: EMA, SMA, SuperTrend, ADX
✓ Momentum: RSI, Stochastic, CCI, Williams %R
✓ Volume: OBV, VWAP, Volume Profile
✓ Volatility: Bollinger Bands, ATR, Keltner
✓ Pattern: Candlestick patterns
✓ Support/Resistance levels

📋 *Command:*
/scan - Scan semua watchlist
/analyze KODE - Analisis mendalam
/portfolio - Lihat portfolio Stockbit
/watchlist - Kelola watchlist
/signals - Setup trading hari ini
/screener - Screener custom
/help - Bantuan lengkap

⚙️ Ketik /watchlist untuk mulai menambah saham.
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Scan Now", callback_data="scan_all")],
            [InlineKeyboardButton("📋 Watchlist", callback_data="show_watchlist")],
            [InlineKeyboardButton("💼 Portfolio", callback_data="show_portfolio")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def scan_all(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /scan - Professional scan"""
        query = update.callback_query
        if query:
            await query.answer()
            message = query.message
        else:
            message = update.message
        
        user_id = update.effective_user.id
        watchlist = user_watchlists.get(user_id, [])
        
        if not watchlist:
            await message.reply_text(
                "⚠️ Watchlist kosong!\n\n"
                "Gunakan /add KODE untuk menambah saham.\n"
                "Contoh: /add BBCA"
            )
            return
        
        progress_msg = await message.reply_text("🔍 Memulai professional scan...\n⏳ Mohon tunggu...")
        
        # Perform comprehensive scan
        results = []
        for i, ticker in enumerate(watchlist, 1):
            try:
                await progress_msg.edit_text(
                    f"🔍 Scanning {i}/{len(watchlist)}\n"
                    f"📊 Analyzing {ticker}..."
                )
                
                analysis = await scanner.comprehensive_analysis(ticker)
                if analysis:
                    results.append(analysis)
                
            except Exception as e:
                logger.error(f"Error scanning {ticker}: {e}")
                continue
        
        if not results:
            await progress_msg.edit_text("❌ Tidak ada data yang bisa dianalisis.")
            return
        
        # Sort by total score
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Generate report
        report = self._generate_scan_report(results)
        
        # Send report (split if too long)
        await progress_msg.delete()
        
        for chunk in self._split_message(report, 4000):
            await message.reply_text(chunk, parse_mode='Markdown')
        
        # Send top signals
        await self._send_top_signals(message, results)
    
    async def analyze_ticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /analyze KODE - Deep analysis"""
        if not context.args:
            await update.message.reply_text(
                "⚠️ Format salah!\n\n"
                "Gunakan: /analyze KODE\n"
                "Contoh: /analyze BBCA"
            )
            return
        
        ticker = context.args[0].upper()
        await update.message.reply_text(f"🔬 Menganalisis {ticker} secara mendalam...")
        
        try:
            analysis = await scanner.comprehensive_analysis(ticker)
            
            if not analysis:
                await update.message.reply_text(f"❌ Gagal menganalisis {ticker}")
                return
            
            # Generate detailed report
            report = self._generate_detailed_report(analysis)
            
            # Send report
            for chunk in self._split_message(report, 4000):
                await update.message.reply_text(chunk, parse_mode='Markdown')
            
            # Send chart if available
            chart_path = await scanner.generate_chart(ticker)
            if chart_path and os.path.exists(chart_path):
                await update.message.reply_photo(photo=open(chart_path, 'rb'))
                os.remove(chart_path)
            
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def show_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /portfolio - Show manual portfolio"""
        query = update.callback_query
        if query:
            await query.answer()
            message = query.message
        else:
            message = update.message
        
        user_id = update.effective_user.id
        
        await message.reply_text("📊 Menghitung portfolio value...")
        
        try:
            # Get or create user portfolio
            if user_id not in user_portfolios:
                user_portfolios[user_id] = ManualPortfolio(user_id)
            
            portfolio_manager = user_portfolios[user_id]
            portfolio = await portfolio_manager.get_portfolio_value(sectors)
            
            if not portfolio['holdings']:
                await message.reply_text(
                    "📋 Portfolio kosong\n\n"
                    "Gunakan /addholding untuk menambah saham ke portfolio\n"
                    "Format: /addholding BBCA 5 8500\n"
                    "(ticker, lot, avg_price)"
                )
                return
            
            report = self._generate_portfolio_report(portfolio)
            await message.reply_text(report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            await message.reply_text(f"❌ Error: {str(e)}")
    
    async def watchlist_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /watchlist - Manage watchlist"""
        user_id = update.effective_user.id
        watchlist = user_watchlists.get(user_id, [])
        
        text = "📋 *WATCHLIST MANAGEMENT*\n\n"
        
        if watchlist:
            text += "*Saham yang dipantau:*\n"
            for i, ticker in enumerate(watchlist, 1):
                text += f"{i}. {ticker}\n"
            text += f"\nTotal: {len(watchlist)} saham\n"
        else:
            text += "_Watchlist kosong_\n"
        
        text += "\n*Commands:*\n"
        text += "/add KODE - Tambah saham\n"
        text += "/remove KODE - Hapus saham\n"
        text += "/clear - Kosongkan watchlist\n"
        text += "/import - Import dari Stockbit"
        
        keyboard = [
            [InlineKeyboardButton("➕ Tambah Saham", callback_data="add_stock")],
            [InlineKeyboardButton("🔄 Import dari Stockbit", callback_data="import_stockbit")],
            [InlineKeyboardButton("📊 Scan Watchlist", callback_data="scan_all")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def add_to_watchlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /add KODE"""
        if not context.args:
            await update.message.reply_text("⚠️ Format: /add KODE\nContoh: /add BBCA")
            return
        
        user_id = update.effective_user.id
        ticker = context.args[0].upper()
        
        if user_id not in user_watchlists:
            user_watchlists[user_id] = []
        
        if ticker in user_watchlists[user_id]:
            await update.message.reply_text(f"ℹ️ {ticker} sudah ada di watchlist")
            return
        
        # Validate ticker
        is_valid = await scanner.validate_ticker(ticker)
        if not is_valid:
            await update.message.reply_text(f"❌ {ticker} tidak ditemukan atau tidak valid")
            return
        
        user_watchlists[user_id].append(ticker)
        await update.message.reply_text(f"✅ {ticker} ditambahkan ke watchlist")
    
    async def remove_from_watchlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /remove KODE"""
        if not context.args:
            await update.message.reply_text("⚠️ Format: /remove KODE\nContoh: /remove BBCA")
            return
        
        user_id = update.effective_user.id
        ticker = context.args[0].upper()
        
        if user_id not in user_watchlists or ticker not in user_watchlists[user_id]:
            await update.message.reply_text(f"ℹ️ {ticker} tidak ada di watchlist")
            return
        
        user_watchlists[user_id].remove(ticker)
        await update.message.reply_text(f"✅ {ticker} dihapus dari watchlist")
    
    async def signals_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /signals - Trading signals today using Sectors API"""
        await update.message.reply_text("🎯 Mencari setup trading terbaik hari ini...")
        
        try:
            # Get top gainers and top active stocks from Sectors API
            top_active = await sectors.get_most_active(limit=30)
            
            buy_signals = []
            sell_signals = []
            
            for stock in top_active:
                ticker = stock.get('symbol', '')
                try:
                    analysis = await scanner.comprehensive_analysis(ticker)
                    
                    if analysis and analysis['trading_signal'] == 'STRONG BUY':
                        buy_signals.append(analysis)
                    elif analysis and analysis['trading_signal'] == 'STRONG SELL':
                        sell_signals.append(analysis)
                        
                except Exception as e:
                    continue
            
            # Generate signals report
            report = "🎯 *TRADING SIGNALS HARI INI*\n"
            report += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            report += "=" * 30 + "\n\n"
            
            if buy_signals:
                report += "🟢 *BUY SIGNALS:*\n\n"
                for sig in buy_signals[:5]:  # Top 5
                    report += f"*{sig['ticker']}* - Rp {sig['price']:,.0f}\n"
                    report += f"{sig['trading_signal']} (Score: {sig['total_score']})\n"
                    report += f"Entry: {sig['entry_point']}\n"
                    report += f"Target: {sig['target_price']}\n"
                    report += f"SL: {sig['stop_loss']}\n\n"
            
            if sell_signals:
                report += "🔴 *SELL SIGNALS:*\n\n"
                for sig in sell_signals[:5]:  # Top 5
                    report += f"*{sig['ticker']}* - Rp {sig['price']:,.0f}\n"
                    report += f"{sig['trading_signal']} (Score: {sig['total_score']})\n\n"
            
            if not buy_signals and not sell_signals:
                report += "ℹ️ Tidak ada signal kuat hari ini\n"
                report += "Pasar sedang dalam kondisi netral"
            
            await update.message.reply_text(report, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in signals_today: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command /help"""
        help_text = """
📖 *PANDUAN LENGKAP BOT*

*🎯 ANALISIS PROFESIONAL*
Bot ini menggunakan 20+ indikator teknikal untuk memberikan analisis swing trading yang komprehensif.

*📊 INDIKATOR YANG DIGUNAKAN:*

*Trend Indicators:*
• EMA 9, 20, 50, 200
• SMA 20, 50, 200
• SuperTrend
• ADX (Average Directional Index)
• Parabolic SAR

*Momentum Indicators:*
• RSI (Relative Strength Index)
• Stochastic Oscillator
• CCI (Commodity Channel Index)
• Williams %R
• ROC (Rate of Change)

*Volume Indicators:*
• OBV (On Balance Volume)
• VWAP (Volume Weighted Average Price)
• Volume SMA
• Money Flow Index (MFI)

*Volatility Indicators:*
• Bollinger Bands
• ATR (Average True Range)
• Keltner Channels
• Standard Deviation

*Pattern Recognition:*
• Candlestick patterns (Doji, Hammer, etc)
• Chart patterns (Support/Resistance)
• Fibonacci retracements

*💼 COMMANDS:*
/scan - Scan all watchlist
/analyze KODE - Analisis mendalam
/signals - Setup trading hari ini
/portfolio - Portfolio Stockbit
/watchlist - Kelola watchlist
/add KODE - Tambah ke watchlist
/remove KODE - Hapus dari watchlist
/screener - Custom screener

*🎓 CARA MENGGUNAKAN:*
1. Tambahkan saham: /add BBCA
2. Scan watchlist: /scan
3. Analisis detail: /analyze BBCA
4. Lihat signals: /signals

*📈 INTERPRETASI SCORE:*
+15 hingga +20: STRONG BUY
+8 hingga +14: BUY
-7 hingga +7: NEUTRAL/HOLD
-8 hingga -14: SELL
-15 hingga -20: STRONG SELL

*💡 TIPS SWING TRADING:*
• Entry saat RSI oversold + MACD crossover
• Konfirmasi dengan volume tinggi
• Set stop loss di bawah support terdekat
• Target profit 1.5-2x risk (R:R ratio)
• Hold 3-7 hari untuk swing trade

*⚠️ DISCLAIMER:*
Bot ini adalah tools bantu analisis. Keputusan trading tetap ada di tangan Anda. Selalu gunakan risk management yang baik.

📞 Support: @yourusername
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    def _generate_scan_report(self, results):
        """Generate scan report"""
        report = "📊 *HASIL PROFESSIONAL SCAN*\n"
        report += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        report += f"📋 Total: {len(results)} saham\n"
        report += "=" * 35 + "\n\n"
        
        for r in results:
            emoji = self._get_signal_emoji(r['trading_signal'])
            report += f"{emoji} *{r['ticker']}* - Rp {r['price']:,.0f}\n"
            report += f"Signal: {r['trading_signal']}\n"
            report += f"Score: {r['total_score']}/20\n"
            report += f"Trend: {r['trend_strength']}\n"
            report += f"Momentum: {r['momentum_status']}\n"
            report += f"Volume: {r['volume_status']}\n"
            report += "─" * 35 + "\n\n"
        
        return report
    
    def _generate_detailed_report(self, analysis):
        """Generate detailed analysis report"""
        report = f"🔬 *ANALISIS MENDALAM: {analysis['ticker']}*\n"
        report += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        report += "=" * 40 + "\n\n"
        
        # Price Info
        report += f"💰 *HARGA & PERGERAKAN*\n"
        report += f"Harga: Rp {analysis['price']:,.0f}\n"
        report += f"Change: {analysis['change']:.2f}%\n"
        report += f"Volume: {analysis['volume']:,.0f}\n\n"
        
        # Trading Signal
        emoji = self._get_signal_emoji(analysis['trading_signal'])
        report += f"🎯 *TRADING SIGNAL*\n"
        report += f"{emoji} {analysis['trading_signal']}\n"
        report += f"Score: {analysis['total_score']}/20\n\n"
        
        # Entry & Targets
        report += f"📍 *ENTRY & TARGETS*\n"
        report += f"Entry Zone: {analysis['entry_point']}\n"
        report += f"Target 1: {analysis['target_price']}\n"
        report += f"Stop Loss: {analysis['stop_loss']}\n"
        report += f"R:R Ratio: {analysis['risk_reward']}\n\n"
        
        # Trend Analysis
        report += f"📈 *TREND ANALYSIS*\n"
        report += f"Trend: {analysis['trend_strength']}\n"
        report += f"ADX: {analysis['adx']:.2f}\n"
        report += f"SuperTrend: {analysis['supertrend_signal']}\n\n"
        
        # Momentum
        report += f"⚡ *MOMENTUM*\n"
        report += f"Status: {analysis['momentum_status']}\n"
        report += f"RSI: {analysis['rsi']:.2f}\n"
        report += f"Stochastic: {analysis['stochastic']:.2f}\n"
        report += f"CCI: {analysis['cci']:.2f}\n\n"
        
        # Volume Analysis
        report += f"📊 *VOLUME ANALYSIS*\n"
        report += f"Status: {analysis['volume_status']}\n"
        report += f"OBV Trend: {analysis['obv_trend']}\n"
        report += f"MFI: {analysis['mfi']:.2f}\n\n"
        
        # Support & Resistance
        report += f"🎯 *SUPPORT & RESISTANCE*\n"
        report += f"Resistance: Rp {analysis['resistance']:,.0f}\n"
        report += f"Support: Rp {analysis['support']:,.0f}\n\n"
        
        # Key Signals
        report += f"🔑 *KEY SIGNALS*\n"
        for signal in analysis['key_signals'][:5]:
            report += f"• {signal}\n"
        
        return report
    
    def _generate_portfolio_report(self, portfolio):
        """Generate portfolio report"""
        report = "💼 *STOCKBIT PORTFOLIO*\n"
        report += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        report += "=" * 35 + "\n\n"
        
        total_value = portfolio.get('total_value', 0)
        total_pl = portfolio.get('total_pl', 0)
        total_pl_pct = portfolio.get('total_pl_pct', 0)
        
        report += f"💰 Total Value: Rp {total_value:,.0f}\n"
        report += f"📈 P/L: Rp {total_pl:,.0f} ({total_pl_pct:.2f}%)\n\n"
        
        holdings = portfolio.get('holdings', [])
        if holdings:
            report += "*Holdings:*\n\n"
            for stock in holdings:
                report += f"*{stock['ticker']}*\n"
                report += f"Lot: {stock['lot']}\n"
                report += f"Avg: Rp {stock['avg_price']:,.0f}\n"
                report += f"Current: Rp {stock['current_price']:,.0f}\n"
                report += f"P/L: {stock['pl_pct']:.2f}%\n"
                report += "─" * 35 + "\n\n"
        
        return report
    
    def _get_signal_emoji(self, signal):
        """Get emoji for signal"""
        if 'STRONG BUY' in signal:
            return '🟢🟢'
        elif 'BUY' in signal:
            return '🟢'
        elif 'STRONG SELL' in signal:
            return '🔴🔴'
        elif 'SELL' in signal:
            return '🔴'
        else:
            return '⚪'
    
    async def _send_top_signals(self, message, results):
        """Send top trading signals"""
        strong_signals = [r for r in results if 'STRONG' in r['trading_signal']]
        
        if strong_signals:
            text = "🎯 *TOP SIGNALS*\n\n"
            for r in strong_signals[:3]:
                emoji = self._get_signal_emoji(r['trading_signal'])
                text += f"{emoji} *{r['ticker']}* - {r['trading_signal']}\n"
                text += f"Entry: {r['entry_point']}\n"
                text += f"Target: {r['target_price']}\n\n"
            
            await message.reply_text(text, parse_mode='Markdown')
    
    def _split_message(self, text, max_length):
        """Split long message"""
        chunks = []
        while text:
            if len(text) <= max_length:
                chunks.append(text)
                break
            
            split_pos = text[:max_length].rfind('\n\n')
            if split_pos == -1:
                split_pos = max_length
            
            chunks.append(text[:split_pos])
            text = text[split_pos:].lstrip()
        
        return chunks

async def scheduled_scan(application):
    """Scheduled automatic scan"""
    while True:
        try:
            now = datetime.now().time()
            
            # Scan at 9:05 AM and 3:55 PM (market hours)
            if (now.hour == 9 and now.minute == 5) or (now.hour == 15 and now.minute == 55):
                logger.info("Running scheduled scan...")
                
                if ADMIN_CHAT_ID:
                    # Send scan results to admin
                    pass
                
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Error in scheduled scan: {e}")
            await asyncio.sleep(60)

def main():
    """Main function"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    bot = TradingBot()
    
    # Register handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("scan", bot.scan_all))
    application.add_handler(CommandHandler("analyze", bot.analyze_ticker))
    application.add_handler(CommandHandler("portfolio", bot.show_portfolio))
    application.add_handler(CommandHandler("watchlist", bot.watchlist_menu))
    application.add_handler(CommandHandler("add", bot.add_to_watchlist))
    application.add_handler(CommandHandler("remove", bot.remove_from_watchlist))
    application.add_handler(CommandHandler("signals", bot.signals_today))
    application.add_handler(CommandHandler("help", bot.help_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(bot.scan_all, pattern="^scan_all$"))
    application.add_handler(CallbackQueryHandler(bot.watchlist_menu, pattern="^show_watchlist$"))
    application.add_handler(CallbackQueryHandler(bot.show_portfolio, pattern="^show_portfolio$"))
    
    logger.info("🤖 Bot starting...")
    
    # Start bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
