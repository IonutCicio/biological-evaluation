import argparse
import logging
import sys
from dataclasses import dataclass, field
from logging import Logger

import buckpass
from biological_scenarios_generation.core import IntGEZ, IntGTZ
from biological_scenarios_generation.model import BiologicalModel
from dotenv import load_dotenv
from openbox import space

FAIL_COST: float = 100  # sys.float_info.max


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Option:
    env: list[str]
    task_id: buckpass.core.OpenBoxTaskId = field(default="")


def init() -> tuple[Option, Logger]:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    _ = argument_parser.add_argument(
        "-e", "--env", dest="env", nargs="*", metavar=None
    )
    _ = argument_parser.add_argument("-t", "--task", dest="task_id")
    _ = argument_parser.add_argument(
        "-l",
        "--log",
        dest="log",
        nargs=None,
        default=sys.stdout,
        type=argparse.FileType("w"),
        metavar="logfile",
    )
    args: argparse.Namespace = argument_parser.parse_args()

    assert isinstance(args.env, list | None)
    assert isinstance(args.task_id, str | None)

    _ = load_dotenv()
    if args.env:
        for dotenv_path in args.env:
            _ = load_dotenv(dotenv_path=dotenv_path.strip())

    logger: Logger = logging.getLogger(__name__)
    logging.basicConfig(stream=args.log, level=logging.INFO)

    return (
        Option(
            env=list(map(str.strip, args.env)) if args.env else [],
            task_id=buckpass.core.OpenBoxTaskId((args.task_id or "").strip()),
        ),
        logger,
    )


def openbox_config_multiobjective(
    biological_model: BiologicalModel,
) -> tuple[space.Space, IntGTZ, IntGEZ]:
    _space: space.Space = space.Space()
    _space.add_variables(
        [
            space.Real(
                name=kinetic_constant,
                lower=category.interval().lower_bound,
                upper=category.interval().upper_bound,
                default_value=0.0,
            )
            for kinetic_constant, category in biological_model.kinetic_constants.items()
        ]
    )

    num_objectives = IntGTZ(4)
    # IntGTZ(
    #     (len(biological_model.other_parameters) - 1)  # for normalization
    #     + (len(biological_model.other_parameters) - 1)  # for transitory
    #     + len(biological_model.species_order)
    #     + len(biological_model.kinetic_constants_order)
    # )

    num_constraints = IntGEZ(0)

    return _space, num_objectives, num_constraints
