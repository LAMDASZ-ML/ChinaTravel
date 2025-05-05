from abc import ABC, abstractmethod
from openai import OpenAI
from json_repair import repair_json
from transformers import AutoTokenizer
from transformers import AutoConfig

# from modelscope import AutoModelForCausalLM, AutoTokenizer

from vllm import LLM, SamplingParams
import re
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
        self.input_token_count = 0
        self.output_token_count = 0
        self.input_token_maxx = 0
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
        self.path = os.path.join(
            project_root_path, "chinatravel", "local_llm", "deepseek_v3_tokenizer"
        )
        self.name = "DeepSeek-V3"

        self.tokenizer = AutoTokenizer.from_pretrained(self.path)

    def _send_request(self, messages, kwargs):

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        input_tokens = self.tokenizer(text)["input_ids"]

        self.input_token_count += len(input_tokens)
        self.input_token_maxx = max(self.input_token_maxx, len(input_tokens))
        
        res_str = (
            self.llm.chat.completions.create(messages=messages, **kwargs)
            .choices[0]
            .message.content
        )
        output_tokens = self.tokenizer(res_str)["input_ids"]
        self.output_token_count += len(output_tokens)
        
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
    def __init__(self, model_name, extend65536=False):
        super().__init__()
        self.path = os.path.join(
            project_root_path, "chinatravel", "local_llm", model_name
        )
        os.environ["VLLM_ALLOW_LONG_MAX_MODEL_LEN"] = "1" 
        if "Qwen3" in model_name:    
            self.sampling_params = SamplingParams(temperature=0.6, top_p=0.95, top_k=20, max_tokens=4096)
            
            config.save_pretrained(self.path)
        else:
            self.sampling_params = SamplingParams(temperature=0, top_p=0.001, max_tokens=4096)

        if extend65536:
            config = AutoConfig.from_pretrained(self.path)
            config.rope_scaling = {
                    "type": "yarn", 
                    "factor": 2.0,  # 原长 32,768 → 扩展到 32,768 * 2 = 65536
                    "original_max_position_embeddings": 32768
                }
            config.save_pretrained(self.path)
            os.environ["VLLM_ALLOW_LONG_MAX_MODEL_LEN"] = "1"
        else:
            config = AutoConfig.from_pretrained(self.path)
            if "rope_scaling" in config.to_dict():
                del config.rope_scaling
            config.save_pretrained(self.path)

        self.tokenizer = AutoTokenizer.from_pretrained(self.path)

        if extend65536:
            self.llm = LLM(
                model=self.path,
                gpu_memory_utilization=0.95,
                max_model_len=65536,  # 强制上下文长度为 65536
                enable_prefix_caching=True,  # 可选：启用前缀缓存优化长文本
            )
        else:
            self.llm = LLM(
                model=self.path,
                gpu_memory_utilization=0.95,
                enable_prefix_caching=True,  # 可选：启用前缀缓存优化长文本
            )
            
        self.name = model_name

        

    def _get_response(self, messages, one_line, json_mode):
        # print(messages)
        
        

        if "Qwen3" in self.name:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True # Switch between thinking and non-thinking modes. Default is True.
            )

            input_tokens = self.tokenizer(text)["input_ids"]
            self.input_token_count += len(input_tokens)       
            self.input_token_maxx = max(self.input_token_maxx, len(input_tokens))
            
            if len(input_tokens) >= 65536:
                return '{"error": "Input prompt is longer than 65536 tokens."}'
            # conduct text completion
            outputs = self.llm.generate([text], self.sampling_params)


            generated_text = outputs[0].outputs[0].text
            # print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
            # print(generated_text)

            output_token_ids = outputs[0].outputs[0].token_ids
            self.output_token_count += len(output_token_ids)

            try:
                m = re.match(r"<think>\n(.+)</think>\n\n", generated_text, flags=re.DOTALL)
                content = generated_text[len(m.group(0)):]
                thinking_content = m.group(1).strip()

            except Exception as e:
                thinking_content = ""
                content = generated_text.strip()
            
            # print("think content: ", thinking_content)
            # print("content: ", content)
            res_str = content
        else:
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            
            input_tokens = self.tokenizer(text)["input_ids"]
            self.input_token_count += len(input_tokens)        
            self.input_token_maxx = max(self.input_token_maxx, len(input_tokens))
            
            if len(input_tokens) >= 65536:
                return '{"error": "Input prompt is longer than 65536 tokens."}'

            outputs = self.llm.generate([text], self.sampling_params)
            res_str = outputs[0].outputs[0].text

            output_token_ids = outputs[0].outputs[0].token_ids
            self.output_token_count += len(output_token_ids)
        try:
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
            elif one_line:
                res_str = res_str.split("\n")[0]
        except Exception as e:
            res_str = '{"error": "Request with specific format failed, please try again."}'
        # print("---qwen_output---")
        # print(res_str)
        # print("---qwen_output_end---")
        return res_str


class Mistral(AbstractLLM):
    def __init__(self, extend65536=False):
        super().__init__()
        self.path = os.path.join(
            project_root_path, "chinatravel", "local_llm", "Mistral-7B-Instruct-v0.3",
        )
        
        if extend65536:
            config = AutoConfig.from_pretrained(self.path)
            config.rope_scaling = {
                    "type": "yarn", 
                    "factor": 2.0,  # 原长 32,768 → 扩展到 32,768 * 2 = 65536
                    "original_max_position_embeddings": 32768
                }
            config.save_pretrained(self.path)
            os.environ["VLLM_ALLOW_LONG_MAX_MODEL_LEN"] = "1"
        else:
            config = AutoConfig.from_pretrained(self.path)
            if "rope_scaling" in config.to_dict():
                del config.rope_scaling
            config.save_pretrained(self.path)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)
        self.sampling_params = SamplingParams(
            temperature=0, top_p=0.001, max_tokens=4096
        )
        
        if extend65536:
            self.llm = LLM(
                model=self.path,
                gpu_memory_utilization=0.95,
                max_model_len=65536,  # 强制上下文长度为 65536
                enable_prefix_caching=True,  # 可选：启用前缀缓存优化长文本
            )
        else:
            self.llm = LLM(
                model=self.path,
                gpu_memory_utilization=0.95,
                enable_prefix_caching=True,  # 可选：启用前缀缓存优化长文本
            )
        self.name = "Mistral-7B-Instruct-v0.3"

    def _get_response(self, messages, one_line, json_mode):
        messages = merge_repeated_role(messages)
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        input_tokens = self.tokenizer(text)["input_ids"]
        self.input_token_count += len(input_tokens)
        self.input_token_maxx = max(self.input_token_maxx, len(input_tokens))

        try:
            # res_str = self.llm.generate([text], self.sampling_params)[0].outputs[0].text
            
            outputs = self.llm.generate([text], self.sampling_params)
            res_str = outputs[0].outputs[0].text
            
            output_token_ids = outputs[0].outputs[0].token_ids
            self.output_token_count += len(output_token_ids)
            
            if json_mode:
                res_str = repair_json(res_str, ensure_ascii=False)
            elif one_line:
                res_str = res_str.split("\n")[0]
        except Exception as e:
            print("error: ", e)
            res_str = '{"error": "Request failed, please try again."}'
        # print("---mistral_output---")
        # print(res_str)
        # print("---mistral_output_end---")
        return res_str


class Llama(AbstractLLM):
    def __init__(self, model_name):
        super().__init__()


        Llama_supported = ["Llama3-3B", "Llama3-8B"]
        if model_name not in Llama_supported:
            raise ValueError(f"Unsupported model name: {model_name}. Supported models: {Llama_supported}")
        
        if model_name == "Llama3-3B":
            self.path = os.path.join(
            project_root_path, "chinatravel", "local_llm", "Llama-3.2-3B-Instruct"
            )
        elif model_name == "Llama3-8B":
            self.path = os.path.join(
            project_root_path, "chinatravel", "local_llm", "Meta-Llama-3.1-8B-Instruct"
            )
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, local_files_only=True)
        self.sampling_params = SamplingParams(
            temperature=0, top_p=0.001, max_tokens=4096
        )
        self.llm = LLM(model=self.path) #, local_files_only=True)
        self.name = model_name

    def _get_response(self, messages, one_line, json_mode):
        # print(messages)
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    
        input_tokens = self.tokenizer(text)["input_ids"]
        self.input_token_count += len(input_tokens)
        self.input_token_maxx = max(self.input_token_maxx, len(input_tokens))
        
        if len(input_tokens) >= 131072:
            return '{"error": "Input prompt is longer than 131072 tokens."}'
        
        
        try:
            outputs = self.llm.generate([text], self.sampling_params)
            res_str = outputs[0].outputs[0].text
            
            output_token_ids = outputs[0].outputs[0].token_ids
            self.output_token_count += len(output_token_ids)

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
