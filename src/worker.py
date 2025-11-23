import json
import os
from datetime import UTC, datetime
from time import perf_counter

import buckpass
import libsbml
from biological_scenarios_generation.model import (
    BiologicalModel,
    VirtualPatient,
)
from openbox.utils.constants import FAILED, SUCCESS

from blackbox import SIMULATION_FAIL_COST, objective_function
from lib import init, openbox_config

option, logger = init()


def main() -> None:
    filepath: str | None = os.getenv("SBML")
    assert filepath
    worker_start_time = datetime.now(tz=UTC)

    # Load model

    start_time = perf_counter()
    biological_model = BiologicalModel.load(
        libsbml.readSBML(
            f"{os.getenv('HOME')}/{os.getenv('PROJECT_PATH')}/{filepath}"
        )
    )
    _, num_objectives = openbox_config(biological_model)
    _timedelta_load = perf_counter() - start_time

    # Ask suggestion

    start_time = perf_counter()
    openbox_url: buckpass.openbox_api.URL = buckpass.openbox_api.URL(
        host=os.getenv("VM_HOST", default=""), port=8000
    )
    suggestion: VirtualPatient = buckpass.openbox_api.get_suggestion(  # pyright: ignore[reportAny]
        url=openbox_url, task_id=option.task_id
    )
    _timedelta_suggestion = perf_counter() - start_time

    # Compute objective function value

    start_time = perf_counter()
    _objective_function = objective_function(biological_model, num_objectives)
    result = _objective_function(
        {
            kinetic_constant: 10**value
            for kinetic_constant, value in suggestion.items()
        }
    )
    _timedelta_blackbox = perf_counter() - start_time

    start_time = perf_counter()
    buckpass.openbox_api.update_observation(
        url=openbox_url,
        task_id=option.task_id,
        config_dict=suggestion,
        objectives=result["objectives"],
        constraints=[],
        trial_info={
            "cost": str(_timedelta_blackbox),
            "worker_id": os.getenv("SLURM_JOB_ID"),
            "trial_info": json.dumps(
                {
                    "start_time": str(worker_start_time),
                    "load_duration": str(_timedelta_load),
                    "suggestion_duration": str(_timedelta_suggestion),
                }
            ),
        },
        trial_state=FAILED
        if result["objectives"][0] == SIMULATION_FAIL_COST
        else SUCCESS,
    )
    _timedelta_observation = perf_counter() - start_time
    logger.info(_timedelta_observation)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
