#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL (change this if using different port)
API_URL="http://localhost:8000"  # For FastAPI
# API_URL="http://localhost:5000"  # For Flask

echo -e "${BLUE}Testing Cryptocurrency API Endpoints${NC}\n"

# Test 1: Get all cryptocurrencies
echo -e "${GREEN}1. Getting list of all cryptocurrencies...${NC}"
curl -s "${API_URL}/cryptocurrencies" | json_pp
echo -e "\n"

# Test 2: Get BTC prices for last 5 days
echo -e "${GREEN}2. Getting recent BTC prices (last 5 entries)...${NC}"
curl -s "${API_URL}/prices/BTCUSDT?limit=5" | json_pp
echo -e "\n"

# Test 3: Get ETH statistics
echo -e "${GREEN}3. Getting ETH statistics...${NC}"
curl -s "${API_URL}/statistics/ETHUSDT" | json_pp
echo -e "\n"

# Test 4: Get monthly analysis for SOL (last 3 months)
echo -e "${GREEN}4. Getting monthly analysis for SOL (last 3 months)...${NC}"
curl -s "${API_URL}/monthly-analysis/SOLUSDT?months=3" | json_pp
echo -e "\n"

# Test 5: Get price changes for ADA (7-day change)
echo -e "${GREEN}5. Getting 7-day price changes for ADA...${NC}"
curl -s "${API_URL}/price-changes/ADAUSDT?days=7" | json_pp
echo -e "\n"

# Test 6: Get prices with date range
echo -e "${GREEN}6. Getting BTC prices for specific date range...${NC}"
curl -s "${API_URL}/prices/BTCUSDT?start_date=2023-01-01&end_date=2023-12-31&limit=5" | json_pp
echo -e "\n"

# Test 7: Get DOGE monthly analysis with custom months
echo -e "${GREEN}7. Getting DOGE monthly analysis (6 months)...${NC}"
curl -s "${API_URL}/monthly-analysis/DOGEUSDT?months=6" | json_pp
echo -e "\n"

# Test error handling
echo -e "${GREEN}8. Testing error handling (invalid symbol)...${NC}"
curl -s "${API_URL}/prices/INVALIDCOIN" | json_pp
echo -e "\n"

echo -e "${BLUE}API Testing Complete!${NC}"

# Optional: Save responses to files
echo -e "${GREEN}Saving responses to files...${NC}"
mkdir -p api_responses

# Save each response to a separate file
curl -s "${API_URL}/cryptocurrencies" > api_responses/cryptocurrencies.json
curl -s "${API_URL}/prices/BTCUSDT?limit=100" > api_responses/btc_prices.json
curl -s "${API_URL}/statistics/ETHUSDT" > api_responses/eth_stats.json
curl -s "${API_URL}/monthly-analysis/SOLUSDT?months=12" > api_responses/sol_monthly.json
curl -s "${API_URL}/price-changes/ADAUSDT?days=30" > api_responses/ada_changes.json

echo -e "${BLUE}Responses saved to 'api_responses' directory${NC}"

# Function to check API health
check_api_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}")
    if [ $response -eq 200 ]; then
        echo -e "${GREEN}API is running and healthy${NC}"
    else
        echo -e "\033[0;31mAPI is not responding properly (HTTP $response)${NC}"
    fi
}

# Check API health
echo -e "\n${GREEN}Checking API health...${NC}"
check_api_health 