import argparse
import os
import re
from pathlib import Path

import buckpass
from biological_scenarios_generation.model import BiologicalModel, libsbml
from buckpass.policy.burst import BurstPolicy
from openbox import space

policy: (
    None | BurstPolicy[buckpass.core.SlurmJobId, buckpass.core.OpenBoxTaskId]
) = None


def main() -> None:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    _ = argument_parser.add_argument("-f", "--file", required=True)
    args = argument_parser.parse_args()

    model_file: str = str(args.file)
    model_path = Path(model_file)
    assert model_path.exists()
    assert model_path.is_file()

    document: libsbml.SBMLDocument = libsbml.readSBML(model_file)
    biological_model: BiologicalModel = BiologicalModel.load(document)

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

    max_runs = 10000

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

    task_id = buckpass.openbox_api.register_task(
        config_space=_space,
        server_ip="localhost",
        port=8000,
        email="test@test.test",
        password=str(os.getenv("OPENBOX_PASSWORD")),
        task_name=model_file,
        num_objectives=num_objectives,
        num_constraints=0,
        advisor_type="default",
        sample_strategy="bo",
        surrogate_type="prf",
        acq_type="mesmo",
        parallel_type="async",
        acq_optimizer_type="random_scipy",
        initial_runs=0,
        random_state=1,
        active_worker_num=1,
        max_runs=max_runs,
    )

    _ = BurstPolicy(
        args=f"--task {task_id} --file {model_file}",
        size=buckpass.core.IntGTZ(max_runs),
        submitter=buckpass.Uniroma1Submitter(),
    )


if __name__ == "__main__":
    main()

# from openbox.artifact.remote_advisor import RemoteAdvisor

# remote_advisor
# - 'tpe': Tree-structured Parzen Estimator
# - 'ea': Evolutionary Algorithms
# - 'random': Random Search
# - 'mcadvisor': Bayesian Optimization with Monte Carlo Sampling

# remote_advisor: RemoteAdvisor = RemoteAdvisor(
#     config_space=_space,
#     server_ip="localhost",
#     port=8000,
#     email="test@test.test",
#     password=os.getenv("OPENBOX_PASSWORD"),
#     task_name=model_file,
#     num_objectives=1,
#     num_constraints=0,
#     advisor_type="tpe",
#     sample_strategy="bo",
#     surrogate_type="prf",
#     acq_type="ei",
#     parallel_type="async",
#     acq_optimizer_type="random_scipy",
#     initial_runs=0,
#     random_state=1,
#     active_worker_num=1,
#     max_runs=1000,
# )
# remote_advisor.task_id
