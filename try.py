from vllm import LLM, SamplingParams

model_path = "/home/shjj/文档/codes/ChinaTravel/opensource-v0/ChinaTravel/chinatravel/local_llm/Qwen3-8B"
sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
llm = LLM(model=model_path)
prompts = ["Hello, my name is"]
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
