import os

import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox import Optimizer

from blackbox import FAIL_COST, Config, blackbox
from lib import init, openbox_config

_, logger = init()


filepath = os.getenv("SBML")
assert filepath


def _custom_objective_function(config: Config) -> dict[str, list[float]]:
    biological_model: BiologicalModel = BiologicalModel.load(
        sbml_document=libsbml.readSBML(filepath)
    )
    _space, num_objectives, num_constraints = openbox_config(biological_model)
    objectives: list[float] = []
    try:
        cost = blackbox(
            biological_model,
            {
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
        sbml_document=libsbml.readSBML(filepath)
    )
    _space, num_objectives, num_constraints = openbox_config(biological_model)

    # TODO: add missing arguments
    optimizer = Optimizer(
        objective_function=_custom_objective_function,
        config_space=_space,
        num_objectives=num_objectives,
        num_constraints=num_constraints,
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        max_runs=int(os.getenv("MAX_RUNS", default="1000")),
        surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
        acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
        acq_optimizer_type=os.getenv(
            "ACQ_OPTIMIZER_TYPE", default="random_scipy"
        ),
        initial_runs=0,
        logging_dir=f"{os.getenv('HOME')}/logs",
        random_state=1,  # TODO: env variable for random_state
    )

    history = optimizer.run()


# parallel_strategy="async",
# batch_size=8,
# batch_strategy="default",


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
