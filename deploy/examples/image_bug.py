from prefect import flow


@flow(log_prints=True)
def image_bug(name: str = "world"):
    print(f"Hello {name} from Prefect! 🤗")


if __name__ == "__main__":
    image_bug.deploy(
        name="image-bug-deployment",
        build=False,
        push=False,
        work_pool_name="ecs-pool",
        image="ghcr.io/blackwhitehere/acme-prefect:main-latest",
    )
