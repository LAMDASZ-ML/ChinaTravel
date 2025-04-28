from abc import ABC, abstractmethod
from openai import OpenAI
from json_repair import repair_json
from transformers import AutoTokenizer

from vllm import LLM, SamplingParams

import sys
import os

project_root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)


def merge_repeated_role(messages):
    ptr = len(messages) - 1
    last_role = ""
    while ptr >= 0:
        cur_role = messages[ptr]["role"]
        if cur_role == last_role:
            messages[ptr]["content"] += "\n" + messages[ptr + 1]["content"]
            del messages[ptr + 1]
        last_role = cur_role
        ptr -= 1
    return messages


class AbstractLLM(ABC):
    class ModeError(Exception):
        pass

    def __init__(self):
        pass

    def __call__(self, messages, one_line=True, json_mode=False):
        if one_line and json_mode:
            raise self.ModeError(
                "one_line and json_mode cannot be True at the same time"
            )
        return self._get_response(messages, one_line, json_mode)

    @abstractmethod
    def _get_response(self, messages, one_line, json_mode):
        pass


class Deepseek(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.llm = OpenAI(
            base_url="https://api.deepseek.com",
        )
        self.name = "DeepSeek-V3"

    def _send_request(self, messages, kwargs):
        res_str = (
            self.llm.chat.completions.create(messages=messages, **kwargs)
            .choices[0]
            .message.content
        )
        res_str = res_str.strip()
        return res_str

    def _get_response(self, messages, one_line, json_mode):
        kwargs = {
            "model": "deepseek-chat",
            "max_tokens": 4096,
            "temperature": 0,
            "top_p": 0.00000001,
        }
        if one_line:
            kwargs["stop"] = ["\n"]
        elif json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            res_str = self._send_request(messages, kwargs)
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
        except Exception as e:
            print(e)
            res_str = '{"error": "Request failed, please try again."}'
        return res_str


class GLM4Plus(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.llm = OpenAI(
            base_url="https://open.bigmodel.cn/api/paas/v4",
        )
        self.name = "GLM4Plus"

    def _send_request(self, messages, kwargs):
        res_str = (
            self.llm.chat.completions.create(messages=messages, **kwargs)
            .choices[0]
            .message.content
        )
        res_str = res_str.strip()
        return res_str

    def _get_response(self, messages, one_line, json_mode):
        kwargs = {
            "model": "glm-4-plus",
            "max_tokens": 4095,
            "temperature": 0,
            "top_p": 0.01,
        }
        if one_line:
            kwargs["stop"] = ["<STOP>"]
        try:
            res_str = self._send_request(messages, kwargs)
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
        except Exception as e:
            res_str = '{"error": "Request failed, please try again."}'
        return res_str


class GPT4o(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.llm = OpenAI()
        self.name = "GPT4o"

    def _send_request(self, messages, kwargs):
        res_str = (
            self.llm.chat.completions.create(messages=messages, **kwargs)
            .choices[0]
            .message.content
        )
        res_str = res_str.strip()
        return res_str

    def _get_response(self, messages, one_line, json_mode):
        kwargs = {
            "model": "chatgpt-4o-latest",
            "max_tokens": 4095,
            "temperature": 0,
            "top_p": 0.01,
        }
        if one_line:
            kwargs["stop"] = ["\n"]
        elif json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            res_str = self._send_request(messages, kwargs)
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
        except Exception as e:
            res_str = '{"error": "Request failed, please try again."}'
        return res_str


class Qwen(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.path = os.path.join(
            project_root_path, "chinatravel", "open_source_llm", "Qwen2.5-7B-Instruct"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)
        self.sampling_params = SamplingParams(
            temperature=0, top_p=0.001, max_tokens=4096
        )
        self.llm = LLM(
            model=self.path,
            gpu_memory_utilization=0.95,
        )
        self.name = "Qwen"

    def _get_response(self, messages, one_line, json_mode):
        # print(messages)
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        try:
            res_str = self.llm.generate([text], self.sampling_params)[0].outputs[0].text
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
            elif one_line:
                res_str = res_str.split("\n")[0]
        except Exception as e:
            res_str = '{"error": "Request failed, please try again."}'
        # print("---qwen_output---")
        # print(res_str)
        # print("---qwen_output_end---")
        return res_str


class Mistral(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.path = os.path.join(
            project_root_path,
            "chinatravel",
            "open_source_llm",
            "Mistral-7B-Instruct-v0.3",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)
        self.sampling_params = SamplingParams(
            temperature=0, top_p=0.001, max_tokens=4096
        )
        self.llm = LLM(
            model=self.path,
            gpu_memory_utilization=0.95,
        )
        self.name = "Mistral"

    def _get_response(self, messages, one_line, json_mode):
        messages = merge_repeated_role(messages)
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        try:
            res_str = self.llm.generate([text], self.sampling_params)[0].outputs[0].text
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
            elif one_line:
                res_str = res_str.split("\n")[0]
        except Exception as e:
            res_str = '{"error": "Request failed, please try again."}'
        # print("---mistral_output---")
        # print(res_str)
        # print("---mistral_output_end---")
        return res_str


class Llama(AbstractLLM):
    def __init__(self):
        super().__init__()
        self.path = "/lamda/shaojj/codes/TravelPlanner-main/dev/model/llama-3-chinese-8b-instruct-v3"
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)
        self.sampling_params = SamplingParams(
            temperature=0, top_p=0.001, max_tokens=4096
        )
        self.llm = LLM(model=self.path)
        self.name = "Llama"

    def _get_response(self, messages, one_line, json_mode):
        # print(messages)
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        try:
            res_str = self.llm.generate([text], self.sampling_params)[0].outputs[0].text
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
            elif one_line:
                res_str = res_str.split("\n")[0]
        except Exception as e:
            res_str = '{"error": "Request failed, please try again."}'
        # print("---mistral_output---")
        # print(res_str)
        # print("---mistral_output_end---")
        print(res_str)
        return res_str


if __name__ == "__main__":
    # model = Mistral()
    model = GPT4o()
    print(model([{"role": "user", "content": "hello!"}], one_line=False))
