# AI Trading Insights

Get real-time stock analysis with AI-powered trading insights. Free, fast, and simple.

## Course Project

**Module:** Deep Learning et intelligence Artificielle Générative
**Students:** Fatima Ezzahraa Abbari, Mariem Tahramt  
**Professor:** OUTMAN Haddani  
**Masters Program:** Finance, Actuariat et Data Science


---

## What It Does

Fetches stock prices and automatically generates trading insights:

```
GOOGL: Close $319.95, Change -1.08%
→ UPTREND (10d MA above 30d MA) | Watch for pullback

TSLA: Close $426.58, Change +1.71%
→ DOWNTREND (10d MA below 30d MA) | Possible reversal forming
```

## How It Works

1. **Get Stock Data** → Fetches 30 days of price history from Polygon.io (now Massive)
2. **Calculate Indicators** → Computes 10-day and 30-day moving averages
3. **Generate Insight** → Analyzes trend and creates trading recommendation
4. **Optional Storage** → Saves results to S3 for tracking (optional)

## Setup (5 minutes)

### 1. Get API Keys

**Polygon.io / Massive** (stock prices)
- Go to: https://polygon.io/
- Sign up (free tier)
- Copy your API key
- Note: Polygon is transitioning to Massive platform

**Hugging Face** (optional AI enhancement)
- Go to: https://huggingface.co/
- Sign up → Settings → Tokens → Create new token
- Choose "Read" permission
- Copy token

### 2. Install & Configure

```bash
# Install packages
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env and paste your keys:
# POLYGON_API_KEY=your_key_here
# HF_API_TOKEN=your_token_here
```

### 3. Run It

```bash
# Single stock
python stock_analyzer.py AAPL

# Multiple stocks (13-second delays between requests)
python stock_analyzer.py GOOGL TSLA MSFT

# Save to S3 (if configured)
python stock_analyzer.py AAPL --save-s3
```

**Output:**
```
============================================================
Analyzing: GOOGL
============================================================

Stock Data:
  Latest Close: $319.95
  Daily Change: -1.08%
  SMA(10d):     $296.82
  SMA(30d):     $289.65
  Avg Volume (10d): 59,250,020

AI Insight:
  GOOGL is in UPTREND (10d MA above 30d MA) | Watch for pullback

============================================================
```

## How It Works

1. **Stock Data** → Polygon.io API fetches last 30 days of daily aggregates
2. **Indicators** → Script computes SMA-10, SMA-30, daily % change, average volume
3. **Prompt** → Data is formatted into a concise text prompt
4. **AI Analysis** → Prompt sent to Hugging Face Inference API (flan-t5-small model)
5. **Insight** → Model generates a plain-English trading recommendation
6. **Optional S3 Storage** → Results persisted to S3-compatible bucket (Massive) for historical tracking

## S3 Integration (Optional)

To save analysis results to S3 for historical tracking:

1. Add S3 credentials to `.env`:
   ```
   S3_ACCESS_KEY=your_access_key
   S3_SECRET_KEY=your_secret_key
   S3_ENDPOINT=https://files.massive.com
   S3_BUCKET=your_bucket_name
   ```

2. Run with `--save-s3` flag:
   ```bash
   python stock_analyzer.py AAPL --save-s3
   ```

3. Results are stored at: `s3://bucket/analyses/TICKER/YYYY-MM-DDTHH-MM-SS.json`

## Files

- `stock_analyzer.py` — Main analysis script
- `requirements.txt` — Python dependencies
- `.env.example` — API key template
- `.env` — Your actual API keys (create this, don't commit)

## Free Tier Limitations & Rate Limits

| Service | Rate Limit | How Script Handles It |
|---------|-----------|-------|
| Polygon.io (Massive) | 5 calls/min | Waits 13 seconds between requests |
| Hugging Face | ~1 req/sec | Optional; falls back to technical analysis if unavailable |

## What are Polygon.io / Massive and Hugging Face?

**Polygon.io / Massive**
- Financial data API for stocks, crypto, currencies
- Free tier: real-time & historical prices
- 5 API calls/min (script auto-waits 13 seconds between tickers)
- Transitioning from Polygon.io to Massive platform

**Hugging Face**
- Free AI model hosting & inference API
- Provides free API calls for learning/testing
- Script tries it for smarter insights, falls back to technical analysis if unavailable
- No GPU needed—runs on their servers

## Understanding the Insights

```
GOOGL is in UPTREND (10d MA above 30d MA) | Watch for pullback
↑                                          ↑
Trend Signal                              Price Action

TSLA is in DOWNTREND (10d MA below 30d MA) | Possible reversal forming
↑                                           ↑
Downtrend                                  Recovery Signal
```

## Tested & Working

✅ Real stock data from Polygon.io
✅ Rate limiting (13-second delays)
✅ Technical analysis insights (moving averages, trend detection)
✅ Multiple stocks in one run
✅ Optional S3 storage (Massive bucket)

## Next Steps

- Run with your stocks: `python stock_analyzer.py MSFT AMZN NVDA`
- Check insights daily for trading signals
- Set up S3 storage to track historical trends
- Extend with more indicators (RSI, MACD, Bollinger Bands) if needed

## Course Learning Outcomes

This project demonstrates:

- **API Integration** → Connecting to multiple free APIs (Polygon.io, Hugging Face)
- **Data Processing** → Fetching, parsing, and analyzing financial data
- **AI Implementation** → Using Hugging Face models for AI insights
- **Cloud Storage** → S3/Massive for data persistence
- **Rate Limiting & Error Handling** → Managing API constraints gracefully
- **Python Best Practices** → Clean code, modular design, environment variables

## Project Structure

```
ai-trading-insights/
├── stock_analyzer.py      # Main script (270+ lines)
├── requirements.txt       # Dependencies (requests, boto3, python-dotenv)
├── .env.example          # API key template
├── .env                  # Your actual keys (not committed)
└── README.md             # This file
```

## Key Technologies

| Technology | Purpose | Why Used |
|-----------|---------|----------|
| Python | Core language | Simplicity, data processing |
| Polygon.io/Massive | Stock data API | Free, reliable, real-time |
| Hugging Face | AI insights | Free inference, no GPU needed |
| boto3 | S3 storage | Data persistence, cloud integration |
| python-dotenv | Config management | Secure API key handling |

## License

free for personal use 

