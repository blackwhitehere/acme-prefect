import argparse

from prefect.blocks.core import Block
from prefect.blocks.fields import SecretDict

from acme_config import add_main_arguments, fetch_parameters


class AcmeConfig(Block):
    env: SecretDict

    def __dict__(self):
        return self.env


def parse_args():
    parser = argparse.ArgumentParser(description="Load config from acme_config to prefect Block")
    add_main_arguments(parser)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    block_name = f"{args.app_name}-{args.env}-{args.ver_number}"
    try:
        acme_config_block = AcmeConfig.load(block_name)
    except ValueError:
        print(f"Block {block_name} does not already exist, creating new one")
        parameters = fetch_parameters(args.app_name, args.env, args.ver_number)
        acme_config_block = AcmeConfig(env=parameters)
        acme_config_block.save(block_name)