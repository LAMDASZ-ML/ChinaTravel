# Travel Planning Challange @ AIC 2025

## 比赛阶段

### 初赛
初赛提供数据集仅供参赛者在前期进行算法验证与调试，选手提交的算法与方案结果不计入最终总分。

### 复赛
复赛提供新的数据集(格式和初赛保持一致), 选手提交的模型由机器进行自动评分，其得分将计入决赛总分。
复赛截止前提交算法运行结果和代码，赛事方验证算法运行结果，机器评分结果将在比赛网站上展示。

### 决赛
决赛代码不可更改，参赛选手完善提交算法技术报告，进行现场答辩。
决赛综合成绩由客观评分和主观评分构成，比例为70%和30%。
 - 客观评分：复赛阶段提交代码在决赛私有数据集上进行评测验证的得分；
 - 主观评分：依据经过标准化处理后的答辩得分。答辩评价将综合考察参赛者的答辩表现，以及所提交的技术方案和代码文档。

## 评估指标

### 环境约束
环境约束评价了输出规划方案中的信息是否与提供的沙盒环境信息一致，度量了规划方案的可行性。
[环境约束说明文档](../chinatravel/symbol_verification/readme.md)


$$EPR-micro = \frac{\sum_{p\in P}\sum_{\in Env} 1_{passed(c,p)}}{|P|*|Env|}$$


$$EPR-macro = \frac{\sum_{p\in P}\prod_{\in Env} 1_{passed(c,p)}}{|P|}$$

### 条件逻辑约束
条件逻辑约束评价了输出规划方案中在满足环境约束的前提下对用户个性化需求的满足程度。

$$C-LPR = \frac{\sum_{p \in P} 1_{passed(Env,p)}\cdot \sum_{c\in C_p} 1_{passed(c,p)}}{\sum_{p \in P}|P|}$$

P是输出的规划方案集合，C_p 是方案 p 对应询问中的约束需求集合，passed(c,p) 表示在p中约束c是否被满足。

### 硬约束通过率
硬约束通过率表达了输出规划方案中满足所有环境约束和逻辑约束的比例。

$$FPR = \frac{\sum_{p \in P} 1_{passed(Env,p)}\cdot \prod_{c\in C_p} 1_{passed(c,p)}}{\sum_{p \in P}|P|}$$

### 偏好评估
TPC 比赛中，我们提供了三个旅行中常见的偏好指标：

每天访问的景点数量尽可能多, Daily Average Attractions Visited, DAV，数值归一化到[0.4]作为分数

$$DAV\text{-}score = (DAV - 0)/4 $$


平均交通时间尽可能少， Averaged Transportation Time, ATT，数值归一到[15,120] (分钟)作为分数

$$ATT\text{-}score = \max(\min((120-ATT)/(120-15),1),0) $$


每天餐饮推荐数量尽可能多, Daily Dining Recommendations, DDR，数值归一到[0,3] 作为分数

$$DDR\text{-}score = \min((DDR - 0)/(3-0),1) $$

### 最终得分

Overall Score = 10% * EPR-micro + 10% * EPR-macro + 25% * C-LPR + 40% * FPR + 5% DAV-Score + 5% ATT-Score + 5% DDR-Score


## 环境配置
请根据ChinaTravel代码库说明进行环境配置
https://github.com/LAMDASZ-ML/ChinaTravel/tree/main


## 数据配置

数据集和数据索引下载：


[![Dataset-Phase1](https://img.shields.io/badge/Dataset-Phase1-yellow)](https://box.nju.edu.cn/d/be342d7958a44fb2ab35/)

请在官网报名注册后获取访问密码


请将数据集解压到`chinatravel/data/`目录下。例如：`chinatravel/data/tpc_aic_phase1/`
将数据索引放到`chinatravel/evaluation/`目录下。例如：`chinatravel/evaluation/tpc_aic_phase1.txt`


## 🛠️ 算法开发

### 1. 智能体算法开发

我们在`chinatravel/agent/tpc_agent/` 提供了独立的算法开发目录，你可以把算法需要的内容都放到这里。


### 2. 语言模型训练适配

支持本地语言模型在旅行规划的适配，你可以在`chinatravel/agent/tpc_agent/tpc_llm.py` 文件中的TPCLLM实例化你的本地模型推理代码。


```python
class TPCLLM(AbstractLLM):
    def __init__(self):
        super().__init__()
        # Initialization logic
        self.name = "TPCLLM"

    def _get_response(self, messages, one_line, json_mode):
        # Implement the response logic of the LLM
        response = "Your LLM response"
        if json_mode:
            # Handle JSON mode
            pass
        elif one_line:
            # Handle one - line mode
            response = response.split("\n")[0]
        return response
```

### 3. 本地算法运行
完成智能体算法开发后，你可以使用实验脚本运行你的代码。


任务1：基于符号验证器的旅行方案修正
测试流程中提供对用户需求的领域特定语言描述和符号验证器，用户在测试时可以通过该验证器对方案进行校验，实时修正方案。


```bash
python run_tpc.py --splits tpc_aic_phase1 --agent TPCAgent --llm TPCLLM --oracle_translation
```

规划结果会保存在：`results/TPCAgent_TPCLLM_oracletranslation` 目录。


任务2：全流程方案生成
测试流程中，用户需要实时理解用户自然语言表达的约束需求，并自动化地给出满足约束需求的旅行方案。

```bash
python run_tpc.py --splits tpc_aic_phase1 --agent TPCAgent --llm TPCLLM
```


### 4. 本地结果获取

本地评估代码在`eval_tpc.py`文件中提供。你可以使用以下命令运行评估代码：

任务1：基于符号验证器的旅行方案修正
```bash
python eval_tpc.py --splits tpc_aic_phase1 --method TPCAgent_TPCLLM_oracle_translation
```

任务2：全流程方案生成
```bash
python eval_tpc.py --splits tpc_aic_phase1 --method TPCAgent_TPCLLM
```

### 5. 代码和结果提交

代码压缩包 XXX_code.zip：请将`chinatravel/agent/tpc_agent/`压缩提交。

（任务1）
结果压缩包 XXX_code.zip：请将`chinatravel/results/TPCAgent_TPCLLM_oracletranslation/`压缩提交。

（任务2）
结果压缩包 XXX_code.zip：请将`chinatravel/results/TPCAgent_TPCLLM/`压缩提交。

### 6. 官方评测 （复赛、决赛）

- 官方验证将在离线设备上进行，该设备配置为：14核Xeon(R) Gold 6348 CPU，100GB RAM，A800-80GB GPU，50GB SSD，驱动程序：550.54.14，CUDA：12.4。
- 算法需要快速响应用户请求，官方评估期间，每个查询将分配5分钟的推理时间，如果超出时间限制，系统将跳至下一个查询。请合理设计你的算法，或使用计时机制在给定的计算资源内完成规划。
- 评估将以离线方式进行，如果你的算法需要使用大型语言模型（LLM），请使用开源模型，例如Qwen3-8B/4B、Llama 3.1-8B等。避免使用外部API，例如DeepSeek API、GPT API等。
- 我们将重复评估五次，取总分的平均值作为最终结果。如果最终结果与用户提交的结果存在显著差异，我们将联系参与者进行确认。无法重现结果的参赛队伍将被取消资格。

