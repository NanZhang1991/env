# Rerank API 测试套件 - 运行说明

跟 embedding 测试套件是同一套风格：配置驱动(改用例只改yaml，不碰代码)、pytest组织、
警告写入HTML报告。`conftest.py` 和 `pytest.ini` 两个文件**直接复用**embedding套件那两份，
不需要重新写。

## 文件说明

```
your_project/
├── conftest.py               # 复用embedding套件的，通用逻辑，不用改
├── pytest.ini                 # 复用embedding套件的，marker注册+filterwarnings
├── rerank_test_cases.yaml    # rerank专属配置(新增)
└── test_rerank_api.py        # rerank测试代码(新增)
```

## 1. 安装依赖

```bash
pip install pytest requests numpy jsonschema pyyaml pytest-html
```

## 2. 放置文件

四个文件放同一目录，如果这个目录已经有embedding套件的`conftest.py`/`pytest.ini`，直接共用，不用复制第二份。

## 3. 修改配置

打开`rerank_test_cases.yaml`，重点确认这几处（因为rerank接口的字段规范业界不像embedding那样统一，需要你对照实际接口逐条核实）：

| 配置项 | 说明 |
|---|---|
| `models.default` | 实际测试的rerank模型名 |
| `models.max_documents` | 接口支持的最大文档数量上限 |
| `expected_status.*` | 对照接口的真实错误码文档逐项修改 |
| `boundary_cases[].expected_status` / `expected_key` | 每条边界用例期望的状态码，不要假设都是错误（参考embedding套件里vLLM空字符串返回200的例子） |
| `document_object_format_test.object_field_name` | 如果你的接口documents对象格式用的字段名不是`text`（比如`content`），改这里 |
| `document_object_format_test.mixed_format_should_error` | 字符串和对象混用是否该报错，取决于你的接口实现 |

**同时要核对代码本身**——因为rerank接口没有像OpenAI embeddings那样近乎事实标准的规范，`test_rerank_api.py`里的这几处**假设**很可能需要按你的真实接口调整：

- `RESPONSE_SCHEMA`：假设响应字段是`results` / `index` / `relevance_score`，如果你的接口叫`score`而不是`relevance_score`，或者外层不叫`results`，需要改schema和相关断言
- `TestTopN.test_no_top_n_returns_all_documents`：假设不传`top_n`时返回全部文档，如果你的接口有默认截断（比如默认只返回前10条），需要相应调整
- `TestTopN.test_top_n_greater_than_document_count`：假设`top_n`超过文档数时返回全部文档而不报错，如果你的接口对此场景是报错，需要把这条用例迁移到`boundary_cases`里

## 4. 设置接口地址和密钥

```bash
export RERANK_BASE_URL="https://你的接口域名/v1"
export RERANK_API_KEY="你的真实key"
```

## 5. 运行测试

```bash
# 跑全部（不含慢用例）
pytest test_rerank_api.py -v -m "not slow"

# 跑全部（含慢用例，比如文档数上限边界值测试）
pytest test_rerank_api.py -v

# 只跑某一类
pytest test_rerank_api.py -v -k "TopN"
pytest test_rerank_api.py -v -k "ReturnDocuments"
pytest test_rerank_api.py -v -k "MultiDocument"
pytest test_rerank_api.py -v -k "DocumentObjectFormat"

# 生成HTML报告(警告会展示在报告的Links列，跟embedding套件一致)
pytest test_rerank_api.py -v --html=report.html --self-contained-html
```

## 6. 首次验证建议

先只跑最基础的一条，确认连接、鉴权、响应结构假设是否成立：

```bash
pytest test_rerank_api.py -v -k "test_basic_response_structure"
```

如果这条报错，大概率是以下几种情况之一：
- 连接/鉴权问题（跟embedding套件排查方式一样）
- **响应字段名跟假设不一致**（这是rerank测试独有的高发问题，因为没有统一规范）——把你接口的真实响应样例发出来，照着改`RESPONSE_SCHEMA`和相关断言

## 覆盖的六个测试维度

| 测试类 | 覆盖点 |
|---|---|
| `TestBasicRerank` | 基本响应结构、按分数降序排列、语义相关性排序正确性（不只是形式上的单调递减）、延迟、幂等性 |
| `TestTopN` | 合法值截断结果数、超过文档总数时的行为、不传时的默认行为 |
| `TestReturnDocuments` | true/false两种开关下document字段是否存在、返回内容与原文档是否对应（防止index错位） |
| `TestMultiDocument` | 15/30/60条文档规模下的排序完整性（index集合完整、分数降序），可在yaml调整规模档位 |
| `TestDocumentObjectFormat` | 纯字符串数组 vs 对象数组两种格式、两种格式排序结果是否等价、混用格式的行为、对象缺失必需字段时是否报错 |
| `TestBoundaryAndErrorHandling` | 空query、空文档列表、模型不存在、鉴权失败、文档数超限、top_n非法值、单文档超长、文档数恰好等于上限的边界值 |

## 并发测试维度（rerank独有的重点：文档数x并发数矩阵）

rerank是cross-encoder，一次请求内部要对query和每个文档都算一次相关性，
**文档数本身就是隐藏的计算量因子**，跟外部并发数会互相放大压力——
这是跟embedding并发测试最本质的区别，其余维度（防串扰、幂等性、限流韧性、
异步、闭环监控）思路和embedding套件基本一致，只是把client换成了`RerankClient`。

| 测试类 | 覆盖点 | 单独运行 |
|---|---|---|
| `TestConcurrency` | 不同query并发下是否串扰(跟自身基准比对)、同请求并发幂等性 | `-k "TestConcurrency"` |
| `TestDocCountConcurrencyMatrix` | **文档数x并发数矩阵**，找出两个维度叠加时先失效的组合 | `-k DocCountConcurrency` |
| `TestTailLatencyByDocCount` | 按"小文档规模"/"大文档规模"分桶统计P99变异系数，而非笼统一个P99 | `-k TailLatencyByDocCount` |
| `TestRateLimitResilience` | 触发429后按Retry-After退避能否最终成功、限流窗口过后是否立刻恢复 | `-k RateLimitResilience` |
| `TestAsyncConcurrency` | 用asyncio+httpx压更高并发(需装httpx) | `-k AsyncConcurrency` |
| `TestClosedLoopServerMonitoring` | 压测同时抓服务端Prometheus指标(排队长度/GPU显存占用)，rerank是compute-heavy场景，这个关联的诊断价值比embedding更大 | `-k ClosedLoop` |

跑全部并发相关用例：
```bash
pytest test_rerank_api.py -v -k "Concurrency or TailLatency or RateLimitResilience or ClosedLoop"
```

`TestDocCountConcurrencyMatrix`和`TestTailLatencyByDocCount`用的`doc_count_concurrency_matrix`配置在yaml里，
组合数=`len(doc_counts) x len(worker_counts)`，默认3x3=9组合，数值不要设太大，否则跑得会比较久（已标记`slow`）。

`TestClosedLoopServerMonitoring`同embedding套件，需要配置`monitoring.server_metrics_url`才会真正执行，不配置则自动跳过。

## 常见问题排查

| 现象 | 可能原因 |
|---|---|
| `test_basic_response_structure`就失败 | 响应字段名跟`RESPONSE_SCHEMA`假设不符，需要对照真实响应调整 |
| `test_most_relevant_document_ranks_first`失败 | 不一定是bug——如果模型本身排序能力较弱或测试用的样例文档区分度不够，可以换用更有区分度的query/文档组合再测 |
| `test_object_format_documents`报错 | 接口可能不支持对象格式，或字段名不是`text`，改`document_object_format_test.object_field_name` |
| `PytestUnknownMarkWarning` | 确认`pytest.ini`跟测试文件在同一目录，且里面已注册了`slow`这个marker |
| 警告没出现在HTML报告里 | 参考embedding套件README里"把警告写入HTML报告"那一节的排查步骤，机制是通用的 |
