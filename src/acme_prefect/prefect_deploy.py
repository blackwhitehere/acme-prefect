import argparse
import importlib
from importlib.util import find_spec

from acme_config import add_main_arguments, load_saved_parameters

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
    parser.add_argument("-package-version", type=str, help="Package version")
    parser.add_argument(
        "--flows-to-deploy",
        type=str,
        default="all",
        help="Comma separated list of flow config names to deploy, or 'all'",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    env_vars = load_saved_parameters(args.app_name, args.env, args.ver_number)
    if args.flows_to_deploy == "all":
        flows_to_deploy = STATIC_CONFIG.keys()
    else:
        flows_to_deploy = args.flows_to_deploy.split(",")
    for flow_name in flows_to_deploy:
        flow_config = STATIC_CONFIG[flow_name]
        module_path, function_name = flow_config["import_path"].split(":")
        flow_function = import_function(module_path, function_name)
        flow_name = f"{args.project_name}--{args.branch_name}--{flow_config['name']}--{args.env}"
        flow_function.deploy(
            name=flow_name,
            description=flow_config["description"],
            work_pool_name=flow_config["work_pool_name"],
            cron=flow_config["cron"],
            image=args.image_uri,
            job_variables={"env": {**env_vars, "DEPLOYMENT_NAME": flow_name}},
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
