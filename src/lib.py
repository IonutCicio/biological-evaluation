import argparse
from dataclasses import dataclass, field

import buckpass
from dotenv import load_dotenv


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Arguments:
    env: str = field(default="")
    task_id: buckpass.core.OpenBoxTaskId = field(default="")


def source_env() -> Arguments:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    _ = argument_parser.add_argument("-e", "--env")
    _ = argument_parser.add_argument("-t", "--task")
    args = argument_parser.parse_args()

    _ = load_dotenv()
    _ = load_dotenv(dotenv_path=str(args.env).strip())

    return Arguments(
        env=args.env,
        task_id=buckpass.core.OpenBoxTaskId(str(args.task).strip()),
    )
