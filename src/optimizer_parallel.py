import os

import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox import ParallelOptimizer

from core.blackbox import FAIL_COST, Config, blackbox
from core.lib import init, openbox_config_multiobjective

option, logger = init()


filepath = os.getenv("SBML")
assert filepath


def _objective_function(config: Config) -> dict[str, list[float]]:
    biological_model: BiologicalModel = BiologicalModel.load(
        sbml_document=libsbml.readSBML(filepath)
    )
    _space, num_objectives, _ = openbox_config_multiobjective(biological_model)
    objectives: list[float] = []
    try:
        cost = blackbox(
            biological_model,
            virtual_patient={
                kinetic_constant: 10**value
                for kinetic_constant, value in config.items()
            },
        )
        objectives = cost.normalization + cost.transitory
    except:
        objectives = [FAIL_COST] * num_objectives

    return {"objectives": objectives}


def main() -> None:
    biological_model: BiologicalModel = BiologicalModel.load(
        libsbml.readSBML(filepath)
    )
    _space, num_objectives, num_constraints = openbox_config_multiobjective(
        biological_model
    )
    optimizer = ParallelOptimizer(
        objective_function=_objective_function,
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

    _ = optimizer.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
