from acme_portal_sdk.prefect.flow_finder import PrefectFlowFinder, PrefectFlowDetails
from pathlib import Path

# Create an instance of PrefectFlowFinder
project_root = Path(__file__).parent.parent
flow_finder = PrefectFlowFinder(
    root_dir=str(project_root / "src" / "acme_prefect")
)