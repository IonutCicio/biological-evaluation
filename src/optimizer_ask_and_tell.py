import os

import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox import Advisor, Observation

from core.blackbox import Config, objective_function_multi_objective
from src.core.lib import init, openbox_config_multiobjective

option, logger = init()


def main() -> None:
    filepath = os.getenv("SBML")
    assert filepath

    biological_model: BiologicalModel = BiologicalModel.load(
        libsbml.readSBML(filepath)
    )
    _space, num_objectives, num_constraints = openbox_config_multiobjective(
        biological_model
    )
    _objective_function = objective_function_multi_objective(
        biological_model, num_objectives
    )

    max_runs = int(os.getenv("MAX_RUNS", default="1000"))
    advisor = Advisor(
        config_space=_space,
        num_objectives=num_objectives,
        num_constraints=num_constraints,
        parallel_strategy=os.getenv("PARALLEL_STRATEGY", default="async"),
        batch_size=int(os.getenv("BATCH_SIZE", default="8")),
        batch_strategy="default",
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        max_runs=int(os.getenv("MAX_RUNS", default="1000")),
        surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
        acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
        acq_optimizer_type=os.getenv(
            "ACQ_OPTIMIZER_TYPE", default="random_scipy"
        ),
        initial_runs=0,
        logging_dir=f"{os.getenv('HOME')}/logs",
        random_state=int(os.getenv("RANDOM_STATE", default="1")),
        task_id=option.env[0],
    )

    for _ in range(max_runs):
        config: Config = advisor.get_suggestion()
        result = _objective_function(config)
        advisor.update_observation(
            Observation(config=config, objectives=result["objectives"])
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
