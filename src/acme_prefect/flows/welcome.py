from prefect import flow

@flow(log_prints=True, description="A welcome flow")
def welcome_flow():
    print("Welcome to the flow!")

if __name__ == "__main__":
    welcome_flow()