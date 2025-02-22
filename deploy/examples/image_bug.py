from prefect import flow


@flow(log_prints=True)
def image_bug(name: str = "world"):
    print(f"Hello {name} from Prefect! 🤗")


if __name__ == "__main__":
    image_bug.deploy(build=False,
                       push=False,
                       image="ghcr.io/blackwhitehere/acme-prefect:main-latest")