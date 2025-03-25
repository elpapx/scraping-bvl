import requests
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import threading
import time
from datetime import datetime, timedelta


class RealTimeStockPlotter:
    def __init__(self, update_interval=300):  # Default 5-minute updates
        self.fig = None
        self.historical_data = []
        self.update_interval = update_interval
        self.running = False

    def fetch_credicorp_data(self):
        """Fetch the latest Credicorp data from API"""
        try:
            response = requests.get('http://localhost:8000/api/credicorp')
            data = response.json()
            return data['historical']
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

    def create_initial_plot(self):
        """Create the initial plot with existing data"""
        # Fetch initial data
        self.historical_data = self.fetch_credicorp_data()

        # Convert to DataFrame
        df = pd.DataFrame(self.historical_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.sort_values('datetime')

        # Create figure with secondary y-axis
        self.fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Price Line
        self.fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['price'],
                mode='lines+markers',
                name='Stock Price',
                line=dict(color='royalblue', width=2),
                marker=dict(size=8, color='darkblue')
            ),
            secondary_y=False
        )

        # Variation Line
        self.fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['variation'],
                mode='lines+markers',
                name='Price Variation (%)',
                line=dict(color='green', width=2),
                marker=dict(size=8, color='darkgreen')
            ),
            secondary_y=True
        )

        # Update layout
        self.fig.update_layout(
            title='Credicorp Stock - Real-Time Price and Variation',
            xaxis_title='Date',
            template='plotly_white',
            height=600,
            width=1000,
            legend_title_text='Metrics',
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=[
                        dict(
                            args=[{"visible": [True, True]}],
                            label="All",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [True, False]}],
                            label="Price",
                            method="update"
                        ),
                        dict(
                            args=[{"visible": [False, True]}],
                            label="Variation",
                            method="update"
                        )
                    ],
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.11,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ]
        )

        # Customize axes
        self.fig.update_yaxes(title_text="Stock Price", secondary_y=False)
        self.fig.update_yaxes(title_text="Price Variation (%)", secondary_y=True)

    def update_plot(self):
        """Periodically update the plot with new data"""
        while self.running:
            try:
                # Fetch new data
                new_data = self.fetch_credicorp_data()

                # Convert to DataFrame
                df = pd.DataFrame(new_data)
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df = df.sort_values('datetime')

                # Update traces
                self.fig.data[0].x = df['datetime']
                self.fig.data[0].y = df['price']
                self.fig.data[1].x = df['datetime']
                self.fig.data[1].y = df['variation']

                # Save updated plot
                self.fig.write_html("credicorp_realtime.html", auto_open=True)

                # Wait before next update
                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(self.update_interval)

    def start_live_plotting(self):
        """Start the real-time plotting process"""
        # Create initial plot
        self.create_initial_plot()

        # Save initial plot
        self.fig.write_html("credicorp_realtime.html", auto_open=True)

        # Start update thread
        self.running = True
        update_thread = threading.Thread(target=self.update_plot)
        update_thread.start()

    def stop_live_plotting(self):
        """Stop the real-time plotting process"""
        self.running = False


def main():
    # Create plotter instance
    plotter = RealTimeStockPlotter(update_interval=300)  # Update every 5 minutes

    try:
        # Start live plotting
        plotter.start_live_plotting()

        # Keep main thread running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping real-time plotting...")
        plotter.stop_live_plotting()


if __name__ == "__main__":
    main()