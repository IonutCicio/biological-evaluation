import json
import os
import random

import libsbml
from biological_scenarios_generation.model import BiologicalModel

from core.blackbox import Config, objective_function
from core.lib import init, openbox_config

option, logger = init()


def main() -> None:
    filepath: str | None = os.getenv("SBML")
    assert filepath
    print(filepath)

    biological_model = BiologicalModel.load(libsbml.readSBML(filepath))
    _, num_objectives, _ = openbox_config(biological_model)

    history = []
    best_config: None | dict[str, float] = None
    best_observations: None | list[float] = None
    best_value: None | float = None
    _objective_function = objective_function(biological_model, num_objectives)
    for _ in range(1000):
        config: Config = {
            kinetic_constant: random.uniform(
                category.interval().lower_bound, category.interval().upper_bound
            )
            for kinetic_constant, category in biological_model.kinetic_constants.items()
        }

        result = _objective_function(config)["objectives"]
        if best_config and best_value:
            if sum(result) < best_value:
                best_config = config
                best_observations = result
                best_value = sum(result)
            print(sum(result), best_value)
        else:
            best_config = config
            best_value = sum(result)

        history.append(
            {"config": config, "observations": result, "result": sum(result)}
        )

    print(best_config)
    print(best_observations)
    print(best_value)

    with open("logs.json", "w") as file:
        file.write(json.dumps(history))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("")

    # config: Config = buckpass.openbox_api.get_suggestion(  # pyright: ignore[reportAny]
    #     url=OPENBOX_URL, task_id=option.task_id
    # )
    # _timedelta_suggestion = perf_counter() - start_time
    # logger.info(config)

    # Compute objective function value

    # start_time = perf_counter()
    # _timedelta_blackbox = perf_counter() - start_time
    # logger.info(result["objectives"])
