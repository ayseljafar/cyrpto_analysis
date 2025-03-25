import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from db_config import get_connection_string

def load_data_from_csv_files():
    """Load data from CSV files for each cryptocurrency"""
    all_data = []
    
    # Read each CSV file
    for symbol in TRADING_PAIRS:
        try:
            df = pd.read_csv(f"data/{symbol}_daily_1730_prices.csv")
            all_data.append(df)
        except FileNotFoundError:
            print(f"Warning: {symbol}_daily_1730_prices.csv not found in data directory")
    
    if not all_data:
        raise FileNotFoundError("No CSV files found in data directory")
    
    return pd.concat(all_data, ignore_index=True)

def monthly_analysis(df):
    """Calculate monthly statistics for each cryptocurrency"""
    # Convert date to month start
    df['month'] = df['date'].dt.to_period('M')
    
    # Group by symbol and month
    monthly_stats = df.groupby(['symbol', 'month']).agg({
        'price': ['mean', 'max', 'min']
    }).round(2)
    
    # Calculate price range
    monthly_stats['price_range'] = monthly_stats['price']['max'] - monthly_stats['price']['min']
    
    # Flatten column names
    monthly_stats.columns = ['average_price', 'highest_price', 'lowest_price', 'price_range']
    
    return monthly_stats.reset_index()

def price_statistics(df):
    """Calculate overall price statistics for each cryptocurrency"""
    stats = df.groupby('symbol').agg({
        'price': [
            'count',
            'mean',
            'std',
            'min',
            'max'
        ]
    }).round(2)
    
    stats.columns = ['count', 'average_price', 'volatility', 'lowest_price', 'highest_price']
    return stats.reset_index()

def weekly_price_changes(df):
    """Calculate weekly price changes for each cryptocurrency"""
    # Sort data
    df = df.sort_values(['symbol', 'date'])
    
    # Calculate 7-day price change
    weekly_changes = df.groupby('symbol').apply(
        lambda x: pd.DataFrame({
            'date': x['date'],
            'current_price': x['price'],
            'price_7_days_ago': x['price'].shift(7),
            'price_change_pct': ((x['price'] - x['price'].shift(7)) / x['price'].shift(7) * 100).round(2)
        })
    ).reset_index(level=0)
    
    return weekly_changes[weekly_changes['price_7_days_ago'].notna()]

def plot_price_trends(df):
    """Create price trend plots for each cryptocurrency"""
    fig = px.line(df, x='date', y='price', color='symbol',
                  title='Cryptocurrency Price Trends',
                  labels={'date': 'Date', 'price': 'Price (USDT)', 'symbol': 'Cryptocurrency'})
    fig.write_html('crypto_trends.html')

def main():
    # Load data
    print("Loading cryptocurrency data...")
    df = load_data_from_csv_files()
    
    if df is None:
        print("No data found. Please run the data collection script first.")
        return
    
    # Monthly analysis
    print("\nCalculating monthly statistics...")
    monthly_stats = monthly_analysis(df)
    print("\nMonthly Statistics (last 5 months):")
    print(monthly_stats.tail())
    
    # Overall price statistics
    print("\nOverall Price Statistics:")
    stats = price_statistics(df)
    print(stats)
    
    # Weekly price changes
    print("\nRecent Weekly Price Changes:")
    weekly_changes = weekly_price_changes(df)
    print(weekly_changes.tail())
    
    # Create visualizations
    print("\nCreating price trend visualization...")
    plot_price_trends(df)
    
    # Save analyses to CSV files
    print("\nSaving analyses to files...")
    monthly_stats.to_csv('data/monthly_analysis.csv', index=False)
    stats.to_csv('data/overall_statistics.csv', index=False)
    weekly_changes.to_csv('data/weekly_changes.csv', index=False)
    
    print("\nAnalysis complete! Check the data directory for CSV files and crypto_trends.html for results.")

if __name__ == "__main__":
    main() 