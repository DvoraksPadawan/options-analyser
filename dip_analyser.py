import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_30min_data(ticker_symbol, days_back=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(interval="30m", start=start_date, end=end_date)
    
    return df

def analyze_candles(df, change_threshold, target_drop):
    # Calculate percentage change for each candle
    df['pct_change'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    
    # Create a column with day's closing price
    df['date'] = df.index.date
    df['daily_close'] = df.groupby('date')['Close'].transform('last')
    
    # Separate positive and negative changes
    positive_candles = df[df['pct_change'] >= change_threshold]
    negative_candles = df[df['pct_change'] <= -change_threshold]
    
    # Calculate percentage change from candle close to day close
    for dataset in [positive_candles, negative_candles]:
        dataset['to_day_close_pct'] = (
            (dataset['daily_close'] - dataset['Close']) / 
            dataset['Close']
        ) * 100
    
    # Count cases where price dropped by target_drop or more
    pos_drop_cases = positive_candles[
        positive_candles['to_day_close_pct'] <= -target_drop
    ]
    neg_drop_cases = negative_candles[
        negative_candles['to_day_close_pct'] <= -target_drop
    ]
    
    return {
        'positive': (len(positive_candles), len(pos_drop_cases)),
        'negative': (len(negative_candles), len(neg_drop_cases))
    }

def main():
    # User inputs
    ticker = input("Enter stock ticker symbol (e.g., AAPL): ").upper()
    change_threshold = float(input("Enter minimum % change threshold (e.g., 0.5): "))
    target_drop = float(input("Enter target % drop to day close (e.g., 1.0): "))
    days = int(input("Enter number of days to analyze (e.g., 30): "))
    
    try:
        # Get data
        print(f"Downloading data for {ticker}...")
        df = get_30min_data(ticker, days)
        
        if df.empty:
            print("No data available for this ticker.")
            return
            
        # Analyze
        results = analyze_candles(df, change_threshold, target_drop)
        
        # Print results
        print(f"\nAnalysis for {ticker} over {days} days:")
        
        print(f"\nCandles with ≥ +{change_threshold}% change:")
        pos_total, pos_drops = results['positive']
        print(f"Total cases: {pos_total}")
        print(f"Cases with ≥ {target_drop}% drop by day close: {pos_drops}")
        if pos_total > 0:
            pos_pct = (pos_drops / pos_total) * 100
            print(f"Percentage: {pos_pct:.2f}%")
        else:
            print("No cases found")
            
        print(f"\nCandles with ≥ -{change_threshold}% change:")
        neg_total, neg_drops = results['negative']
        print(f"Total cases: {neg_total}")
        print(f"Cases with ≥ {target_drop}% drop by day close: {neg_drops}")
        if neg_total > 0:
            neg_pct = (neg_drops / neg_total) * 100
            print(f"Percentage: {neg_pct:.2f}%")
        else:
            print("No cases found")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()