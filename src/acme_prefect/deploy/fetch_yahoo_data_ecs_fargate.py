from acme_prefect.flows.fetch_yahoo_data import main

# TODO: use https://docs-3.prefect.io/v3/deploy/infrastructure-concepts/prefect-yaml
if __name__ == "__main__":
    main.deploy(
        name="fetch-yahoo-data-ecs-fargate",
        work_pool_name="ecs-pool",
        cron="0 12 * * 1-5",
        image="ghcr.io/blackwhitehere/acme-prefect:latest", # we should specify exact version here
        build=False,
        push=False,
    )
