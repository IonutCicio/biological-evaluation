import os
import re

import buckpass
from biological_scenarios_generation.model import BiologicalModel, libsbml
from buckpass.policy.burst import BurstPolicy
from openbox import space

from lib import source_env

args = source_env()

policy: (
    None | BurstPolicy[buckpass.core.SlurmJobId, buckpass.core.OpenBoxTaskId]
) = None


def main() -> None:
    filepath = os.getenv("SBML")
    assert filepath

    biological_model: BiologicalModel = BiologicalModel.load(
        libsbml.readSBML(filepath)
    )

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
    )

    max_runs = int(os.getenv("MAX_RUNS") or 1000)

    task_id = buckpass.openbox_api.register_task(
        config_space=_space,
        server_ip="localhost",
        port=8000,
        email=str(os.getenv("OPENBOX_EMAIL")),
        password=str(os.getenv("OPENBOX_PASSWORD")),
        task_name=filepath,
        num_objectives=num_objectives,
        num_constraints=0,
        advisor_type=str(os.getenv("ADVISOR_TYPE") or "default"),
        sample_strategy=str(os.getenv("SAMPLE_STRATEGY") or "bo"),
        surrogate_type=str(os.getenv("SURROGATE_TYPE") or "prf"),
        acq_type=str(os.getenv("ACQ_TYPE") or "mesmo"),
        parallel_type="async",
        acq_optimizer_type=str(os.getenv("SURROGATE_TYPE") or "random_scipy"),
        initial_runs=0,
        random_state=1,
        active_worker_num=int(os.getenv("RANDOM_STATE") or 1),
        max_runs=max_runs,
    )

    _ = BurstPolicy(
        args=f"--task {task_id} --env {args.env}",
        size=buckpass.core.IntGTZ(max_runs),
        submitter=buckpass.Uniroma1Submitter(),
    )


if __name__ == "__main__":
    main()
