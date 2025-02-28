import logging
import os
from datetime import datetime, timedelta

import pandas as pd
from acme_dw import DW, DatasetMetadata
from prefect import flow
from prefect_aws import AwsCredentials

logger = logging.getLogger(__name__)

aws_credentials_block = AwsCredentials.load("dev-bucket")


def get_date_range(days_back=1):
    # Calculate start and end dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


@flow(name="hello_dw", log_prints=True)
def main():
    start_date, end_date = get_date_range(days_back=1)
    data = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    s3_client = aws_credentials_block.get_s3_client()
    metadata = DatasetMetadata(
        source="examples",
        name="hello_dw",
        version="v1",
        process_id=os.environ.get("DEPLOYMENT_NAME", "tmp"),
        partitions=["example_partition"],
        file_name=f"{start_date:%Y%m%d}_{end_date:%Y%m%d}.parquet",
        file_type="parquet",
    )
    # TODO: read bucket name from env var
    dw = DW("acme-s3-dev", s3_client_kwargs={"boto3_client": s3_client})
    dw.write_df(data, metadata)


if __name__ == "__main__":
    main()
