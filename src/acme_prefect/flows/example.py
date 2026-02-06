from prefect import flow, task

@task
def example_task():
    print("I'm an example task!")
    return 42

@task
def another_example_task(a):
    print(f"I'm another example task! {a}")

@flow(log_prints=True, description="An example flow", name="example-flow", retries=3)
def example_flow():
    a = example_task()
    another_example_task(a)
    print("I'm an example flow!")

if __name__ == "__main__":
    example_flow()