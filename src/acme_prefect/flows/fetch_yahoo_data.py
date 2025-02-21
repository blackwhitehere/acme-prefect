import os
from datetime import datetime, timedelta
import logging

from prefect import flow
from prefect_aws import AwsCredentials
from acme_dw import DatasetMetadata, DW

import yfinance as yf
from retry import retry

logger = logging.getLogger(__name__)


aws_credentials_block = AwsCredentials.load("dev-bucket")


@retry(tries=3)
def get_minute_data(ticker_symbol, start_date, end_date):
    """
    Fetch minute-level stock data for a given ticker symbol.

    Args:
        ticker_symbol (str): The stock ticker symbol (e.g., 'AAPL', 'MSFT')
        days_back (int): Number of trading days to look back (default: 1)

    Returns:
        pandas.DataFrame: Minute-level stock data
    """

    # Create ticker object
    ticker = yf.Ticker(ticker_symbol)

    # Fetch minute-level data
    # interval options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h
    df = ticker.history(start=start_date, end=end_date, interval="1m")
    return df


def get_date_range(days_back=1):
    # Calculate start and end dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


@flow(name="fetch-yahoo-data", log_prints=True)
def main():
    start_date, end_date = get_date_range(days_back=1)
    stock = "AAPL"
    # Get stock data
    try:
        data = get_minute_data(stock, start_date, end_date)
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        raise

    s3_client = aws_credentials_block.get_s3_client()
    metadata = DatasetMetadata(
        source="yahoo_finance",
        name="price_history",
        version="v1",
        process_id=os.environ.get("DEPLOYMENT_NAME", "fetch_yahoo_data"),
        partitions=["minute", stock, end_date.strftime("%Y")],
        file_name=f"{start_date:%Y%m%d}_{end_date:%Y%m%d}.parquet",
        file_type="parquet",
    )
    # TODO: read bucket name from env var
    dw = DW("acme-s3-dev", boto3_client=s3_client)
    dw.write_df(data, metadata)

if __name__ == "__main__":
    main()