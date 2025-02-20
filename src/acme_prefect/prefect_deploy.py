import argparse
import logging
import importlib
import asyncio
from importlib.util import find_spec

from prefect.client.orchestration import get_client

from acme_config import add_main_arguments, load_saved_parameters

logger = logging.getLogger(__name__)

# TODO: set from acme-config?
STATIC_CONFIG = {
    "fetch-yahoo-data": {
        "name": "fetch-yahoo-data",
        "import_path": "acme_prefect.flows.fetch_yahoo_data:main",
        "cron": "0 12 * * 1-5",
        "description": "Fetches Yahoo Finance data with minute-level granularity",
        "work_pool_name": "ecs-pool",
    },
}


def import_function(module_path, function_name):
    try:
        # Check if module exists
        if find_spec(module_path) is None:
            raise ImportError(f"Module {module_path} not found")

        # Import module
        module = importlib.import_module(module_path)

        # Get function
        if not hasattr(module, function_name):
            raise AttributeError(f"Function {function_name} not found in {module_path}")

        return getattr(module, function_name)

    except Exception as e:
        print(f"Error importing {function_name} from {module_path}: {e}")
        raise


def parse_args():
    parser = argparse.ArgumentParser(description="Deploy flows to prefect")
    subparsers = parser.add_subparsers(dest="command")
    # Deploy parser for initial deployment
    deploy_parser = subparsers.add_parser("deploy")
    add_main_arguments(deploy_parser)
    deploy_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the project",
    )
    deploy_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the branch",
    )
    deploy_parser.add_argument("-commit-hash", type=str, help="Git commit hash")
    deploy_parser.add_argument("-image-uri", type=str, help="Image URI")
    deploy_parser.add_argument("-package-version", type=str, help="Package version")
    deploy_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    # Promote parser for promoting deployment from one environment to another
    promote_parser = subparsers.add_parser("promote")
    add_main_arguments(promote_parser)
    promote_parser.add_argument("-source-env", type=str, help="Source environment")
    promote_parser.add_argument(
        "-project-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the project",
    )
    promote_parser.add_argument(
        "-branch-name",
        type=lambda x: str(x).replace("_", "-"),
        help="Name of the branch",
    )
    promote_parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )

    return parser.parse_args()


def deploy(args):
    env_vars = load_saved_parameters(args.app_name, args.env, args.ver_number)
    if args.flows_to_deploy == "all":
        flows_to_deploy = STATIC_CONFIG.keys()
    else:
        flows_to_deploy = args.flows_to_deploy.split(",")
    for flow_name in flows_to_deploy:
        deploy_config = STATIC_CONFIG[flow_name]
        module_path, function_name = deploy_config["import_path"].split(":")
        flow_function = import_function(module_path, function_name)
        # align with expectation of flow name being flow function name with underscores
        underscore_flow_name = deploy_config["name"].replace("-", "_")
        if flow_function.name != underscore_flow_name:
            logger.info(f"Standardizing flow name {flow_function.name} for deployment to {underscore_flow_name}")
            flow_function.name = underscore_flow_name
        deployment_name = f"{args.project_name}--{args.branch_name}--{deploy_config['name']}--{args.env}"
        flow_function.deploy(
            name=deployment_name,
            description=deploy_config["description"],
            work_pool_name=deploy_config["work_pool_name"],
            cron=deploy_config["cron"],
            image=args.image_uri,
            job_variables={"env": {**env_vars, "DEPLOYMENT_NAME": deployment_name}},
            tags=[
                f"PROJECT_NAME={args.project_name}",
                f"BRANCH_NAME={args.branch_name}",
                f"COMMIT_HASH={args.commit_hash}",
                f"PACKAGE_VERSION={args.package_version}",
            ],
            version=f"{args.branch_name}-{args.commit_hash}",
            build=False,
            push=False,
        )


def promote(args):
    client = get_client()
    if args.flows_to_deploy == "all":
        flows_to_deploy = STATIC_CONFIG.keys()
    else:
        flows_to_deploy = args.flows_to_deploy.split(",")
    for flow_name in flows_to_deploy:
        deploy_config = STATIC_CONFIG[flow_name]
        underscore_flow_name = deploy_config["name"].replace("-", "_")
        deployment_name = f"{args.project_name}--{args.branch_name}--{deploy_config['name']}--{args.source_env}"
        r = dict(asyncio.run(client.read_deployment_by_name(f"{underscore_flow_name}/{deployment_name}")))
        args.image_uri = r["job_variables"]["image"]
        args.package_version = [x for x in r["tags"] if x.startswith("PACKAGE_VERSION=")][0].split("=")[1]
        args.commit_hash = [x for x in r["tags"] if x.startswith("COMMIT_HASH=")][0].split("=")[1]
        # TODO: note that description, work_pool_name, cron, etc. are set from current version of 
        # static config rather than being inherited from source deployment
        deploy(args)


def main_logic(args):
    if args.command == "deploy":
        deploy(args)
    elif args.command == "promote":
        promote(args)
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    args = parse_args()
    main_logic(args)
