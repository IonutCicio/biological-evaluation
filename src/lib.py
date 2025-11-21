import argparse
import logging
import sys
from dataclasses import dataclass, field
from logging import Logger

import buckpass
from dotenv import load_dotenv


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Option:
    env: list[str]
    task_id: buckpass.core.OpenBoxTaskId = field(default="")


def init() -> tuple[Option, Logger]:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    _ = argument_parser.add_argument(
        "-e",
        "--env",
        dest="env",
        nargs="*",
        # default=".env",
        # type=Path,
        help=".env files to load before runing the script",
        metavar=None,
    )
    _ = argument_parser.add_argument("-t", "--task", dest="task_id")
    _ = argument_parser.add_argument(
        "-l",
        "--log",
        dest="log",
        nargs=None,
        default=sys.stdout,
        type=argparse.FileType("w"),
        help="log file",
        metavar="logfile",
    )
    args = argument_parser.parse_args()

    assert isinstance(args.env, list | None)
    assert isinstance(args.task_id, str | None)

    _ = load_dotenv()
    if args.env:
        for dotenv_path in args.env:
            _ = load_dotenv(dotenv_path=dotenv_path)

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=args.log, level=logging.INFO)

    return (
        Option(
            env=args.env or [],
            task_id=buckpass.core.OpenBoxTaskId((args.task_id or "").strip()),
        ),
        logger,
    )
