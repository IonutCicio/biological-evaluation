import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from logging import Logger

import buckpass
from biological_scenarios_generation.core import IntGTZ
from biological_scenarios_generation.model import BiologicalModel
from dotenv import load_dotenv
from openbox import space


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
            _ = load_dotenv(dotenv_path=dotenv_path.strip())

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=args.log, level=logging.INFO)

    return (
        Option(
            env=list(map(str.strip, args.env)) if args.env else [],
            task_id=buckpass.core.OpenBoxTaskId((args.task_id or "").strip()),
        ),
        logger,
    )


def config(biological_model: BiologicalModel) -> tuple[space.Space, IntGTZ]:
    _space: space.Space = space.Space()
    _space.add_variables(
        [
            space.Real(
                name=kinetic_constant,
                lower=-20.0,
                upper=0.0 if kinetic_constant.startswith("k_s_") else 20.0,
                default_value=0.0,
            )
            for kinetic_constant in biological_model.kinetic_constants
        ]
    )

    num_objectives = (
        biological_model.sbml_document.getModel().getNumSpecies()
        - len(
            {
                kinetic_constant
                for kinetic_constant in biological_model.kinetic_constants
                if re.match(r"k_s_\d+", kinetic_constant)
            }
        )
    ) * 2

    return _space, num_objectives
