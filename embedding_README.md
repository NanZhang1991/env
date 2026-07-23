# Embedding API 测试套件 - 运行说明

## 文件说明

```
your_project/
├── test_embedding_api_v2.py   # 测试代码
└── test_cases.yaml            # 测试用例配置（改用例只改这个文件）
```

## 1. 安装依赖

```bash
pip install pytest requests numpy jsonschema pyyaml pytest-html
pip install httpx   # 可选，异步并发测试需要，不装的话相关用例会自动跳过
```

## 2. 放置文件

将 `test_embedding_api_v2.py`、`test_cases.yaml`、`conftest.py` 放在同一目录下。

`conftest.py` 的作用：把测试用例中通过 `warnings.warn(...)` 产生的软性警告
（断言通过但有需要关注的情况，比如延迟接近阈值、精度误差接近容忍上限）
自动附加到HTML报告里对应那一行的 "Warnings" 展开区域，而不是只在终端末尾
打印一堆和具体用例对不上号的warnings摘要。

## 3. 修改配置

打开 `test_cases.yaml`，将以下内容替换为真实值：

| 配置项 | 说明 |
|---|---|
| `models.default` / `models.large` / `models.compare_group` | 实际测试的模型名 |
| `models.native_dim` | 模型的真实原生向量维度 |
| `models.max_batch_size` | 接口支持的最大批量条数 |
| `expected_status.*` | 对照接口的真实错误码文档逐项修改 |
| `boundary_cases[].expected_status` | 每条边界用例期望的状态码，**不要假设都是错误**。比如vLLM把空字符串当合法输入返回200，只有空数组才400，需按你实际接口的行为逐条确认 |

> `expected_status` 里的默认值是按OpenAI风格惯例填写的，**不是通用标准**，必须对照你实际接口的文档确认。

## 4. 设置接口地址和密钥

不要写进代码或配置文件，用环境变量传入。

**macOS / Linux:**
```bash
export EMBEDDING_BASE_URL="https://你的接口域名/v1"
export EMBEDDING_API_KEY="你的真实key"
```

**Windows PowerShell:**
```powershell
$env:EMBEDDING_BASE_URL="https://你的接口域名/v1"
$env:EMBEDDING_API_KEY="你的真实key"
```

## 5. 运行测试

```bash
# 跑全部（不含并发/限流等慢用例）
pytest test_embedding_api_v2.py -v -m "not slow"

# 跑全部（含慢用例）
pytest test_embedding_api_v2.py -v

# 只跑某一类，例如批量相关
pytest test_embedding_api_v2.py -v -k "Batch"

# 只跑某个具体用例
pytest test_embedding_api_v2.py -v -k "test_idempotency"

# 生成 HTML 报告
pytest test_embedding_api_v2.py -v --html=report.html --self-contained-html
```

## 6. encoding_format数值容忍度（atol/rtol）配置

不同模型的底层推理精度（float16 / bfloat16 / float32 / float64）和硬件（NVIDIA / Ascend / TPU等）不同，
`float`与`base64`一致性校验的容忍阈值不该写死，已放在 `test_cases.yaml` 的 `encoding_format_test` 下：

```yaml
encoding_format_test:
  numeric_dtype: float32
  atol: 1.0e-6
  rtol: 1.0e-5
  overrides:              # 可选：不同模型单独设置阈值
    - model: your-model-on-ascend-fp16
      numeric_dtype: float16
      atol: 1.0e-2
      rtol: 1.0e-2
```

**不要凭感觉设置这两个值。** 先跑校准用例，摸清真实误差水平再回填：

```bash
pytest test_embedding_api_v2.py -v -m calibration
```

它会打印类似输出：
```
[误差校准结果] dtype=float32 样本数=4608 max=8.2e-07 mean=1.1e-07 p99=4.5e-07 p999=6.9e-07
建议：atol 设为 max_diff 的 5~10 倍留余量，回填到 test_cases.yaml 的 encoding_format_test.atol
```
按提示把`atol`回填到yaml里即可。

> 注意：主套件默认运行不会自动跑校准用例，也不会自动排除它——如果不加`-m`筛选直接跑`pytest test_embedding_api_v2.py -v`，
> 校准用例会作为一条普通用例混在结果里（它不会失败，只是多打印一段诊断信息）。
> 想跑"纯业务断言、不含慢用例和校准用例"的主套件，用：
> ```bash
> pytest test_embedding_api_v2.py -v -m "not slow and not calibration"
> ```

## 7. 把警告写入HTML报告

已经内置了两处"软性警告"示例（断言通过、但接近临界值时提醒）：

- `TestSingleEmbedding.test_latency_within_threshold`：延迟超过阈值的80%时警告
- `TestEncodingFormat.test_float_and_base64_numerically_consistent`：数值误差超过atol的50%时警告

跑测试并生成报告：

```bash
pytest test_embedding_api_v2.py -v --html=report.html --self-contained-html
```

打开`report.html`后，对应用例那一行虽然是绿色PASSED，但会多一个可展开的
**Warnings**区块，点开能看到具体警告内容（比如"延迟已达阈值的85%"）。

**给自己的代码加软性警告**，只需要在测试函数里：

```python
import warnings

def test_something(self, client):
    ...
    if 某个非致命但值得关注的情况:
        warnings.warn("说明具体情况", UserWarning)
```

不需要额外配置，`conftest.py`里的钩子会自动捕获并挂到对应用例的报告行上。

> 依赖`conftest.py`和`pytest-html`配合工作，确保两个文件在同一目录、`pytest-html`已安装。

## 8. 切换配置文件（多环境场景）

```bash
export EMBEDDING_TEST_CONFIG="./test_cases_prod.yaml"
pytest test_embedding_api_v2.py -v
```

可以为测试环境、生产环境分别维护一份 `test_cases_*.yaml`，运行时通过该环境变量切换，代码不用改。

## 9. 首次验证建议

先只跑最简单的一条，确认连接和鉴权没问题：

```bash
pytest test_embedding_api_v2.py -v -k "test_basic_response_structure"
```

如果这一条报错（连接失败 / 401 / JSON解析失败），说明 `base_url`、`api_key` 或接口路径不对，先排查这里，再跑全套用例。

## 10. 进阶并发测试维度

| 测试类 | 验证什么 | 单独运行 |
|---|---|---|
| `TestVariableLengthConcurrency` | 长文本是否让短文本被迫排队变慢(队头阻塞) | `-k VariableLength` |
| `TestTailLatencyDeepDive` | P99延迟在多轮之间是否稳定，而非只看单次数值 | `-k TailLatency` |
| `TestRateLimitResilience` | 触发429后按Retry-After退避能否最终成功、限流窗口过后是否立刻恢复 | `-k RateLimitResilience` |
| `TestAsyncConcurrency` | 用asyncio+httpx压更高并发，排除线程调度开销干扰测试结果(需装httpx) | `-k AsyncConcurrency` |
| `TestPerformanceTrend` | 本次P95跟本地历史记录均值对比，发现趋势性劣化(仅客户端视角) | `-k PerformanceTrend` |
| `TestClosedLoopServerMonitoring` | 压测同时抓服务端Prometheus指标(排队长度/GPU显存占用)，把客户端延迟跟服务端根因对上号 | `-k ClosedLoop` |

`TestClosedLoopServerMonitoring`需要在`test_cases.yaml`里配置`monitoring.server_metrics_url`（比如vLLM服务自带的`http://<地址>:<端口>/metrics`），不配置的话这两条用例会自动`skip`，不影响其他测试。不同推理框架/版本的指标名不一样，`server_metrics_of_interest`列表要对照你实际`/metrics`端点返回的内容核对，名字不对的话会在跑测试时警告"未找到"。

跑全部进阶并发用例：
```bash
pytest test_embedding_api_v2.py -v -k "Concurrency or TailLatency or RateLimitResilience or PerformanceTrend or ClosedLoop"
```

`TestPerformanceTrend`会在当前目录生成`.embedding_perf_history.jsonl`持续累积历史记录，这是轻量级趋势对比，**不是**完整监控系统。需要长期持续监控告警的话，建议把这里采集到的指标（P95/P99/错误率）接入你现有的Prometheus/Grafana，而不是让这份文件无限增长下去。

## 常见问题排查

| 现象 | 可能原因 |
|---|---|
| `ConnectionError` | `EMBEDDING_BASE_URL` 地址错误或网络不通 |
| 401 | `EMBEDDING_API_KEY` 无效或未设置 |
| `FileNotFoundError: test_cases.yaml` | yaml文件不在同一目录，或未设置 `EMBEDDING_TEST_CONFIG` 指向正确路径 |
| 大量用例状态码不匹配 | `expected_status` 配置的期望值与接口真实行为不符，需对照接口文档修正 |
| `jsonschema.ValidationError` | 接口实际响应字段与预期结构不同，需调整代码中的 `RESPONSE_SCHEMA` |
