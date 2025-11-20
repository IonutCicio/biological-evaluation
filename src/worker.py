import builtins
import contextlib
import json
import os
import re
from datetime import UTC, datetime

import buckpass
import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox.utils.constants import FAILED, SUCCESS

from blackbox import Cost, blackbox
from lib import source_env

args = source_env()

OPENBOX_URL: buckpass.openbox_api.URL = buckpass.openbox_api.URL(
    host=os.getenv("VM_HOST") or "", port=8000
)

ORCHESTRATOR_URL = f"http://{os.getenv('VM_HOST')}:8080/"


def main() -> None:
    filepath = os.getenv("SBML")
    assert filepath

    start_time = datetime.now(tz=UTC)

    start = datetime.now(tz=UTC)
    biological_model = BiologicalModel.load(
        libsbml.readSBML(
            f"{os.getenv('HOME')}/{os.getenv('PROJECT_PATH')}/{filepath}"
        )
    )
    end = datetime.now(tz=UTC)
    _timedelta_load = end - start

    start = datetime.now(tz=UTC)
    suggestion: dict[str, float] = buckpass.openbox_api.get_suggestion(
        url=OPENBOX_URL, task_id=args.task_id
    )
    end = datetime.now(tz=UTC)
    _timedelta_suggestion = end - start

    cost: Cost | None = None
    start = datetime.now(tz=UTC)
    with contextlib.suppress(builtins.BaseException):
        cost = blackbox(
            biological_model,
            virtual_patient={
                kinetic_constant: 10**value
                for kinetic_constant, value in suggestion.items()
            },
        )
    end = datetime.now(tz=UTC)
    _timedelta_blackbox = end - start

    normalization_len = (
        biological_model.sbml_document.getModel().getNumSpecies()
    ) - len(
        {
            kinetic_constant
            for kinetic_constant in biological_model.kinetic_constants
            if re.match(r"k_s_\d+", kinetic_constant)
        }
    )

    start = datetime.now(tz=UTC)
    buckpass.openbox_api.update_observation(
        url=OPENBOX_URL,
        task_id=args.task_id,
        config_dict=suggestion,
        objectives=cost.normalization if cost else [1] * normalization_len,
        constraints=[],
        trial_info={
            "cost": str(_timedelta_blackbox),
            "worker_id": os.getenv("SLURM_JOB_ID"),
            "trial_info": json.dumps(
                {
                    "start_time": str(start_time),
                    "load_duration": str(_timedelta_load),
                    "suggestion_duration": str(_timedelta_suggestion),
                }
            ),
        },
        trial_state=SUCCESS if cost else FAILED,
    )
    end = datetime.now(tz=UTC)
    _timedelta_observation = end - start

    print(_timedelta_observation, flush=True)


if __name__ == "__main__":
    main()
