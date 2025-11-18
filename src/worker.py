import argparse
import builtins
import contextlib
import datetime
import os
from pathlib import Path

import buckpass
import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox.utils.constants import FAILED, SUCCESS

from blackbox import blackbox

OPENBOX_URL: buckpass.openbox_api.URL = buckpass.openbox_api.URL(
    host=os.getenv("VIRTUAL_MACHINE_ADDRESS") or "", port=8000
)

ORCHESTRATOR_URL = f"http://{os.getenv('VIRTUAL_MACHINE_ADDRESS')}:8080/"


def main() -> None:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    _ = argument_parser.add_argument("-t", "--task", required=True)
    _ = argument_parser.add_argument("-f", "--file", required=True)
    args = argument_parser.parse_args()

    model_file: str = str(args.file).strip()
    model_path = Path(model_file)
    assert model_path.exists()
    assert model_path.is_file()

    openbox_task_id: buckpass.core.OpenBoxTaskId = buckpass.core.OpenBoxTaskId(
        args.task
    ).strip()

    document: libsbml.SBMLDocument = libsbml.readSBML(
        f"{os.getenv('CLUSTER_PROJECT_PATH')}{model_file}"
    )
    biological_model = BiologicalModel.load(document)

    suggestion: dict[str, float] = buckpass.openbox_api.get_suggestion(
        url=OPENBOX_URL, task_id=openbox_task_id
    )

    blackbox_start_time = datetime.datetime.now(tz=datetime.UTC)
    loss: float | None = None
    with contextlib.suppress(builtins.BaseException):
        loss = blackbox(
            biological_model,
            virtual_patient={
                kinetic_constant: 10**value
                for kinetic_constant, value in suggestion.items()
            },
        )
    blackbox_end_time = datetime.datetime.now(tz=datetime.UTC)

    trial_info = {
        "cost": (blackbox_end_time - blackbox_start_time).seconds,
        "worker_id": os.getenv("SLURM_JOB_ID"),
        "trial_info": None,
    }

    buckpass.openbox_api.update_observation(
        url=OPENBOX_URL,
        task_id=openbox_task_id,
        config_dict=suggestion,
        objectives=[
            loss
            if loss
            else len(biological_model.sbml_document.getModel().getNumSpecies())
            * 10
        ],
        constraints=[],
        trial_info=trial_info,
        trial_state=SUCCESS if loss else FAILED,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, flush=True)
