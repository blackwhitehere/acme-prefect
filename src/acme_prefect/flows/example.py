from prefect import flow

@flow(log_prints=True, description="An example flow")
def example_flow():
    print("I'm an example flow!")
