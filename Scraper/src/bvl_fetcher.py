"""
BVL Data Fetcher

This script fetches stock data from the Lima Stock Exchange (BVL) API,
filters for specific companies, and saves the results to a CSV file.
"""
import requests
import json
import pandas as pd
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse
from dotenv import load_dotenv
import sys
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables from .env file
load_dotenv()


class EnhancedBVLDataFetcher:
    """Enhanced version of BVL Data Fetcher with improved features."""

    def __init__(self, config: Dict[str, Any]):
        self.url = config["url"]
        self.headers = config["headers"]
        self.payload = config["payload"]
        self.csv_filename = config["csv_filename"]
        self.target_companies = set(config["target_companies"])
        self.iterations = config["iterations"]
        self.wait_time = config["wait_time"]
        self.logger = self._setup_logger(config["log_level"], config["log_file"])
        self.output_dir = config["output_dir"]

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _setup_logger(self, log_level: str, log_file: str) -> logging.Logger:
        logger = logging.getLogger("EnhancedBVLDataFetcher")
        logger.setLevel(getattr(logging, log_level))

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
    def fetch_data(self) -> Optional[Dict[str, Any]]:
        try:
            self.logger.info("Sending request to BVL API")
            response = requests.post(self.url, headers=self.headers, json=self.payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error in fetch_data: {str(e)}")
            return None

    def process_data(self, data: Dict[str, Any]) -> Optional[pd.DataFrame]:
        try:
            companies_list = data.get("content", [])
            if not isinstance(companies_list, list):
                self.logger.error("Error: 'content' does not contain a list")
                return None

            self.logger.info(f"Received data for {len(companies_list)} companies")

            filtered_companies = [company for company in companies_list
                                  if company.get("companyName") in self.target_companies]

            if not filtered_companies:
                self.logger.warning(f"Target companies {self.target_companies} not found in the response")
                return None

            self.logger.info(f"Filtered to {len(filtered_companies)} target companies")

            df = pd.DataFrame(filtered_companies)
            df[["buy", "sell"]] = df[["buy", "sell"]].fillna(0)
            df['timestamp'] = datetime.now().isoformat()

            return df
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            return None

    def save_data(self, df: pd.DataFrame) -> bool:
        try:
            file_path = os.path.join(self.output_dir, self.csv_filename)

            # If file exists, load existing data and concatenate
            if os.path.exists(file_path):
                existing_data = pd.read_csv(file_path)
                combined = pd.concat([existing_data, df])

                # Remove duplicates based on timestamp and company
                combined = combined.drop_duplicates(subset=['timestamp', 'companyName'], keep='last')
            else:
                combined = df

            # Save updated data
            combined.to_csv(file_path, index=False)
            self.logger.info(f"Data successfully updated in {file_path}")

            return True
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            return False

    def run(self) -> None:
        self.logger.info(f"Starting BVL data fetching process for {self.iterations} iterations")

        for i in range(self.iterations):
            self.logger.info(f"Iteration {i + 1}/{self.iterations}: Getting data...")

            data = self.fetch_data()
            if not data:
                self.logger.error("Failed to fetch data, skipping iteration")
                continue

            df = self.process_data(data)
            if df is not None:
                if not self.save_data(df):
                    self.logger.error("Failed to save data")

            if i < self.iterations - 1:
                wait_minutes = self.wait_time // 60
                self.logger.info(f"Waiting {wait_minutes} minutes for the next update...")
                time.sleep(self.wait_time)

        self.logger.info(f"Process finished after {self.iterations} iterations")


def get_default_config() -> Dict[str, Any]:
    return {
        "url": os.getenv("BVL_API_URL", "https://dataondemand.bvl.com.pe/v1/stock-quote/market"),
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": os.getenv("USER_AGENT",
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        },
        "payload": {
            "sector": "",
            "today": True,
            "companyCode": "",
            "inputCompany": ""
        },
        "csv_filename": "bvl_data.csv",
        "target_companies": ["CREDICORP LTD."],
        "iterations": 3,
        "wait_time": 2 * 60 * 60,  # 2 hours in seconds
        "log_level": "INFO",
        "log_file": "bvl_data_fetcher.log",
        "output_dir": "data"
    }


def parse_arguments() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Fetch stock data from the BVL API")
    parser.add_argument("--companies", nargs="+", help="List of target companies")
    parser.add_argument("--iterations", type=int, help="Number of iterations")
    parser.add_argument("--wait-time", type=int, help="Wait time between iterations in minutes")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    parser.add_argument("--output-dir", help="Output directory for data files")
    parser.add_argument("--config-file", help="Path to config file")

    return vars(parser.parse_args())


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    config = get_default_config()

    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading config file: {str(e)}")

    args = parse_arguments()
    args = {k: v for k, v in args.items() if v is not None}

    if "wait_time" in args:
        args["wait_time"] = args["wait_time"] * 60

    config.update(args)

    return config


def main():
    try:
        config = load_config()
        fetcher = EnhancedBVLDataFetcher(config)
        fetcher.run()
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()