import argparse

from acme_prefect.flows.fetch_yahoo_data import main

from acme_config import add_main_arguments, fetch_parameters


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy flows to prefect")
    add_main_arguments(parser)
    parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the project",
    )
    parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the branch",
    )
    parser.add_argument("-commit-hash", type=str, help="Git commit hash")
    parser.add_argument("-image-uri", type=str, help="Image URI")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    parameters = fetch_parameters(args.app_name, args.env, args.ver_number)
    main.deploy(
        name=f"{args.project_name}--{args.branch_name}--fetch-yahoo-data--dev",
        description="Fetches Yahoo Finance data with minute-level granularity",
        work_pool_name="ecs-pool",  # TODO: pass as config?
        cron="0 12 * * 1-5",
        image=args.image_uri,
        job_variables={"env": parameters},
        tags=[args.project_name, args.branch_name, args.commit_hash],
        version=f"{args.branch_name}-{args.commit_hash}",
        build=False,
        push=False,
    )
