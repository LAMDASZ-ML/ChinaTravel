import os
import sys

project_root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if project_root_path not in sys.path:
    sys.path.append(project_root_path)
if os.path.dirname(project_root_path) not in sys.path:
    sys.path.append(os.path.dirname(project_root_path))

from agent.llms import AbstractLLM


class TPCLLM(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.name = "EmptyLLM"

    def _get_response(self, messages, one_line, json_mode):
        return "Empty LLM response"

