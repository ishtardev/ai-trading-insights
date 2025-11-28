#!/usr/bin/env python3
"""
Stock Ticker Analysis using Polygon.io (free tier) + Hugging Face Inference API.

Free APIs:
- Polygon.io: Free tier gives you access to real-time & historical stock data, aggregates, etc.
  Sign up: https://polygon.io/
  Free tier rate limit: 5 API calls/min (sufficient for this example)

- Hugging Face Inference API: Free tier with limited quota for text generation/summarization.
  Sign up: https://huggingface.co/ and generate API token at https://huggingface.co/settings/tokens

- S3-compatible storage (Massive): Optional S3 endpoint for persisting analysis results.

Usage:
  python stock_analyzer.py AAPL
  python stock_analyzer.py GOOGL
  python stock_analyzer.py AAPL --save-s3  # Save results to S3
"""

import os
import sys
import json
import time
import requests
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# S3 config (optional)
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_BUCKET = os.getenv("S3_BUCKET")

if not POLYGON_API_KEY or not HF_API_TOKEN:
    print("Error: Missing POLYGON_API_KEY or HF_API_TOKEN in .env file")
    print("Please create a .env file with your API keys (see .env.example)")
    sys.exit(1)


def get_s3_client():
    """Initialize S3 client for Massive bucket."""
    if not all([S3_ACCESS_KEY, S3_SECRET_KEY, S3_ENDPOINT, S3_BUCKET]):
        return None
    
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name="us-east-1",
        )
        return s3_client
    except Exception as e:
        print(f"Warning: Could not initialize S3 client: {e}")
        return None


def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch last 30 days of daily aggregates from Polygon.io.
    Returns dict with close, high, low, volume, and computed indicators.
    
    Note: Polygon.io free tier has a 5 requests/min rate limit.
    Script adds 13-second delays between requests to stay within limits.
    """
    try:
        # Polygon.io free tier: 5 requests/min = 1 request per 12 seconds
        # Adding 13 seconds buffer to be safe
        print(f"Fetching data for {ticker}... (waiting for rate limit)")
        time.sleep(13)
        
        # Get last 30 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        url = (
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/"
            f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            f"?adjusted=true&sort=asc&apiKey={POLYGON_API_KEY}"
        )
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Accept both 'OK' and 'DELAYED' statuses (both contain valid data)
        if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
            print(f"Error: API returned status '{data.get('status')}'. Response: {data}")
            return {}
        
        results = data["results"]
        closes = [r["c"] for r in results]
        volumes = [r["v"] for r in results]
        
        latest = closes[-1]
        prev = closes[-2] if len(closes) > 1 else closes[-1]
        
        # Simple indicators
        sma_10 = sum(closes[-10:]) / min(len(closes), 10)
        sma_30 = sum(closes[-30:]) / min(len(closes), 30)
        avg_volume = sum(volumes[-10:]) / min(len(volumes), 10)
        
        daily_change_pct = ((latest - prev) / prev * 100) if prev != 0 else 0
        
        return {
            "ticker": ticker,
            "latest_close": latest,
            "daily_change_pct": daily_change_pct,
            "sma_10": sma_10,
            "sma_30": sma_30,
            "avg_volume_10d": avg_volume,
            "num_days": len(closes),
        }
    
    except requests.RequestException as e:
        print(f"Error fetching data from Polygon.io: {e}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        return {}


def get_ai_insight(data: dict) -> str:
    """
    Generate trading insight from stock data.
    Uses Hugging Face API with fallback to local analysis.
    """
    if not data:
        return "No data available for analysis."
    
    ticker = data["ticker"]
    close = data["latest_close"]
    change = data["daily_change_pct"]
    sma_10 = data["sma_10"]
    sma_30 = data["sma_30"]
    
    # Try HF API first
    if HF_API_TOKEN and HF_API_TOKEN != "your_hf_api_token_here":
        try:
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json",
            }
            
            prompt = (
                f"Ticker: {ticker}, Close: ${close:.2f}, Change: {change:+.2f}%, "
                f"SMA10: ${sma_10:.2f}, SMA30: ${sma_30:.2f}. "
                f"Give 1-sentence trading recommendation:"
            )
            
            # Use a simple text generation endpoint
            url = "https://api-inference.huggingface.co/models/gpt2"
            payload = {"inputs": prompt}
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result and "generated_text" in result[0]:
                    insight = result[0]["generated_text"]
                    # Extract just the new text (after the prompt)
                    if prompt in insight:
                        insight = insight.split(prompt)[-1].strip()
                    return insight[:150] if insight else generate_fallback_insight(ticker, change, sma_10, sma_30)
        except Exception as e:
            # Silently fall back if HF API fails
            pass
    
    # Use local analysis if HF API unavailable
    return generate_fallback_insight(ticker, change, sma_10, sma_30)


def generate_fallback_insight(ticker: str, change: float, sma_10: float, sma_30: float) -> str:
    """Generate a basic trading insight from technical analysis."""
    insights = []
    
    # Trend analysis
    if sma_10 > sma_30:
        insights.append(f"{ticker} is in UPTREND (10d MA above 30d MA)")
        if change > 0:
            insights.append("Positive momentum continues")
        else:
            insights.append("Watch for pullback or consolidation")
    elif sma_10 < sma_30:
        insights.append(f"{ticker} is in DOWNTREND (10d MA below 30d MA)")
        if change < 0:
            insights.append("Downward momentum persists")
        else:
            insights.append("Possible reversal forming")
    else:
        insights.append(f"{ticker} is at inflection point")
    
    # Price action
    if abs(change) > 2:
        insights.append(f"Large move ({change:+.2f}%) - evaluate fundamentals")
    elif abs(change) > 0.5:
        insights.append(f"Moderate movement ({change:+.2f}%)")
    
    # Recommendation
    if sma_10 > sma_30 and change > 0:
        insights.append("Action: HOLD/BUY on dips")
    elif sma_10 > sma_30:
        insights.append("Action: HOLD, watch support")
    elif sma_10 < sma_30 and change < 0:
        insights.append("Action: AVOID or short setup")
    else:
        insights.append("Action: WAIT for confirmation")
    
    return " | ".join(insights[:2])


def save_to_s3(ticker: str, data: dict, insight: str, s3_client) -> bool:
    """Save analysis results to S3-compatible storage (Massive)."""
    if not s3_client:
        return False
    
    try:
        timestamp = datetime.now().isoformat()
        
        analysis_record = {
            "ticker": ticker,
            "timestamp": timestamp,
            "data": data,
            "insight": insight,
        }
        
        # Key format: analyses/AAPL/2025-11-28T15-30-45.json
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H-%M-%S")
        key = f"analyses/{ticker}/{date_str}T{time_str}.json"
        
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(analysis_record, indent=2),
            ContentType="application/json",
        )
        
        print(f"✓ Saved to S3: s3://{S3_BUCKET}/{key}")
        return True
    
    except Exception as e:
        print(f"Warning: Could not save to S3: {e}")
        return False


def print_analysis(ticker: str, save_s3: bool = False):
    """Fetch stock data and print analysis with AI insight."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {ticker}")
    print(f"{'='*60}\n")
    
    data = fetch_stock_data(ticker)
    
    if not data:
        print("Analysis failed. Check your API keys and ticker symbol.")
        return
    
    print(f"Stock Data:")
    print(f"  Latest Close: ${data['latest_close']:.2f}")
    print(f"  Daily Change: {data['daily_change_pct']:+.2f}%")
    print(f"  SMA(10d):     ${data['sma_10']:.2f}")
    print(f"  SMA(30d):     ${data['sma_30']:.2f}")
    print(f"  Avg Volume (10d): {data['avg_volume_10d']:,.0f}")
    print(f"  Data Points: {data['num_days']}")
    
    print(f"\nGenerating AI insight...")
    insight = get_ai_insight(data)
    print(f"\nAI Insight:")
    print(f"  {insight}")
    
    if save_s3:
        print(f"\nSaving to S3...")
        s3_client = get_s3_client()
        save_to_s3(ticker, data, insight, s3_client)
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stock_analyzer.py TICKER [TICKER2 ...] [--save-s3]")
        print("\nExample:")
        print("  python stock_analyzer.py AAPL GOOGL TSLA")
        print("  python stock_analyzer.py AAPL --save-s3")
        sys.exit(1)
    
    save_s3 = "--save-s3" in sys.argv
    tickers = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    for ticker in tickers:
        print_analysis(ticker.upper(), save_s3=save_s3)

