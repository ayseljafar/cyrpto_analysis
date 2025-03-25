from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
from db_config import get_connection_string
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Database connection
engine = create_engine(get_connection_string())

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Cryptocurrency Price API"})

@app.route('/cryptocurrencies')
def get_cryptocurrencies():
    """Get list of all available cryptocurrencies"""
    query = "SELECT DISTINCT symbol FROM crypto_prices ORDER BY symbol"
    with engine.connect() as conn:
        result = conn.execute(text(query))
        cryptos = [row[0] for row in result]
    return jsonify({"cryptocurrencies": cryptos})

@app.route('/prices/<symbol>')
def get_crypto_prices(symbol):
    """Get historical prices for a specific cryptocurrency"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = min(int(request.args.get('limit', 100)), 1000)
    
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
        prices = [{"date": str(row[0]), "price": float(row[1])} for row in result]
        
    if not prices:
        return jsonify({"error": f"No data found for {symbol}"}), 404
    
    return jsonify({"symbol": symbol, "prices": prices})

@app.route('/statistics/<symbol>')
def get_crypto_statistics(symbol):
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
            return jsonify({"error": f"No data found for {symbol}"}), 404
        
        return jsonify({
            "symbol": symbol,
            "statistics": {
                "total_days": result[0],
                "min_price": float(result[1]),
                "max_price": float(result[2]),
                "avg_price": float(result[3]),
                "earliest_date": str(result[4]),
                "latest_date": str(result[5])
            }
        })

@app.route('/monthly-analysis/<symbol>')
def get_monthly_analysis(symbol):
    """Get monthly price analysis for a specific cryptocurrency"""
    months = min(int(request.args.get('months', 12)), 60)
    
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
            "month": str(row[0]),
            "avg_price": float(row[1]),
            "max_price": float(row[2]),
            "min_price": float(row[3]),
            "price_range": float(row[4])
        } for row in result]
        
    if not analysis:
        return jsonify({"error": f"No monthly data found for {symbol}"}), 404
    
    return jsonify({"symbol": symbol, "monthly_analysis": analysis})

@app.route('/price-changes/<symbol>')
def get_price_changes(symbol):
    """Get price changes over specified number of days"""
    days = min(int(request.args.get('days', 7)), 365)
    
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
            "date": str(row[0]),
            "current_price": float(row[1]),
            "previous_price": float(row[2]),
            "change_percent": float(row[3])
        } for row in result]
        
    if not changes:
        return jsonify({"error": f"No price change data found for {symbol}"}), 404
    
    return jsonify({"symbol": symbol, "price_changes": changes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 