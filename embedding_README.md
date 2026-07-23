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
```

## 2. 放置文件

将 `test_embedding_api_v2.py` 和 `test_cases.yaml` 放在同一目录下。

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

## 7. 切换配置文件（多环境场景）

```bash
export EMBEDDING_TEST_CONFIG="./test_cases_prod.yaml"
pytest test_embedding_api_v2.py -v
```

可以为测试环境、生产环境分别维护一份 `test_cases_*.yaml`，运行时通过该环境变量切换，代码不用改。

## 8. 首次验证建议

先只跑最简单的一条，确认连接和鉴权没问题：

```bash
pytest test_embedding_api_v2.py -v -k "test_basic_response_structure"
```

如果这一条报错（连接失败 / 401 / JSON解析失败），说明 `base_url`、`api_key` 或接口路径不对，先排查这里，再跑全套用例。

## 常见问题排查

| 现象 | 可能原因 |
|---|---|
| `ConnectionError` | `EMBEDDING_BASE_URL` 地址错误或网络不通 |
| 401 | `EMBEDDING_API_KEY` 无效或未设置 |
| `FileNotFoundError: test_cases.yaml` | yaml文件不在同一目录，或未设置 `EMBEDDING_TEST_CONFIG` 指向正确路径 |
| 大量用例状态码不匹配 | `expected_status` 配置的期望值与接口真实行为不符，需对照接口文档修正 |
| `jsonschema.ValidationError` | 接口实际响应字段与预期结构不同，需调整代码中的 `RESPONSE_SCHEMA` |
