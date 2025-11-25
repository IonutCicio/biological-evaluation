import json
import os
from datetime import UTC, datetime
from time import perf_counter

import buckpass
import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox.utils.constants import FAILED, SUCCESS

from core.blackbox import FAIL_COST, Config, objective_function_multi_objective
from core.lib import init, openbox_config_multiobjective

option, logger = init()

OPENBOX_URL: buckpass.openbox_api.URL = buckpass.openbox_api.URL(
    host=os.getenv("VM_HOST", default=""), port=8000
)


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
    _, num_objectives, _ = openbox_config_multiobjective(biological_model)
    _timedelta_load = perf_counter() - start_time

    # Ask suggestion

    start_time = perf_counter()
    config: Config = buckpass.openbox_api.get_suggestion(  # pyright: ignore[reportAny]
        url=OPENBOX_URL, task_id=option.task_id
    )
    _timedelta_suggestion = perf_counter() - start_time
    logger.info(config)

    # Compute objective function value

    start_time = perf_counter()
    result = objective_function_multi_objective(
        biological_model, num_objectives
    )(config)
    _timedelta_blackbox = perf_counter() - start_time
    logger.info(result["objectives"])

    # Send observation to OpenBox

    start_time = perf_counter()
    buckpass.openbox_api.update_observation(
        url=OPENBOX_URL,
        task_id=option.task_id,
        config_dict=config,
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
        trial_state=FAILED if result["objectives"][0] == FAIL_COST else SUCCESS,
    )
    _timedelta_observation = perf_counter() - start_time
    logger.info(_timedelta_observation)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
