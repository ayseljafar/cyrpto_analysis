from binance.client import Client
import pandas as pd
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
import time
from sqlalchemy import create_engine, Table, Column, Integer, Float, DateTime, MetaData, String
from sqlalchemy.dialects.postgresql import insert
from db_config import get_connection_string

# Define all trading pairs
TRADING_PAIRS = [
    'BTCUSDT',  # Bitcoin
    'ETHUSDT',  # Ethereum
    'SOLUSDT',  # Solana
    'ADAUSDT',  # Cardano
    'DOGEUSDT', # Dogecoin
    'SHIBUSDT', # Shiba Inu
    'USDCUSDT'  # USDC
]

def create_db_tables(engine):
    metadata = MetaData()
    
    # Create crypto_prices table
    crypto_prices = Table(
        'crypto_prices', metadata,
        Column('id', Integer, primary_key=True),
        Column('symbol', String(20), nullable=False),
        Column('date', DateTime(timezone=True), nullable=False),
        Column('price', Float, nullable=False),
    )
    
    # Add TimescaleDB hypertable
    metadata.create_all(engine)
    
    # Convert to TimescaleDB hypertable if TimescaleDB is installed
    try:
        with engine.connect() as connection:
            connection.execute("""
                SELECT create_hypertable('crypto_prices', 'date', 
                if_not_exists => TRUE);
            """)
            # Create index on symbol and date
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_date ON crypto_prices (symbol, date DESC);
            """)
            connection.commit()
    except Exception as e:
        print("Note: TimescaleDB extension not available. Running as regular PostgreSQL table.")
        print(f"Error: {e}")

def get_historical_data(symbol, start_date, end_date=None):
    # Initialize Binance client
    client = Client()
    
    try:
        # Convert dates to milliseconds timestamp
        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000) if end_date else int(time.time() * 1000)
        
        # Get klines/candlestick data
        klines = client.get_historical_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            start_str=start_ts,
            end_str=end_ts
        )
        
        if not klines:
            print(f"No data found for {symbol}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Convert price columns to float
        price_columns = ['open', 'high', 'low', 'close']
        df[price_columns] = df[price_columns].astype(float)
        
        return df
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_daily_price_at_1730(df, symbol):
    if df is None:
        return None
        
    # Convert timestamp to UTC
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
    
    # Create a mask for rows at 17:30
    mask = (df['timestamp'].dt.hour == 17) & (df['timestamp'].dt.minute == 0)
    
    # Filter data for 17:30
    daily_prices = df[mask].copy()
    
    if daily_prices.empty:
        print(f"No data at 17:30 UTC for {symbol}")
        return None
    
    # Keep only relevant columns and add symbol
    daily_prices = daily_prices[['timestamp', 'close']]
    daily_prices.columns = ['date', 'price']
    daily_prices['symbol'] = symbol
    
    return daily_prices

def save_to_database(df, engine):
    if df is not None and not df.empty:
        try:
            # Save to database
            df.to_sql('crypto_prices', engine, if_exists='append', index=False,
                     method='multi', chunksize=1000)
            return len(df)
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return 0
    return 0

def main():
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - relativedelta(years=8)
    
    print("Initializing database connection...")
    engine = create_engine(get_connection_string())
    
    # Create tables if they don't exist
    create_db_tables(engine)
    
    total_records = 0
    
    # Process each trading pair
    for symbol in TRADING_PAIRS:
        print(f"\nProcessing {symbol}...")
        print(f"Fetching data from {start_date} to {end_date}")
        
        # Get historical data
        df = get_historical_data(symbol, start_date, end_date)
        
        # Get daily prices at 17:30
        daily_prices = get_daily_price_at_1730(df, symbol)
        
        # Save to database
        if daily_prices is not None:
            print(f"Saving {symbol} data to database...")
            records_saved = save_to_database(daily_prices, engine)
            total_records += records_saved
            
            # Save to CSV as backup
            output_file = f"data/{symbol}_daily_1730_prices.csv"
            daily_prices.to_csv(output_file, index=False)
            print(f"Backup saved to {output_file}")
            print(f"Saved {records_saved} records for {symbol}")
        
        # Add a small delay to avoid hitting rate limits
        time.sleep(1)
    
    print(f"\nProcess completed! Total records saved: {total_records}")

if __name__ == "__main__":
    main() 