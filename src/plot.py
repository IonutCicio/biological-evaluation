import json
from pathlib import Path
from typing import Any

import numpy as np
from matplotlib import pylab

from core.lib import init

_ = init()


def main2() -> None:
    with Path("task.json").open() as file:
        tasks = json.loads(file.read())

    tasks_of_interest: dict[str, Any] = {
        task["_id"]["$oid"]: task
        for task in tasks
        if task["_id"]["$oid"] == "69271f4f00d7c938c5171a01"
        # 69271f4f00d7c938c5171a01
        # "6927196100d7c938c5171957"
        # "692718b200d7c938c51718d5"
        # "692711ee00d7c938c517185d"
        # "692711ee00d7c938c517185d"
        # "69270d5b00d7c938c517175c"
        # if task["create_time"]["$date"].startswith("2025-11-26")
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
                non_optimal_y.append(cost)
            print(cost)

        optimal_x.append(len(task_runhistory))
        optimal_y.append(optimal_cost)
        if len(optimal_x) > 2:
            _ = pylab.plot(non_optimal_x, non_optimal_y, "o", color="gray")
            _ = pylab.plot(optimal_x, optimal_y, "o-")
            _ = pylab.ylim(bottom=0, top=50)
            _ = pylab.savefig(f"docs/{task_id}.svg")
            _ = pylab.title(label=task["task_name"])
            _ = pylab.show()


# def main() -> None:
#     filename = "co_2_cytosol_molecules_transport"
#     # filename = "nitric_oxide_signal_transduction"
#     with Path(f"{filename}.json").open() as file:
#         # print(file.read())
#         data = json.loads(file.read())
#         # print(data[0])
#
#         # perf_y = []
#         reactions_y = []
#         entities_y = []
#         x = []
#         for max_depth in range(49):
#             x.append(max_depth + 1)
#             # perf_y.append(data[max_depth]["perf"])
#             reactions_y.append(data[max_depth]["reaction_like_events"])
#             entities_y.append(data[max_depth]["physical_entities"])
#
#         # _ = pylab.plot(x, perf_y)
#         # set_xlabel('X-axis Label')
#         # pylab.set_ylabel('Y-axis Label')
#
#         _ = pylab.plot(x, reactions_y)
#         _ = pylab.grid(visible=True)
#         _ = pylab.xlabel("max query depth", fontsize=18)
#         _ = pylab.ylabel("number of reactions", fontsize=18)
#         _ = pylab.title(label="number of reactions per depth", fontsize=18)
#         _ = pylab.savefig(f"report/images/{filename}_reactions.png")
#         # _ = pylab.show()
#
#         pylab.clf()
#         _ = pylab.plot(x, entities_y)
#         _ = pylab.grid(visible=True)
#         _ = pylab.xlabel("max query depth", fontsize=18)
#         _ = pylab.ylabel("number of physical entities", fontsize=18)
#         _ = pylab.title(
#             label="number of physical entities per depth", fontsize=18
#         )
#         _ = pylab.savefig(f"report/images/{filename}_entities.png")
#         # _ = pylab.show()
#
#         # x = []
#         points_per_depth = {}
#         x_3 = []
#         perf_y = []
#
#         for iteration in range(10):
#             for max_depth in range(49):
#                 x_3.append(max_depth + 1)
#                 perf_y.append(data[iteration * 49 + max_depth]["perf"])
#                 if max_depth in points_per_depth:
#                     points_per_depth[max_depth].append(
#                         data[iteration * 49 + max_depth]["perf"]
#                     )
#                 else:
#                     points_per_depth[max_depth] = [
#                         data[iteration * 49 + max_depth]["perf"]
#                     ]
#                 # perf_y.append(data[max_depth]["perf"])
#
#         x_mean = []
#         y_mean = []
#         for x, points in points_per_depth.items():
#             x_mean.append(x)
#             y_mean.append(np.mean(points))
#
#         pylab.clf()
#         _ = pylab.plot(x_3, perf_y, "o")
#         _ = pylab.plot(x_mean, y_mean)
#         _ = pylab.grid(visible=True)
#         _ = pylab.xlabel("max query depth", fontsize=18)
#         _ = pylab.ylabel("query duration seconds", fontsize=18)
#         _ = pylab.title(label="query duration (seconds) per depth", fontsize=18)
#         _ = pylab.savefig(f"report/images/{filename}_time.png")
#         # _ = pylab.show()
#         pylab.clf()
#
#         # max_depth = 0
#         # for obj in data:
#         #     max_depth = (max_depth + 1) % 51
#
#         # _ = pylab.plot(non_optimal_x, non_optimal_y, "o", color="gray")
#         # _ = pylab.plot(optimal_x, optimal_y, "o-")
#         # _ = pylab.ylim(bottom=0, top=20)
#         # _ = pylab.savefig(f"docs/{task_id}.svg")
#         # _ = pylab.title(label=task["task_name"])
#         # _ = pylab.show()
#         pass


def main() -> None:
    with open("random_logs.json") as file:
        random_logs = json.loads(file.read())

    best_observation = None
    best_value: float | None = None

    non_optimal_x: list[float] = []
    non_optimal_y: list[float] = []
    optimal_x: list[float] = []
    optimal_y: list[float] = []

    for i, observation in enumerate(random_logs["observations"]):
        value = sum(observation["objectives"])
        if best_value:
            if value < best_value:
                best_observation = observation
                best_value = value
                optimal_x.append(i)
                optimal_y.append(value)
            else:
                non_optimal_x.append(i)
                non_optimal_y.append(value)
        else:
            best_value = value
            best_observation = observation
            optimal_x.append(i)
            optimal_y.append(value)

        # for task_id, task in tasks_of_interest.items():
        #     task_runhistory = [
        #         run for run in runhistory if run["task_id"] == task_id
        #     ]

        # optimal_cost = 10e10

        # for x, run in enumerate(task_runhistory):
        #     trial_info = json.loads(run["trial_info"])
        #     if "blackbox_duration" in trial_info:
        #         print(trial_info["blackbox_duration"])
        #     cost: float = sum(run["result"])
        #     if cost < optimal_cost:
        #         optimal_cost = cost
        #         optimal_x.append(x)
        #         optimal_y.append(cost)
        #     else:
        #         non_optimal_x.append(x)
        #         non_optimal_y.append(min(cost, 20))

    optimal_x.append(len(random_logs["observations"]))
    optimal_y.append(best_value or 0)

    _ = pylab.plot(non_optimal_x, non_optimal_y, "o", color="gray")
    _ = pylab.plot(optimal_x, optimal_y, "o-")
    _ = pylab.ylim(bottom=0, top=20)
    _ = pylab.title(label="task_name")
    _ = pylab.show()

    # _ = pylab.savefig(f"docs/{task_id}.svg")
    print(best_observation["config"])
    print(best_value)


if __name__ == "__main__":
    main()
    # main2()

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
