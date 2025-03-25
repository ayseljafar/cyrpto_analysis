# Cryptocurrency Analysis Tool

A Python-based tool for analyzing cryptocurrency price data, generating statistics, and creating interactive visualizations.

This tool performs comprehensive analysis of cryptocurrency price data by:
- Tracking daily price movements and calculating key metrics
- Analyzing monthly trends and price ranges
- Computing volatility and price change statistics
- Generating interactive visualizations for price trends
- Providing both detailed CSV reports and visual insights

## Features

- Load and process cryptocurrency price data from CSV files
- Calculate monthly statistics including average, highest, and lowest prices
- Generate overall price statistics with volatility metrics
- Track weekly price changes and percentage variations
- Create interactive price trend visualizations using Plotly
- Export analysis results to CSV files
- Web interface for data visualization (coming soon)

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (for data storage)
- Binance API access (for data collection)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cyrpto_analysis.git
cd cyrpto_analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

## Project Structure

```
cyrpto_analysis/
├── data/                   # Directory for CSV data files
├── crypto_analysis.py      # Main analysis script
├── data_collector.py       # Script for collecting data from Binance
├── db_config.py           # Database configuration
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Usage

1. Collect cryptocurrency data:
```bash
python data_collector.py
```

2. Run the analysis:
```bash
python crypto_analysis.py
```

The script will:
- Load cryptocurrency price data from CSV files
- Calculate monthly statistics
- Generate overall price statistics
- Track weekly price changes
- Create interactive visualizations
- Save results to CSV files in the data directory

## Output Files

- `data/monthly_analysis.csv`: Monthly statistics for each cryptocurrency
- `data/overall_statistics.csv`: Overall price statistics and volatility metrics
- `data/weekly_changes.csv`: Weekly price changes and percentage variations
- `crypto_trends.html`: Interactive price trend visualization

## Dependencies

- python-binance: Binance API integration
- pandas: Data manipulation and analysis
- sqlalchemy: Database ORM
- plotly: Interactive visualizations
- dash: Web application framework
- fastapi: API framework
- flask: Web server
- Other dependencies listed in requirements.txt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Binance API for providing cryptocurrency data
- Plotly for interactive visualization capabilities
- Contributors and maintainers of all dependencies