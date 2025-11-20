import json
import os
from pathlib import Path

from dotenv import load_dotenv
from matplotlib import pylab

# TASK_ID: str = "691ed6ed967b65f7163edb6d"
TASK_ID: str = "691f04402da3c47a0b4dfd3c"


def main() -> None:
    load_dotenv()
    # print(os.getenv("NEO4J_URL_REACTOME"))
    # print(os.getenv("VIRTUAL_MACHINE_PROJECT_PATH"))
    # print(os.getenv("NUM_THREADS"))
    # exit()

    with Path("data.json").open() as file:
        runhistory = json.loads(file.read())

    task_runhistory = [run for run in runhistory if run["task_id"] == TASK_ID]

    non_optimal_x = []
    non_optimal_y = []

    optimal_x = []
    optimal_y = []

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
    _ = pylab.show()


if __name__ == "__main__":
    main()

# costs_2.append(cost)
# ord.append(x)

# costs = []
# ord = []
# costs_2 = []
# min_cost = 100
# costs_3 = []
# order_3 = []
# total_time = pd.to_timedelta("0")
# biggest = pd.to_timedelta("0")

# datetime.strptime('13:55:26', '%H:%M:%S').time()
# count = 0
# for order, run in enumerate(task_runhistory):
#     cost: float = 0.0
#     cost += sum(run["result"])
#     delta = pd.to_timedelta(
#         run["trial_info"]
#         .splitlines()[4]
#         .replace('"suggestion_duration": ', "")
#         .strip()
#     )
#     total_time += delta
#     if delta > biggest:
#         biggest = delta
#     count += 1
#
#     # print(run["trial_info"].replace(": ", ': "').replace(","))
#     costs.append((cost, order, run))
#     if cost < min_cost:
#         min_cost = cost
#         costs_3.append(cost)
#         order_3.append(order)
#     else:
#         costs_2.append(cost)
#         ord.append(order)
# print(biggest)
# print(total_time / count)

# costs_3.append(min_cost)
# order_3.append(len(task_runhistory))

# print(costs_3)
# exit()

# for cost, order, run in sorted(costs):
#     print(cost, order)

# for run in data:
#     if run["task_id"] == TASK_ID:
#         runs.append(run)

# print(len(runs))
# print(runs[0])
# exit()
# for obj in run["result"]:
#     cost += float(list(obj.values())[0])
# print(sorted(costs))
# if "$numberInt" in obj:
#     cost += float(obj["$numberInt"])
# else:
# if "$numberFloat" in obj:
#     cost += float(obj["$numberFloat"])
#     print(run)
#     exit()
# print(cost)

# print(runs[0]["result"])
# for t in data:
#     if t["_id"]["$oid"] == TASK:
#         tasks.append(t)
#
# print(tasks[0].keys())

# print(data[0])

# cost
# if cost
# else biological_model.sbml_document.getModel().getNumSpecies()
# TODO: + transitory

# blackbox_start_time = datetime.now(tz=UTC)
# blackbox_end_time = datetime.now(tz=UTC)

# load_start_time = datetime.now(tz=UTC)
# biological_model =
# load_end_time = datetime.now(tz=UTC)
# suggestion: dict[str, float]
# suggestion_start_time = datetime.now(tz=UTC)
# suggestion_end_time = datetime.now(tz=UTC)
