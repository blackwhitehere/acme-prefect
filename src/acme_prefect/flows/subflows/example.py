from prefect import flow

@flow(log_prints=True, description="An example flow")
def subflow_flow():
    print("I'm an example flow!")

if __name__ == "__main__":
    subflow_flow()