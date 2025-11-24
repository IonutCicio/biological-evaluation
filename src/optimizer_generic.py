import os

import libsbml
from biological_scenarios_generation.model import BiologicalModel
from openbox import Optimizer

from core.blackbox import objective_function
from core.lib import init, openbox_config

option, logger = init()


filepath = os.getenv("SBML")
assert filepath


def main() -> None:
    biological_model: BiologicalModel = BiologicalModel.load(
        sbml_document=libsbml.readSBML(filepath)
    )
    _space, num_objectives, num_constraints = openbox_config(biological_model)

    optimizer = Optimizer(
        objective_function=objective_function(biological_model, num_objectives),
        config_space=_space,
        num_objectives=num_objectives,
        num_constraints=num_constraints,
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        max_runs=int(os.getenv("MAX_RUNS", default="1000")),
        advisor_type=os.getenv("ADVISOR_TYPE", default="default"),
        surrogate_type=os.getenv("SURROGATE_TYPE", default="auto"),
        acq_type=os.getenv("ACQ_TYPE", default="auto"),
        acq_optimizer_type=os.getenv("ACQ_OPTIMIZER_TYPE", default="auto"),
        initial_runs=0,
        logging_dir=f"{os.getenv('HOME')}/logs",
        random_state=int(os.getenv("RANDOM_STATE", default="1")),
        task_id=option.env[0],
    )

    _ = optimizer.run()
    optimizer.get_history().save_json("random_logs.json")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
