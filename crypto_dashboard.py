import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Initialize the Dash app
app = dash.Dash(__name__)

# Load the data
def load_all_data():
    monthly_stats = pd.read_csv('data/monthly_analysis.csv')
    overall_stats = pd.read_csv('data/overall_statistics.csv')
    weekly_changes = pd.read_csv('data/weekly_changes.csv')
    
    # Convert date columns
    monthly_stats['month'] = pd.to_datetime(monthly_stats['month'].astype(str))
    weekly_changes['date'] = pd.to_datetime(weekly_changes['date'])
    
    return monthly_stats, overall_stats, weekly_changes

# Create layout
app.layout = html.Div([
    html.H1("Cryptocurrency Analysis Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Price Trends Section
    html.Div([
        html.H2("Monthly Price Statistics", 
                style={'color': '#34495e', 'marginBottom': 20}),
        dcc.Graph(id='monthly-price-trends'),
        
        # Cryptocurrency selector
        dcc.Dropdown(
            id='crypto-selector',
            options=[
                {'label': 'Bitcoin (BTC)', 'value': 'BTCUSDT'},
                {'label': 'Ethereum (ETH)', 'value': 'ETHUSDT'},
                {'label': 'Solana (SOL)', 'value': 'SOLUSDT'},
                {'label': 'Cardano (ADA)', 'value': 'ADAUSDT'},
                {'label': 'Dogecoin (DOGE)', 'value': 'DOGEUSDT'},
                {'label': 'Shiba Inu (SHIB)', 'value': 'SHIBUSDT'},
                {'label': 'USDC', 'value': 'USDCUSDT'}
            ],
            value='BTCUSDT',
            style={'marginBottom': 20}
        ),
    ]),
    
    # Statistics Tables Section
    html.Div([
        html.H2("Overall Statistics", 
                style={'color': '#34495e', 'marginBottom': 20}),
        dcc.Graph(id='overall-stats-table'),
    ]),
    
    # Weekly Changes Section
    html.Div([
        html.H2("Weekly Price Changes", 
                style={'color': '#34495e', 'marginBottom': 20}),
        dcc.Graph(id='weekly-changes-chart'),
    ]),
    
    # Price Range Analysis
    html.Div([
        html.H2("Monthly Price Ranges", 
                style={'color': '#34495e', 'marginBottom': 20}),
        dcc.Graph(id='price-range-chart'),
    ]),
], style={'padding': '20px'})

# Callbacks
@app.callback(
    [Output('monthly-price-trends', 'figure'),
     Output('overall-stats-table', 'figure'),
     Output('weekly-changes-chart', 'figure'),
     Output('price-range-chart', 'figure')],
    [Input('crypto-selector', 'value')]
)
def update_graphs(selected_crypto):
    monthly_stats, overall_stats, weekly_changes = load_all_data()
    
    # 1. Monthly Price Trends
    monthly_fig = px.line(
        monthly_stats[monthly_stats['symbol'] == selected_crypto],
        x='month',
        y=['average_price', 'highest_price', 'lowest_price'],
        title=f'Monthly Price Trends for {selected_crypto}',
        labels={'value': 'Price (USDT)', 'month': 'Month'},
        template='plotly_white'
    )
    
    # 2. Overall Statistics Table
    stats_fig = go.Figure(data=[go.Table(
        header=dict(values=list(overall_stats.columns),
                   fill_color='#34495e',
                   align='left',
                   font=dict(color='white', size=12)),
        cells=dict(values=[overall_stats[col] for col in overall_stats.columns],
                  fill_color='lavender',
                  align='left'))
    ])
    stats_fig.update_layout(title='Overall Statistics for All Cryptocurrencies')
    
    # 3. Weekly Changes
    weekly_fig = px.line(
        weekly_changes[weekly_changes['symbol'] == selected_crypto].tail(12),
        x='date',
        y='price_change_pct',
        title=f'Weekly Price Changes for {selected_crypto}',
        labels={'price_change_pct': 'Price Change (%)', 'date': 'Date'},
        template='plotly_white'
    )
    weekly_fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # 4. Price Range Analysis
    range_data = monthly_stats[monthly_stats['symbol'] == selected_crypto].tail(12)
    range_fig = go.Figure()
    range_fig.add_trace(go.Bar(
        x=range_data['month'],
        y=range_data['price_range'],
        name='Price Range',
        marker_color='#3498db'
    ))
    range_fig.update_layout(
        title=f'Monthly Price Ranges for {selected_crypto}',
        xaxis_title='Month',
        yaxis_title='Price Range (USDT)',
        template='plotly_white'
    )
    
    return monthly_fig, stats_fig, weekly_fig, range_fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8050) 