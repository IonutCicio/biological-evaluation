import os

import buckpass
from biological_scenarios_generation.model import BiologicalModel, libsbml
from buckpass.policy.burst import BurstPolicy

from core.lib import init, openbox_config_multiobjective

option, logger = init()


def main() -> None:
    filepath: str | None = os.getenv("SBML")
    assert filepath

    biological_model: BiologicalModel = BiologicalModel.load(
        sbml_document=libsbml.readSBML(filepath)
    )

    _space, num_objectives, num_constraints = openbox_config_multiobjective(
        biological_model
    )
    max_runs: int = int(os.getenv("MAX_RUNS", default="1000"))

    task_id = buckpass.openbox_api.register_task(
        config_space=_space,
        server_ip="localhost",
        port=8000,
        email=str(os.getenv("OPENBOX_EMAIL")),
        password=str(os.getenv("OPENBOX_PASSWORD")),
        task_name=f"{filepath}_{'_'.join(option.env)}",
        num_objectives=num_objectives,
        num_constraints=num_constraints,
        advisor_type=os.getenv("ADVISOR_TYPE", default="default"),
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
        acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
        parallel_type=os.getenv("PARALLEL_STRATEGY", default="async"),
        acq_optimizer_type=os.getenv(
            "ACQ_OPTIMIZER_TYPE", default="random_scipy"
        ),
        initial_runs=0,
        random_state=int(os.getenv("RANDOM_STATE", default="1")),
        active_worker_num=int(os.getenv("BATCH_SIZE", default="8")),
        max_runs=max_runs,
        max_runtime_per_trial=int(
            os.getenv("MAX_RUNTIME_PER_TRIAL", default="30")
        ),
    )

    _ = BurstPolicy(
        args=f"-t {task_id} -e {' '.join(map(str, option.env))}",
        size=buckpass.core.IntGTZ(max_runs),
        submitter=buckpass.Uniroma1Submitter(),
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
