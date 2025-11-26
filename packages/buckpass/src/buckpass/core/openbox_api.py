import hashlib
import json
import re
from typing import Any

import requests
from openbox.utils.config_space import Configuration
from openbox.utils.config_space import json as config_json
from typing_extensions import override

TaskId = str


TCP_MAX_PORT = 65535


class URL:
    __url: str

    def __init__(self, host: str, port: int) -> None:
        assert 0 <= port <= TCP_MAX_PORT
        assert re.match("", host)

        self.__url = f"http://{host}:{port}/bo_advice/"

    @override
    def __str__(self) -> str:
        return self.__url

    @override
    def __repr__(self) -> str:
        return self.__url


# TODO: add check_setup
def register_task(
    config_space,
    server_ip,
    port,
    email: str,
    password: str,
    task_name: str = "task",
    num_objectives: int = 1,
    num_constraints: int = 0,
    advisor_type: str = "default",
    sample_strategy: str = "bo",
    surrogate_type: None | str = None,
    acq_type: None | str = None,
    acq_optimizer_type: str = "local_random",
    max_runs: int = 100,
    init_strategy: str = "random_explore_first",
    initial_configurations=None,
    initial_runs: int = 3,
    random_state: None | int = None,
    max_runtime_per_trial=None,
    active_worker_num: int = 1,
    parallel_type: str = "async",
    ref_point: list[float] = [],
) -> str:
    # email = email
    md5 = hashlib.md5()
    md5.update(password.encode("utf-8"))
    password = md5.hexdigest()

    # Store and serialize config space
    # config_space = config_space
    config_space_json = config_json.write(config_space)

    # Check setup
    # self.num_objectives = num_objectives
    # self.num_constraints = num_constraints
    # self.acq_type = acq_type
    # constraint_surrogate_type = None
    # self.surrogate_type = surrogate_type
    # check_setup()

    # Set options
    if initial_configurations is not None and isinstance(
        initial_configurations[0], Configuration
    ):
        initial_configurations = [
            config.get_dictionary() for config in initial_configurations
        ]
    # self.max_runs = max_runs
    options = {
        "optimization_strategy": sample_strategy,
        "surrogate_type": surrogate_type,
        "acq_type": acq_type,
        "acq_optimizer_type": acq_optimizer_type,
        "init_strategy": init_strategy,
        "initial_configurations": initial_configurations,
        "initial_trials": initial_runs,
        "random_state": random_state,
        "ref_point": ref_point,
    }

    # Construct base url.
    base_url = "http://%s:%d/bo_advice/" % (server_ip, port)

    # Register task
    res = requests.post(
        base_url + "task_register/",
        data={
            "advisor_type": advisor_type,
            "email": email,
            "password": password,
            "task_name": task_name,
            "config_space_json": config_space_json,
            "num_constraints": num_constraints,
            "num_objectives": num_objectives,
            "max_runs": max_runs,
            "options": json.dumps(options),
            "max_runtime_per_trial": max_runtime_per_trial,
            "active_worker_num": active_worker_num,
            "parallel_type": parallel_type,
        },
    )
    res = json.loads(res.text)

    if res["code"] == 1:
        task_id = res["task_id"]
        return task_id
    else:
        raise Exception("Server error %s" % res["msg"])


def get_suggestion(url: URL, task_id: TaskId):
    result = requests.post(
        f"{url}get_suggestion/", data={"task_id": task_id}, timeout=10000
    )
    response: dict[str, Any] = json.loads(result.text)

    assert response["code"]
    return json.loads(response["res"])


def update_observation(
    url: URL,
    task_id: TaskId,
    config_dict,
    objectives,
    constraints=[],
    trial_info={},
    trial_state=0,
) -> None:
    result = requests.post(
        f"{url}update_observation/",
        data={
            "task_id": task_id,
            "config": json.dumps(config_dict),
            "objectives": json.dumps(objectives),
            "constraints": json.dumps(constraints),
            "trial_state": trial_state,
            "trial_info": json.dumps(trial_info),
        },
        timeout=10000,
    )

    response = json.loads(result.text)

    assert response["code"]
