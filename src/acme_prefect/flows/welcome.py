from prefect import flow

@flow(log_prints=True, description="A welcome flow")
def welcome_flow():
    # comment
    print("I'm a welcome flow!")

if __name__ == "__main__":
    welcome_flow()