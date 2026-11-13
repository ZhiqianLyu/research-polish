# 改前改后示例

下面的例句都是虚构的，覆盖机器学习、材料、生物、机器人、网络等领域，按问题类型分组。
每组给出改前、改后和理由。它们模仿的是真实修改中最常见的写法，可以直接当作判断标准。

## 1. 迂回立论

| 改前 | 改后 | 理由 |
|---|---|---|
| The improvement lies not in a larger model but in the cleaner labels. | The improvement comes from the cleaner labels; both models have the same size. | 直接说来源，再补一个对照事实 |
| This calibration step, not the sensor itself, makes the readings comparable across labs. | This calibration step makes the readings comparable across labs. | 前文已说明传感器本身做不到 |
| The assay shows that the protein binds the receptor, not that it activates the pathway. | The assay shows that the protein binds the receptor; pathway activation is tested in Section 4. | 肯定句加指路，信息不丢 |
| What is proved holds for the simulator, not for the physical robot. | What is proved holds for the simulator, and carrying it over to the physical robot requires a hardware test. | 顺势引出下一步工作 |

## 2. 只防质疑的句子（删）

| 改前 | 处理 | 理由 |
|---|---|---|
| This study did not evaluate the model on languages other than English. | 删（若审稿要求多语言，再写成适用范围） | 没人问，删掉不影响论证 |
| This comparison is suggestive, not conclusive: the two datasets differ in size… | The two datasets differ in size, so the comparison is normalised per sample. | 保留事实，去掉自我贬低 |
| Deployment on embedded hardware is left as a future milestone and is not claimed here. | 删 | 前文已说明只在工作站上运行 |
| An early version of the pipeline was tried and abandoned. With the same budget… | With the same budget, a pipeline without the cache reached 61% accuracy. | 去掉过程叙述，保留对比结果 |

## 3. 被要求写的限制：保留内容，换说法

| 改前 | 改后 |
|---|---|
| Long-term degradation was not observed. | Observing long-term degradation needs cycling tests beyond 500 hours. |
| The check does not cover the thermal model, the scheduler or the network stack. | The thermal model, the scheduler and the network stack lie outside the check. |
| …this work adds the online check but lacks real patient data. | …this work adds the online check, and the earlier study retains the advantage of real patient data. |

## 4. 结论里的自我否定

| 改前 | 改后 |
|---|---|
| The framework supports safer deployment by making its test evidence reproducible; this work does not measure an improvement in safety. | The framework supports safer deployment by making its test evidence reproducible. With the safety monitor every run stayed within its limits, against 7 of 40 without it. |

后半句原本是想避免标题说过头。但如果已经有"有无监测器"的对比数据，直接给出实测结果，
结论就不会否定标题，也没有夸大。

## 5. 过程叙述 → 能力陈述

| 改前 | 改后 |
|---|---|
| In this phase, a random forest is selected as the core classifier. | The pipeline is built on a random forest, selected for its stable feature rankings. |
| This stage of research yields two principal contributions. First, the dataset was constructed… | This section produces two artefacts. The dataset is assembled from… |
| In preliminary runs, the solver failed to converge on the coarse mesh. | On the coarse mesh the solver does not converge, so all results use the refined mesh. |
| 表题 "Phased research pipeline"：Data → Model → Evaluation | "Stages of the pipeline and what each produces"：labelled dataset; trained model; benchmark scores |

## 6. 通读性

| 改前 | 改后 | 问题 |
|---|---|---|
| Medical imaging systems demand extreme rigor, because an erroneous diagnosis can yield irreversible, catastrophic consequences. | Medical imaging systems must be accurate: a missed lesion can delay treatment by months. | 堆砌形容词，换成具体后果 |
| Consequently, any malformed packet is dropped at the gateway. | Any malformed packet is therefore dropped at the gateway. | 句首连接词 |
| A test result of FAIL indicates that the checker identified a counterexample, providing direct evidence that the corresponding state is reachable within the model. | A FAIL result means the checker found a counterexample, which shows directly that the state is reachable. | 两个 that，冗长 |
| …4 of those failures and 7 of the 9 recoveries occurred after…（一句 48 词，三个分号） | 拆成三句：先报阈值以上全部恢复，再报总数，最后报时间分布 | 超长句 |
| This dependence introduces stochastic error. | Where the clocks drift apart, timestamps vary between runs. | 因果不通：依赖本身不产生误差 |

## 7. 说过头（去保留语之后最常见的错误）

| 有问题的改写 | 为什么错 | 正确写法 |
|---|---|---|
| The detector found every anomaly. | 图里另一组测试漏检了一个 | The detector found all 48 anomalies in the main test set, each above the 3σ threshold. |
| …and no run diverged. | 附录里另一组实验发散了 | 只用正文已有的结果："the 12 runs started from unstable states all settled within 3 s" |
| The classifier flags a sample when that sample's score crosses the threshold. | 数据显示中位分数低于阈值的组，检出率仍然过半，靠的是噪声 | In the groups with median scores of 0.6 and 0.8, 25% and 40% of samples exceed the threshold, yet 55% and 72% are flagged. |
