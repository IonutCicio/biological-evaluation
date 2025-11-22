import json
from pathlib import Path

from matplotlib import pylab

from lib import init

_ = init()


def main() -> None:
    tasks: list[str] = [
        "692074b32da3c47a0b4e07c8",
        "692075f42da3c47a0b4e0a40",
        "692076942da3c47a0b4e0b7c",
        "692077352da3c47a0b4e0cbc",
        "692077d52da3c47a0b4e0df5",
        "692078772da3c47a0b4e0f28",
        "692079182da3c47a0b4e105c",
        "692079b82da3c47a0b4e11b0",
        "69207a582da3c47a0b4e12ff",
        "69207af82da3c47a0b4e143a",
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
        _ = pylab.savefig(f"docs/{task_id}.svg")
        _ = pylab.show()


if __name__ == "__main__":
    main()
