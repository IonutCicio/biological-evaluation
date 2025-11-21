import os

import libsbml
from biological_scenarios_generation.model import (
    BiologicalModel,
    VirtualPatient,
)
from openbox import ParallelOptimizer

import blackbox
from lib import init

_, logger = init()


filepath = os.getenv("SBML")
assert filepath

biological_model: BiologicalModel = BiologicalModel.load(
    libsbml.readSBML(filepath)
)
_space, num_objectives = blackbox.config(biological_model)


def _objective_function(
    virtual_patient: VirtualPatient,
) -> dict[str, list[float]]:
    biological_model: BiologicalModel = BiologicalModel.load(
        libsbml.readSBML(filepath)
    )
    _space, num_objectives = blackbox.config(biological_model)
    objectives: list[float] = []
    try:
        cost = blackbox.blackbox(biological_model, virtual_patient)
        objectives = cost.normalization + cost.transitory
    except:
        objectives = [2] * num_objectives

    return {"objectives": objectives}


def main() -> None:
    optimizer = ParallelOptimizer(
        objective_function=_objective_function,
        config_space=_space,
        num_objectives=num_objectives,
        num_constraints=0,
        parallel_strategy="async",
        batch_size=8,
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
        random_state=1,  # TODO: env variable for random_state
    )

    history = optimizer.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
