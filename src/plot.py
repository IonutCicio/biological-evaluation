import json
from pathlib import Path

from matplotlib import pylab

from lib import init

_ = init()


def main() -> None:
    # load_dotenv()

    tasks: list[str] = [
        "691f32922da3c47a0b4e031c",
        "691f04402da3c47a0b4dfd3c",
        "691ed6ed967b65f7163edb6d",
    ]

    with Path("data.json").open() as file:
        runhistory = json.loads(file.read())

    for task_id in tasks:
        task_runhistory = [
            run for run in runhistory if run["task_id"] == task_id
        ]

        non_optimal_x: list[float] = []
        non_optimal_y: list[float] = []

        optimal_x: list[float] = []
        optimal_y: list[float] = []

        optimal_cost = 10e10

        for x, run in enumerate(task_runhistory):
            cost: float = sum(run["result"])
            if cost < optimal_cost:
                optimal_cost = cost
                optimal_x.append(x)
                optimal_y.append(cost)
            else:
                non_optimal_x.append(x)
                non_optimal_y.append(cost)

        optimal_x.append(len(task_runhistory))
        optimal_y.append(optimal_cost)

        _ = pylab.plot(non_optimal_x, non_optimal_y, "o", color="gray")
        _ = pylab.plot(optimal_x, optimal_y, "o-")
        _ = pylab.savefig(f"{task_id}.svg")
        _ = pylab.show()


if __name__ == "__main__":
    main()
