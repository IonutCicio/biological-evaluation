import argparse
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TypeVar

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


T = TypeVar("T")


def measure(f: Callable[[], T]) -> tuple[T, timedelta]:
    start = datetime.now(tz=UTC)
    result = f()
    end = datetime.now(tz=UTC)

    return (result, end - start)


# _ = source_env()

# def arguments(require_task_id: bool = False) -> Arguments:

# load_dotenv
# env: pathlib.Path = field(default=pathlib.Path(".env"))
# env=pathlib.Path(args.env),
