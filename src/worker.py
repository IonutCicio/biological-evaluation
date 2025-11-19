import argparse
import builtins
import contextlib
import os
from datetime import UTC, datetime
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

    start_time = datetime.now(tz=UTC)

    model_file: str = str(args.file).strip()
    model_path = Path(model_file)
    assert model_path.exists()
    assert model_path.is_file()

    openbox_task_id: buckpass.core.OpenBoxTaskId = buckpass.core.OpenBoxTaskId(
        args.task
    ).strip()

    load_model_start_time = datetime.now(tz=UTC)
    document: libsbml.SBMLDocument = libsbml.readSBML(
        f"{os.getenv('CLUSTER_PROJECT_PATH')}{model_file}"
    )
    biological_model = BiologicalModel.load(document)
    load_model_end_time = datetime.now(tz=UTC)

    suggestion_start_time = datetime.now(tz=UTC)
    suggestion: dict[str, float] = buckpass.openbox_api.get_suggestion(
        url=OPENBOX_URL, task_id=openbox_task_id
    )
    suggestion_end_time = datetime.now(tz=UTC)

    blackbox_start_time = datetime.now(tz=UTC)
    loss: float | None = None
    with contextlib.suppress(builtins.BaseException):
        loss = blackbox(
            biological_model,
            virtual_patient={
                kinetic_constant: 10**value
                for kinetic_constant, value in suggestion.items()
            },
        )
    blackbox_end_time = datetime.now(tz=UTC)

    observation_start_time = datetime.now(tz=UTC)
    buckpass.openbox_api.update_observation(
        url=OPENBOX_URL,
        task_id=openbox_task_id,
        config_dict=suggestion,
        objectives=[
            loss
            if loss
            else biological_model.sbml_document.getModel().getNumSpecies()
        ],
        constraints=[],
        trial_info={
            "cost": str(blackbox_end_time - blackbox_start_time),
            "worker_id": os.getenv("SLURM_JOB_ID"),
            "trial_info": f"""
            {{
                "start_time": {start_time},
                "load_duration": {load_model_end_time - load_model_start_time},
                "suggestion_duration": {suggestion_end_time - suggestion_start_time}
            }}
        """,
        },
        trial_state=SUCCESS if loss else FAILED,
    )
    observation_end_time = datetime.now(tz=UTC)
    print(observation_end_time - observation_start_time, flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e, flush=True)
