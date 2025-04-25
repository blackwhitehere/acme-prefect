from acme_portal_sdk.prefect.deployment_finder import PrefectDeploymentFinder

# Will require prefect client be authenticated against prefect server like prefect cloud
deployment_finder = PrefectDeploymentFinder()

if __name__ == "__main__":
    from pprint import pprint
    deployments = deployment_finder.get_deployments()
    pprint(deployments)