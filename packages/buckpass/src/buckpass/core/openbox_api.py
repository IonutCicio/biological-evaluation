import json
import re
from typing import Any

import requests
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


def get_suggestion(url: URL, task_id: TaskId):
    result = requests.post(
        f"{url}get_suggestion/", data={"task_id": task_id}, timeout=10000
    )
    response: dict[str, Any] = json.loads(result.text)

    print("suggestion!", response)
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

    print("observation!", result.text)
    response = json.loads(result.text)

    assert response["code"]
