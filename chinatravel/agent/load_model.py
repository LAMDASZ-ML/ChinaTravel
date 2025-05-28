def init_agent(kwargs):
    from .nesy_agent.rule_driven_rec import RuleDrivenAgent
    from .nesy_agent.llm_driven_rec import LLMDrivenAgent
    from .pure_neuro_agent.pure_neuro_agent import ActAgent, ReActAgent
    from .pure_neuro_agent.prompts import (
        ZEROSHOT_ACT_INSTRUCTION,
        ZEROSHOT_REACT_INSTRUCTION,
        ZEROSHOT_REACT_INSTRUCTION_GLM4,
        ONESHOT_REACT_INSTRUCTION,
        ONESHOT_REACT_INSTRUCTION_GLM4,
    )

    from .nesy_verifier import LLMModuloAgent

    from .tpc_agent.tpc_agent import TPCAgent

    if kwargs["method"] == "RuleNeSy":
        agent = RuleDrivenAgent(
            env=kwargs["env"],
            backbone_llm=kwargs["backbone_llm"],
            cache_dir=kwargs["cache_dir"],
            debug=kwargs["debug"],
        )
    elif kwargs["method"] == "LLMNeSy":
        agent = LLMDrivenAgent(
            **kwargs
        )
    elif kwargs["method"] == "Act":
        agent = ActAgent(
            env=kwargs["env"],
            backbone_llm=kwargs["backbone_llm"],
            prompt=ZEROSHOT_ACT_INSTRUCTION,
        )
    elif kwargs["method"] == "ReAct":
        agent = ReActAgent(
            env=kwargs["env"],
            backbone_llm=kwargs["backbone_llm"],
            prompt=(
                ONESHOT_REACT_INSTRUCTION
                if "glm4" not in kwargs["backbone_llm"].name.lower()
                else ONESHOT_REACT_INSTRUCTION_GLM4
            ),
        )
    elif kwargs["method"] == "ReAct0":
        agent = ReActAgent(
            env=kwargs["env"],
            backbone_llm=kwargs["backbone_llm"],
            prompt=(
                ZEROSHOT_REACT_INSTRUCTION
                if "glm4" not in kwargs["backbone_llm"].name.lower()
                else ZEROSHOT_REACT_INSTRUCTION_GLM4
            ),
        )
    elif kwargs["method"] == "LLM-modulo":
        kwargs["model"] = kwargs["backbone_llm"]
        kwargs["max_steps"] = kwargs["refine_steps"]
        agent = LLMModuloAgent(
            **kwargs
        )
    elif kwargs["method"] == "TPCAgent":
        agent = TPCAgent(
            **kwargs
        )
    else:
        raise Exception("Not Implemented")
    return agent


def init_llm(llm_name, max_model_len=None,extend65536=False):
    from .llms import Deepseek, GPT4o, GLM4Plus, Qwen, Mistral, Llama, EmptyLLM

    from .tpc_agent.tpc_llm import TPCLLM

    if llm_name == "deepseek":
        llm = Deepseek()
    elif llm_name == "gpt-4o":
        llm = GPT4o()
    elif llm_name == "glm4-plus":
        llm = GLM4Plus()
    elif "Qwen" in llm_name:
        llm = Qwen(llm_name, max_model_len=max_model_len)
    elif llm_name == "mistral":
        llm = Mistral(max_model_len=max_model_len)
    elif "Llama" in llm_name:
        llm = Llama(llm_name)
    elif llm_name == "rule":
        return EmptyLLM()
    elif llm_name == "TPCLLM":
        llm = TPCLLM()
    else:
        raise Exception("Not Implemented")

    return llm
