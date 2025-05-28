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
 - 客观评分：复赛阶段提交代码在私有数据集上进行评测验证的得分；
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
$P$ 是输出的规划方案集合，$C_p$是方案p对应询问中的约束需求集合，$passed(c,p)$表示在p中约束c是否被满足。

### 硬约束通过率
硬约束通过率表达了输出规划方案中满足所有环境约束和逻辑约束的比例。
$$FPR = \frac{\sum_{p \in P} 1_{passed(Env,p)}\cdot \prod_{c\in C_p} 1_{passed(c,p)}}{\sum_{p \in P}|P|}$$

### 偏好评估
TPC 比赛中，我们提供了三个旅行中常见的偏好指标：

每天访问的景点数量尽可能多, Daily Average Attractions Visited, DAV，数值归一化到[0.4]作为分数
$$DAV\text{-}score = (DAV - 0)/4 $$


平均交通时间尽可能多, Averaged Transportation Time, ATT，数值归一到[15,120] (分钟)作为分数
$$ATT\text{-}score = \max(\min((120-ATT)/(120-15),1),0) $$


每天餐饮推荐数量尽可能多, Daily Dining Recommendations, DDR，数值归一到[0,3] 作为分数
$$DDR\text{-}score = \min((DDR - 0)/(3-0),1) $$

### 最终得分

Overall Score = 10% * EPR-micro + 10% * EPR-macro + 25% * C-LPR + 40% * FPR + 5% DAV-Score + 5% ATT-Score + 5% DDR-Score