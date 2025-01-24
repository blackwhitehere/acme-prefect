from acme_prefect.flows.fetch_yahoo_data import main

if __name__ == "__main__":
    main.deploy(
        name="yahoo-data-dev-deployment",
        work_pool_name="metaflow-managed-pool",
        image="ghcr.io/blackwhitehere/acme-prefect:latest",
        cron="0 12 * * 1-5",
        build=False,
        push=False,
    )