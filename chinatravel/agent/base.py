import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from json import JSONDecodeError

from abc import ABC, abstractmethod
from agent.utils import decode_numpy_dict


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except JSONDecodeError:
        return False


class AgentError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class AgentReturnError(AgentError):
    pass


class AgentReturnInfoError(AgentError):
    pass


class DecodeLogError(AgentError):
    pass


class AgentReturnInfo:
    """
    This class is used to store the return information of an agent.
    It contains two attributes: ans and log.
    ans: The answer of the agent. Should be a string.
    log: The log of the agent. It can be transformed to json.
    """

    def __init__(self, ans, log: dict = {}):
        if not isinstance(ans, str):
            raise AgentReturnInfoError("ans must be a string")
        if not is_jsonable(log):
            raise AgentReturnInfoError("log must be a json object")
        try:
            log = decode_numpy_dict(log)
        except Exception as e:
            raise DecodeLogError(f"Error when decoding log: {e}")
        self.data = {"ans": ans, "log": log}

    def __getitem__(self, key):
        return self.data[key]


class AbstractAgent(ABC):
    def __init__(self, env):

        self._env = env
        self._ans = None
        self._log = None

    def __call__(self, query):

        return_info = self.run(query)

        if not isinstance(return_info, AgentReturnInfo):
            raise AgentReturnError(
                "Return value must be an instance of AgentReturnInfo"
            )
        self._reset()  # Default reset, reset env, ans and log
        self.reset()  # Reset the agent, just those added in the subclass

        return return_info

    @property
    def env(self):
        return self._env

    @property
    def ans(self):
        return self._ans

    @property
    def log(self):
        return self._log

    def _reset(self):
        self._env.reset()
        self._ans = None
        self._log = None

    @abstractmethod
    def run(self, query) -> AgentReturnInfo:
        """
        You should implement this method to run the agent.
        Return the answer and log in the form of AgentReturnInfo.
        """
        pass

    @abstractmethod
    def reset(self):
        pass
