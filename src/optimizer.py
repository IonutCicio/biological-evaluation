import os

from biological_scenarios_generation.model import BiologicalModel, libsbml
from openbox import ParallelOptimizer

from blackbox import config, objective_function
from lib import init

option, logger = init()


def main() -> None:
    filepath = os.getenv("SBML")
    assert filepath

    biological_model: BiologicalModel = BiologicalModel.load(
        libsbml.readSBML(filepath)
    )
    _space, num_objectives = config(biological_model)

    # sbatch -J satisfiablity --cpus-per-task 32 src/satisfiablity_job.sh

    max_runs = int(os.getenv("MAX_RUNS") or 1000)

    opt = ParallelOptimizer(
        objective_function=objective_function(biological_model, num_objectives),
        config_space=_space,
        num_objectives=num_objectives,
        num_constraints=0,
        parallel_strategy="async",
        batch_size=32,
        batch_strategy="default",
        sample_strategy=os.getenv("SAMPLE_STRATEGY", default="bo"),
        max_runs=max_runs,
        surrogate_type=os.getenv("SURROGATE_TYPE", default="prf"),
        acq_type=os.getenv("ACQ_TYPE", default="mesmo"),
        acq_optimizer_type=os.getenv(
            "ACQ_OPTIMIZER_TYPE", default="random_scipy"
        ),
        initial_runs=0,
        logging_dir="",
        random_state=1,  # TODO: env variable for random_state
        advisor_kwargs={
            "advisor_type": os.getenv("ADVISOR_TYPE", default="default")
        },
    )

    _ = opt.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")
