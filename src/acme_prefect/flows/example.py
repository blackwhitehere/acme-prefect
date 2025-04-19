from prefect import flow

@flow(log_prints=True, description="An example flow", name="example-flow")
def example_flow():
    print("I'm an example flow!")

if __name__ == "__main__":
    example_flow()