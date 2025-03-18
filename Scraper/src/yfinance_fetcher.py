import yfinance as yf
import pandas as pd
import os
import time

# Path where the CSV will be saved
csv_path = r"E:\papx\end_to_end_ml\nb_pr\scraping-bvl\Scraper\src\data\yfinance_data.csv"

# Define the tickers
tickers = ["ILF", "BRK-B", "BAP"]


def get_ticker_data():
    """
    Gets the date, prices, volume, dividend yield, and financial metrics of the tickers.
    """
    data = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            history = stock.history(period="1d")
            info = stock.info  # Extract additional information

            if not history.empty:
                date = history.index[-1].strftime("%Y-%m-%d %H:%M:%S")  # Date format
                open_price = history["Open"].iloc[-1]
                close_price = history["Close"].iloc[-1]
                high_price = history["High"].iloc[-1]
                low_price = history["Low"].iloc[-1]
                volume = history["Volume"].iloc[-1]
                company = info.get("longName", "N/A")

                data.append({
                    "Date": date,
                    "Ticker": ticker,
                    "Open": round(open_price, 2),
                    "High": round(high_price, 2),
                    "Low": round(low_price, 2),
                    "Close": round(close_price, 2),
                    "Volume": volume,
                    "Company": company,
                })
            else:
                print(f"{ticker}: No data available.")

        except Exception as e:
            print(f"Error getting data for {ticker}: {e}")

    return pd.DataFrame(data)


def save_to_csv(df, csv_path):
    """
    Saves the data to a CSV file without duplicates.
    """
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        df = pd.concat([existing_df, df]).drop_duplicates(subset=["Date", "Ticker"], keep="last")

    df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")


def main():
    while True:
        print("\nUpdating prices and metrics...")
        prices_df = get_ticker_data()

        if not prices_df.empty:
            save_to_csv(prices_df, csv_path)

        print("Data updated. Waiting 2 hours...")
        time.sleep(2 * 60 * 60)  # Wait 2 hours (in seconds)


if __name__ == "__main__":
    main()