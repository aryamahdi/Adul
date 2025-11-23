# 🤖 Professional Stock Scanner Bot

Bot Telegram untuk scanning dan analisis saham Indonesia (IDX) dengan 20+ indikator teknikal profesional untuk swing trading.

## 🎯 Features

### Analisis Teknikal Lengkap
- **20+ Indikator Profesional**
  - Trend: EMA, SMA, SuperTrend, ADX, MACD
  - Momentum: RSI, Stochastic, CCI, Williams %R, ROC
  - Volume: OBV, VWAP, MFI, Volume Analysis
  - Volatility: Bollinger Bands, ATR, Keltner Channels

### Fitur Utama
- ✅ Comprehensive stock screening
- ✅ Real-time technical analysis
- ✅ Trading signals (BUY/SELL/HOLD)
- ✅ Entry, target, dan stop loss otomatis
- ✅ Custom watchlist management
- ✅ Portfolio integration (Stockbit)
- ✅ Auto-scan scheduled
- ✅ Chart generation

## 📋 Prerequisites

- Python 3.9+
- Telegram Bot Token (dari @BotFather)
- **Sectors.app API Key** (dari https://sectors.app/api)
- Railway account (untuk hosting)
- GitHub account

## 🔑 Mendapatkan Sectors API Key

1. Buka [Sectors.app](https://sectors.app/api)
2. Klik **Sign Up** atau **Login**
3. Pilih plan:
   - **Free**: 100 requests/day (untuk testing)
   - **Starter**: $9/month - 10,000 requests/month (recommended untuk personal use)
   - **Pro**: $49/month - 100,000 requests/month
4. Copy API Key dari dashboard
5. Paste ke `.env` file

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/stock-scanner-bot.git
cd stock-scanner-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Buat file `.env`:

```bash
cp .env.example .env
```

Edit `.env` dan isi dengan data Anda:

```
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=123456789
SECTORS_API_KEY=your_sectors_api_key_here
```

### 4. Run Locally (Testing)

```bash
python bot.py
```

## ☁️ Deploy ke Railway

### Step-by-Step Deployment

#### 1. Push ke GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/stock-scanner-bot.git
git push -u origin main
```

#### 2. Deploy di Railway

1. **Buka [Railway.app](https://railway.app)**
2. **Login** dengan GitHub
3. **Create New Project** → **Deploy from GitHub repo**
4. **Select repository**: stock-scanner-bot
5. **Add Environment Variables**:
   - Klik "Variables"
   - Tambahkan semua variable dari `.env`:
     - `BOT_TOKEN`
     - `ADMIN_CHAT_ID`
     - `STOCKBIT_EMAIL` (optional)
     - `STOCKBIT_PASSWORD` (optional)

6. **Deploy!**
   - Railway akan otomatis build dan deploy
   - Bot akan running 24/7

#### 3. Verifikasi Deployment

- Cek logs di Railway dashboard
- Test bot di Telegram dengan `/start`

## 📱 Cara Menggunakan Bot

### Basic Commands

```
/start - Mulai bot
/scan - Scan semua watchlist
/analyze BBCA - Analisis saham BBCA
/watchlist - Kelola watchlist
/add BBCA - Tambah BBCA ke watchlist
/remove BBCA - Hapus BBCA dari watchlist
/signals - Trading signals hari ini
/portfolio - Lihat portfolio Stockbit
/help - Bantuan lengkap
```

### Workflow Umum

1. **Setup Watchlist**
   ```
   /add BBCA
   /add BBRI
   /add TLKM
   ```

2. **Scan Saham**
   ```
   /scan
   ```

3. **Analisis Detail**
   ```
   /analyze BBCA
   ```

4. **Cek Signals**
   ```
   /signals
   ```

## 🎯 Data Source

Bot ini menggunakan **Sectors.app API** sebagai sumber data utama:
- ✅ 99% coverage saham Indonesia Stock Exchange (IDX)
- ✅ Real-time price data (updated daily)
- ✅ Company financials & fundamentals
- ✅ Top gainers/losers
- ✅ Most active stocks
- ✅ Historical data
- ✅ IHSG (IDX Composite) data

Plus **Yahoo Finance** untuk historical technical analysis data.

## 💼 Portfolio Management

Karena broker Indonesia tidak menyediakan public API, bot ini menggunakan **manual portfolio tracking**:

```
# Tambah saham ke portfolio
/addholding BBCA 5 8500
# (Ticker, Jumlah Lot, Harga Rata-rata)

# Lihat portfolio dengan P/L real-time
/portfolio

# Hapus saham dari portfolio
/removeholding BBCA
```

Portfolio akan dihitung P/L nya menggunakan harga real-time dari Sectors API.

### Scheduled Scanning

Bot akan otomatis scan pada:
- 09:05 WIB (market open)
- 15:55 WIB (before market close)

Edit di `bot.py` untuk mengubah jadwal.

### Custom Indicators

Edit `scanner.py` untuk menambah/modifikasi indikator:

```python
# Tambah indikator baru
df['YOUR_INDICATOR'] = calculate_your_indicator(df)
```

### Database Integration (Production)

Untuk production dengan banyak user, gunakan PostgreSQL:

```bash
# Install psycopg2
pip install psycopg2-binary

# Add to requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
```

Tambahkan `DATABASE_URL` di Railway environment variables.

## 📊 Interpretasi Analisis

### Score System

| Score | Signal | Action |
|-------|--------|--------|
| +15 to +20 | STRONG BUY | 🟢🟢 Entry agresif |
| +8 to +14 | BUY | 🟢 Entry dengan konfirmasi |
| -7 to +7 | HOLD | ⚪ Tunggu sinyal lebih jelas |
| -8 to -14 | SELL | 🔴 Exit posisi |
| -15 to -20 | STRONG SELL | 🔴🔴 Exit segera |

### Trading Signals Explanation

**STRONG BUY**: Kombinasi sempurna dari:
- Trend kuat (ADX > 25)
- Momentum oversold turning up
- Volume confirmation tinggi
- Price near support

**BUY**: Mayoritas indikator bullish tetapi kurang konfirmasi

**HOLD**: Sinyal campuran, tunggu konfirmasi lebih jelas

**SELL/STRONG SELL**: Kebalikan dari buy signals

## 🛠️ Troubleshooting

### Bot tidak respond

1. Cek Railway logs
2. Pastikan BOT_TOKEN benar
3. Restart deployment di Railway

### Data tidak akurat

1. Yahoo Finance mungkin delay
2. Cek koneksi internet
3. Verifikasi ticker code (harus format: BBCA.JK)

### Error "Ticker not found"

Pastikan format kode saham benar:
- Indonesia: `BBCA` (bot akan otomatis tambah .JK)
- US stocks: `AAPL`

## 📈 Best Practices Swing Trading

1. **Entry**: Tunggu konfirmasi dari multiple indikator
2. **Risk Management**: Selalu set stop loss
3. **Position Sizing**: Maksimal 5% per trade
4. **Holding Period**: 3-7 hari untuk swing trade
5. **Target**: Minimal R:R ratio 1:1.5

## ⚠️ Disclaimer

Bot ini adalah **tools bantu analisis**, bukan financial advice. 

- Keputusan trading sepenuhnya tanggung jawab user
- Past performance tidak menjamin future results
- Selalu gunakan risk management yang baik
- Konsultasikan dengan financial advisor

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

MIT License - feel free to use for personal/commercial projects

## 📞 Support

- Issues: [GitHub Issues](https://github.com/your-username/stock-scanner-bot/issues)
- Email: your.email@example.com
- Telegram: @yourusername

## 🔄 Updates

### Version 1.0.0 (Current)
- Initial release
- 20+ technical indicators
- Railway deployment support
- Stockbit integration

### Roadmap
- [ ] Database untuk multi-user
- [ ] Backtesting feature
- [ ] Alert notifications
- [ ] Machine learning predictions
- [ ] Mobile app

---

**Made with ❤️ for Indonesian traders**

**⭐ Star repo ini jika bermanfaat!**
