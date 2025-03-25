-- Basic Queries --

-- 1. Latest prices for all cryptocurrencies
SELECT DISTINCT ON (symbol) 
    symbol, 
    date, 
    price 
FROM crypto_prices 
ORDER BY symbol, date DESC;

-- 2. Get recent prices for a specific cryptocurrency (change BTCUSDT to any symbol)
SELECT date, price 
FROM crypto_prices 
WHERE symbol = 'BTCUSDT' 
ORDER BY date DESC 
LIMIT 10;

-- Monthly Analysis --

-- 3. Monthly average prices with high/low
SELECT 
    symbol,
    date_trunc('month', date) as month,
    round(avg(price)::numeric, 2) as average_price,
    max(price) as highest_price,
    min(price) as lowest_price,
    round((max(price) - min(price))::numeric, 2) as price_range
FROM crypto_prices 
GROUP BY symbol, date_trunc('month', date)
ORDER BY symbol, month DESC;

-- Price Statistics --

-- 4. Overall statistics for each cryptocurrency
SELECT 
    symbol,
    round(max(price)::numeric, 2) as highest_price,
    round(min(price)::numeric, 2) as lowest_price,
    round(avg(price)::numeric, 2) as average_price,
    round(stddev(price)::numeric, 2) as price_volatility
FROM crypto_prices 
GROUP BY symbol
ORDER BY symbol;

-- Price Changes --

-- 5. Weekly price changes
WITH latest_prices AS (
    SELECT 
        symbol,
        date,
        price,
        LAG(price, 7) OVER (PARTITION BY symbol ORDER BY date) as price_7_days_ago
    FROM crypto_prices
)
SELECT 
    symbol,
    date,
    round(price::numeric, 2) as current_price,
    round(price_7_days_ago::numeric, 2) as price_7_days_ago,
    round(((price - price_7_days_ago) / price_7_days_ago * 100)::numeric, 2) as price_change_percentage
FROM latest_prices
WHERE price_7_days_ago IS NOT NULL
ORDER BY date DESC, symbol;

-- Data Coverage --

-- 6. Data availability for each cryptocurrency
SELECT 
    symbol,
    count(*) as number_of_days,
    min(date) as earliest_date,
    max(date) as latest_date,
    round((max(price) - min(price))::numeric, 2) as total_price_range
FROM crypto_prices
GROUP BY symbol
ORDER BY symbol;

-- Significant Price Movements --

-- 7. Days with significant price changes (>5%)
WITH daily_changes AS (
    SELECT 
        symbol,
        date,
        price,
        LAG(price, 1) OVER (PARTITION BY symbol ORDER BY date) as previous_day_price
    FROM crypto_prices
)
SELECT 
    symbol,
    date,
    round(price::numeric, 2) as price,
    round(previous_day_price::numeric, 2) as previous_day_price,
    round(((price - previous_day_price) / previous_day_price * 100)::numeric, 2) as price_change_percentage
FROM daily_changes
WHERE ABS((price - previous_day_price) / previous_day_price * 100) > 5
ORDER BY ABS((price - previous_day_price) / previous_day_price * 100) DESC;

-- Price Correlations --

-- 8. Price correlation between BTC and other cryptocurrencies
WITH daily_returns AS (
    SELECT 
        date,
        symbol,
        (price - LAG(price) OVER (PARTITION BY symbol ORDER BY date)) / LAG(price) OVER (PARTITION BY symbol ORDER BY date) as daily_return
    FROM crypto_prices
)
SELECT 
    a.symbol as crypto_1,
    b.symbol as crypto_2,
    round(corr(a.daily_return, b.daily_return)::numeric, 3) as correlation
FROM daily_returns a
JOIN daily_returns b ON a.date = b.date
WHERE a.symbol = 'BTCUSDT' AND b.symbol != 'BTCUSDT'
GROUP BY a.symbol, b.symbol
ORDER BY correlation DESC;

-- Time-based Analysis --

-- 9. Average prices by day of week
SELECT 
    symbol,
    EXTRACT(DOW FROM date) as day_of_week,
    round(avg(price)::numeric, 2) as average_price,
    count(*) as number_of_observations
FROM crypto_prices
GROUP BY symbol, EXTRACT(DOW FROM date)
ORDER BY symbol, day_of_week;

-- Custom Date Range Analysis --

-- 10. Price analysis for specific date range (change dates as needed)
SELECT 
    symbol,
    round(min(price)::numeric, 2) as lowest_price,
    round(max(price)::numeric, 2) as highest_price,
    round(avg(price)::numeric, 2) as average_price,
    round(stddev(price)::numeric, 2) as price_volatility
FROM crypto_prices
WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY symbol
ORDER BY symbol; 