from prefect import flow

@flow(log_prints=True, description="A sample flow")
def sample_two():
    # sample comment -- new comment
    print("I'm an example flow!")

if __name__ == "__main__":
    sample_two()