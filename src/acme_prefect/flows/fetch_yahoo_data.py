from datetime import datetime, timedelta
from io import BytesIO

from prefect import flow
from prefect_aws import AwsCredentials

import yfinance as yf
from retry import retry


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


def save_data_to_s3(data, bucket, key, s3_client):
    """
    Save data to an S3 bucket.

    Args:
        data (pandas.DataFrame): Data to save
        bucket (str): S3 bucket name
        key (str): S3 object key
        s3_client (boto3.client): Boto3 S3 client
    """

    # Convert DataFrame to parquet format in memory
    buffer = BytesIO()
    data.to_parquet(buffer, index=True)
    buffer.seek(0)

    # Upload the parquet file to S3
    s3_client.upload_fileobj(buffer, bucket, key)


@flow(name="Fetch Yahoo Data", log_prints=True)
def main():
    start_date, end_date = get_date_range(days_back=1)
    stock = "AAPL"
    # Get stock data
    try:
        data = get_minute_data(stock, start_date, end_date)
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        data = None

    if data is not None:
        s3_client = aws_credentials_block.get_s3_client()
        save_data_to_s3(
            data,
            "acme-s3-dev",
            f"dw/yahoo/price_history/minute/{stock}/{end_date:%Y}/{start_date:%Y%m%d}_{end_date:%Y%m%d}.parquet",
            s3_client,
        )

if __name__ == "__main__":
    main()