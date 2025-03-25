from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from db_config import get_connection_string
import uvicorn

app = FastAPI(
    title="Cryptocurrency Price API",
    description="API for accessing historical cryptocurrency price data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
engine = create_engine(get_connection_string())

@app.get("/")
async def root():
    return {"message": "Welcome to the Cryptocurrency Price API"}

@app.get("/cryptocurrencies")
async def get_available_cryptocurrencies():
    """Get list of all available cryptocurrencies"""
    query = "SELECT DISTINCT symbol FROM crypto_prices ORDER BY symbol"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        cryptos = [row[0] for row in result]
    return {"cryptocurrencies": cryptos}

@app.get("/prices/{symbol}")
async def get_crypto_prices(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(default=100, le=1000)
):
    """Get historical prices for a specific cryptocurrency"""
    query = """
    SELECT date, price
    FROM crypto_prices
    WHERE symbol = :symbol
    """
    params = {"symbol": symbol}
    
    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date
    
    query += " ORDER BY date DESC LIMIT :limit"
    params["limit"] = limit

    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        prices = [{"date": row[0], "price": float(row[1])} for row in result]
        
    if not prices:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    return {"symbol": symbol, "prices": prices}

@app.get("/statistics/{symbol}")
async def get_crypto_statistics(symbol: str):
    """Get statistical information for a specific cryptocurrency"""
    query = """
    SELECT 
        COUNT(*) as total_days,
        MIN(price) as min_price,
        MAX(price) as max_price,
        AVG(price) as avg_price,
        MIN(date) as earliest_date,
        MAX(date) as latest_date
    FROM crypto_prices
    WHERE symbol = :symbol
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"symbol": symbol}).first()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        return {
            "symbol": symbol,
            "statistics": {
                "total_days": result[0],
                "min_price": float(result[1]),
                "max_price": float(result[2]),
                "avg_price": float(result[3]),
                "earliest_date": result[4],
                "latest_date": result[5]
            }
        }

@app.get("/monthly-analysis/{symbol}")
async def get_monthly_analysis(symbol: str, months: int = Query(default=12, le=60)):
    """Get monthly price analysis for a specific cryptocurrency"""
    query = """
    SELECT 
        DATE_TRUNC('month', date) as month,
        AVG(price) as avg_price,
        MAX(price) as max_price,
        MIN(price) as min_price,
        MAX(price) - MIN(price) as price_range
    FROM crypto_prices
    WHERE symbol = :symbol
    GROUP BY DATE_TRUNC('month', date)
    ORDER BY month DESC
    LIMIT :months
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"symbol": symbol, "months": months})
        analysis = [{
            "month": row[0],
            "avg_price": float(row[1]),
            "max_price": float(row[2]),
            "min_price": float(row[3]),
            "price_range": float(row[4])
        } for row in result]
        
    if not analysis:
        raise HTTPException(status_code=404, detail=f"No monthly data found for {symbol}")
    
    return {"symbol": symbol, "monthly_analysis": analysis}

@app.get("/price-changes/{symbol}")
async def get_price_changes(symbol: str, days: int = Query(default=7, le=365)):
    """Get price changes over specified number of days"""
    query = """
    WITH price_changes AS (
        SELECT 
            date,
            price,
            LAG(price, :days) OVER (ORDER BY date) as previous_price
        FROM crypto_prices
        WHERE symbol = :symbol
    )
    SELECT 
        date,
        price,
        previous_price,
        ((price - previous_price) / previous_price * 100) as price_change_percent
    FROM price_changes
    WHERE previous_price IS NOT NULL
    ORDER BY date DESC
    LIMIT 30
    """
    
    with engine.connect() as conn:
        result = conn.execute(text(query), {"symbol": symbol, "days": days})
        changes = [{
            "date": row[0],
            "current_price": float(row[1]),
            "previous_price": float(row[2]),
            "change_percent": float(row[3])
        } for row in result]
        
    if not changes:
        raise HTTPException(status_code=404, detail=f"No price change data found for {symbol}")
    
    return {"symbol": symbol, "price_changes": changes}

if __name__ == "__main__":
    uvicorn.run("crypto_api_fast:app", host="0.0.0.0", port=8000, reload=True) 