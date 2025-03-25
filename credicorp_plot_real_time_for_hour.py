import requests
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


def fetch_credicorp_data():
    """
    Fetch Credicorp stock data from the API
    """
    try:
        # Replace with your actual API endpoint
        response = requests.get("http://localhost:8000/api/credicorp")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def create_plotly_app():
    # Initialize the Dash app
    app = dash.Dash(__name__)

    # Fetch data
    data = fetch_credicorp_data()

    if not data or not data['historical']:
        print("No data available")
        return None

    # Convert data to DataFrame
    df = pd.DataFrame(data['historical'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Create the figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['price'],
        mode='lines+markers',
        name='Stock Price',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))

    # Customize layout
    fig.update_layout(
        title='Credicorp Stock Price',
        xaxis_title='Date and Time',
        yaxis_title='Price ($)',
        hovermode='closest',
        height=600,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Configure x-axis to show detailed time
    fig.update_xaxes(
        tickformat='%Y-%m-%d %H:%M',
        tickangle=45
    )

    # Add annotation for current price
    if data.get('realtime'):
        realtime = data['realtime']
        current_price = realtime['price']
        price_change = realtime['variation']

        fig.add_annotation(
            x=df['timestamp'].iloc[-1],
            y=current_price,
            text=f"Current: ${current_price:.2f}<br>Change: {price_change:.2f}%",
            showarrow=True,
            arrowhead=1,
            ax=50,
            ay=-30
        )

    # Dash app layout
    app.layout = html.Div([
        html.H1('Credicorp Stock Price Visualization'),
        dcc.Graph(figure=fig),
        html.Div([
            html.P(f"Data Points: {data['metadata']['data_points']}"),
            html.P(
                f"Time Range: {datetime.fromtimestamp(data['metadata']['time_range']['from'])} to {datetime.fromtimestamp(data['metadata']['time_range']['to'])}")
        ])
    ])

    return app


# Run the app
if __name__ == '__main__':
    app = create_plotly_app()
    if app:
        app.run(debug=True)  # Updated from app.run_server() to app.run()