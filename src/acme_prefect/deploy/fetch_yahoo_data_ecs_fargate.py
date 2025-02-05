from acme_prefect.flows.fetch_yahoo_data import main

if __name__ == "__main__":
    main.deploy(
        name="fetch-yahoo-data-ecs-fargate",
        work_pool_name="ecs-pool",
        cron="0 12 * * 1-5",
        image="ghcr.io/blackwhitehere/acme-prefect:latest",
        build=False,
        push=False,
    )
