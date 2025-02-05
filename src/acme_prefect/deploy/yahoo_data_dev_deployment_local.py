from acme_prefect.flows.fetch_yahoo_data import main

if __name__ == "__main__":
    main.serve(
        cron="0 12 * * 1-5",
        name="yahoo-data-dev-deployment-local",
        pause_on_shutdown=False
    )