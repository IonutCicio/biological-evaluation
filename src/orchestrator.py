import os

import buckpass
from biological_scenarios_generation.model import BiologicalModel, libsbml
from buckpass.policy.burst import BurstPolicy

from lib import config, init

option, logger = init()


def main() -> None:
    filepath: str | None = os.getenv("SBML")
    assert filepath

    biological_model: BiologicalModel = BiologicalModel.load(
        document=libsbml.readSBML(filepath)
    )

    _space, num_objectives = config(biological_model)
    max_runs: int = int(os.getenv("MAX_RUNS", default="1000"))

    task_id = buckpass.openbox_api.register_task(
        config_space=_space,
        server_ip="localhost",
        port=8000,
        email=str(os.getenv("OPENBOX_EMAIL")),
        password=str(os.getenv("OPENBOX_PASSWORD")),
        task_name=f"{filepath}_{'_'.join(option.env)}",
        num_objectives=int(num_objectives),
        num_constraints=0,
        advisor_type=os.getenv("ADVISOR_TYPE", default="default"),
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
        acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
        parallel_type="async",
        acq_optimizer_type=os.getenv(
            "ACQ_OPTIMIZER_TYPE", default="random_scipy"
        ),
        initial_runs=0,
        random_state=1,
        active_worker_num=int(os.getenv("RANDOM_STATE", default="1")),
        max_runs=max_runs,
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
