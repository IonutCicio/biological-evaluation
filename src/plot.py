import json
from pathlib import Path
from typing import Any

from matplotlib import pylab

from core.lib import init

_ = init()


def main() -> None:
    with Path("task.json").open() as file:
        tasks = json.loads(file.read())

    tasks_of_interest: dict[str, Any] = {
        task["_id"]["$oid"]: task
        for task in tasks
        if task["create_time"]["$date"].startswith("2025-11-24")
    }

    with Path("runhistory.json").open() as file:
        runhistory = json.loads(file.read())

    for task_id, task in tasks_of_interest.items():
        task_runhistory = [
            run for run in runhistory if run["task_id"] == task_id
        ]

        non_optimal_x: list[float] = []
        non_optimal_y: list[float] = []

        optimal_x: list[float] = []
        optimal_y: list[float] = []

        optimal_cost = 10e10

        for x, run in enumerate(task_runhistory):
            trial_info = json.loads(run["trial_info"])
            if "blackbox_duration" in trial_info:
                print(trial_info["blackbox_duration"])
            cost: float = sum(run["result"])
            if cost < optimal_cost:
                optimal_cost = cost
                optimal_x.append(x)
                optimal_y.append(cost)
            else:
                non_optimal_x.append(x)
                non_optimal_y.append(min(cost, 20))

        optimal_x.append(len(task_runhistory))
        optimal_y.append(optimal_cost)
        # TODO: set plot name
        _ = pylab.plot(non_optimal_x, non_optimal_y, "o", color="gray")
        _ = pylab.plot(optimal_x, optimal_y, "o-")
        _ = pylab.savefig(f"docs/{task_id}.svg")
        _ = pylab.ylim(bottom=0, top=20)
        _ = pylab.title(label=task["task_name"])
        _ = pylab.show()


if __name__ == "__main__":
    main()

# trial_info["load_duration"]
# trial_info["start_time"]

# if cost < 3:
#     print(run["config"], end="\n\n")
# print(tasks_of_interest)

# if len(optimal_y) + len(non_optimal_y) > 10:
# print(task["task_name"])
# tasks: list[str] = [
#     "692074b32da3c47a0b4e07c8",
#     "692075f42da3c47a0b4e0a40",
#     "692076942da3c47a0b4e0b7c",
#     "692077352da3c47a0b4e0cbc",
#     "692077d52da3c47a0b4e0df5",
#     "692078772da3c47a0b4e0f28",
#     "692079182da3c47a0b4e105c",
#     "692079b82da3c47a0b4e11b0",
#     "69207a582da3c47a0b4e12ff",
#     "69207af82da3c47a0b4e143a",
# ]

# print(tasks_of_interest)
# print(tasks[0]["_id"]["$oid"])
# print(tasks[0]["create_time"]["$date"])
# exit()

# print(run["result"])
# exit()
