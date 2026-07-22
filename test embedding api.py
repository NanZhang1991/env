"""
Embedding API pytest测试套件

依赖:
    pip install pytest requests numpy jsonschema pytest-html

运行:
    pytest test_embedding_api.py -v --html=report.html --self-contained-html
    pytest test_embedding_api.py -v -k "batch"          # 只跑批量相关用例
    pytest test_embedding_api.py -v -m "not slow"        # 跳过慢用例(并发/限流)

配置:
    通过环境变量或直接修改 conftest 区域的 BASE_URL / API_KEY / MODEL 等常量。
    不同厂商的错误码行为不同，EXPECTED_* 常量需要对照你要测的接口的官方文档调整，
    不要直接当作行业标准照搬。
"""

import base64
import os
import struct
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Union

import numpy as np
import pytest
import requests
from jsonschema import validate as jsonschema_validate, ValidationError


# ============================================================
# 配置区（按你实际接口调整）
# ============================================================

BASE_URL = os.environ.get("EMBEDDING_BASE_URL", "https://api.example.com/v1")
API_KEY = os.environ.get("EMBEDDING_API_KEY", "YOUR_API_KEY")
MODEL = os.environ.get("EMBEDDING_MODEL", "your-model-name")
MODEL_LARGE = os.environ.get("EMBEDDING_MODEL_LARGE", "your-model-large")  # 用于dimensions测试
NATIVE_DIM = int(os.environ.get("EMBEDDING_NATIVE_DIM", "1536"))
MAX_BATCH_SIZE = int(os.environ.get("EMBEDDING_MAX_BATCH", "2048"))
COMPARE_MODELS = [MODEL, MODEL_LARGE]

# 期望的错误码——务必对照你要测接口的官方文档修改，这里只是常见惯例的默认值
EXPECTED = {
    "empty_input": 400,
    "model_not_found": 404,
    "auth_failed": 401,
    "text_too_long": 400,
    "batch_over_limit": 400,
    "invalid_dimensions": 400,
    "invalid_encoding_format": 400,
}

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["data", "model"],
    "properties": {
        "data": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["embedding", "index"],
                "properties": {
                    "embedding": {"type": ["array", "string"]},  # array=float, string=base64
                    "index": {"type": "integer"},
                },
            },
        },
        "model": {"type": "string"},
        "usage": {"type": "object"},
    },
}


# ============================================================
# 客户端
# ============================================================

class EmbeddingClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self, api_key: Optional[str] = None) -> dict:
        key = api_key if api_key is not None else self.api_key
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def embed(
        self,
        input: Union[str, List[str]],
        model: str,
        dimensions: Optional[int] = None,
        encoding_format: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> requests.Response:
        payload = {"input": input, "model": model}
        if dimensions is not None:
            payload["dimensions"] = dimensions
        if encoding_format is not None:
            payload["encoding_format"] = encoding_format
        return requests.post(
            f"{self.base_url}/embeddings",
            json=payload,
            headers=self._headers(api_key),
            timeout=self.timeout,
        )


def decode_base64_to_floats(b64_str: str) -> np.ndarray:
    raw = base64.b64decode(b64_str)
    assert len(raw) % 4 == 0, "字节长度不是4的倍数，可能不是float32编码"
    count = len(raw) // 4
    return np.array(struct.unpack(f"<{count}f", raw))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def client() -> EmbeddingClient:
    return EmbeddingClient(base_url=BASE_URL, api_key=API_KEY)


@pytest.fixture(scope="session")
def sample_texts() -> List[str]:
    return ["苹果很好吃", "今天天气不错", "北京是中国的首都"]


# ============================================================
# 任务1：单文本嵌入
# ============================================================

class TestSingleEmbedding:

    def test_basic_response_structure(self, client):
        resp = client.embed(input="你好，世界", model=MODEL)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        try:
            jsonschema_validate(instance=body, schema=RESPONSE_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"响应结构不符合schema: {e.message}")

        assert len(body["data"]) == 1
        assert body["data"][0]["index"] == 0
        assert len(body["data"][0]["embedding"]) > 0

    def test_latency_within_threshold(self, client, threshold_ms=2000):
        start = time.time()
        resp = client.embed(input="延迟测试文本", model=MODEL)
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < threshold_ms, f"延迟{elapsed_ms:.0f}ms超过阈值{threshold_ms}ms"

    def test_whitespace_only_input(self, client):
        """纯空白字符输入的边界情况"""
        resp = client.embed(input="   ", model=MODEL)
        # 行为因厂商而异：有的当作有效文本处理，有的报400。这里只校验不是500
        assert resp.status_code != 500, f"空白输入不应导致服务端500: {resp.text}"

    @pytest.mark.parametrize("text", [
        "Hello world 你好世界",          # 中英混合
        "こんにちは world 안녕하세요",     # 中日韩英混合
        "🎉 emoji test 测试 🚀",         # emoji+文本
    ])
    def test_multilingual_mixed_input(self, client, text):
        resp = client.embed(input=text, model=MODEL)
        assert resp.status_code == 200, f"多语言混合输入失败: {text} -> {resp.text}"
        vec = resp.json()["data"][0]["embedding"]
        assert len(vec) > 0

    def test_idempotency(self, client):
        """同一文本调用两次，向量应完全一致（或余弦相似度≈1）"""
        text = "幂等性测试文本"
        resp1 = client.embed(input=text, model=MODEL)
        resp2 = client.embed(input=text, model=MODEL)
        assert resp1.status_code == 200 and resp2.status_code == 200

        vec1 = np.array(resp1.json()["data"][0]["embedding"])
        vec2 = np.array(resp2.json()["data"][0]["embedding"])
        sim = cosine(vec1, vec2)
        assert sim > 0.9999, f"同一文本两次调用相似度仅{sim}，模型可能非确定性"


# ============================================================
# 任务2：批量嵌入
# ============================================================

class TestBatchEmbedding:

    def test_count_and_index_alignment(self, client, sample_texts):
        resp = client.embed(input=sample_texts, model=MODEL)
        assert resp.status_code == 200, resp.text
        results = resp.json()["data"]
        assert len(results) == len(sample_texts)

        results_sorted = sorted(results, key=lambda x: x["index"])
        indices = [r["index"] for r in results_sorted]
        assert indices == list(range(len(sample_texts))), "index未能覆盖0..N-1"

    def test_dimension_consistency_within_batch(self, client, sample_texts):
        resp = client.embed(input=sample_texts, model=MODEL)
        dims = {len(d["embedding"]) for d in resp.json()["data"]}
        assert len(dims) == 1, f"同批次维度不一致: {dims}"

    def test_batch_over_limit_returns_error(self, client):
        texts = [f"文本{i}" for i in range(MAX_BATCH_SIZE + 1)]
        resp = client.embed(input=texts, model=MODEL)
        assert resp.status_code == EXPECTED["batch_over_limit"], (
            f"超批量上限应返回{EXPECTED['batch_over_limit']}，实际{resp.status_code}"
        )

    def test_batch_result_matches_individual_calls(self, client):
        """批量结果与逐条单独调用结果应一致（验证批处理内部没有互相干扰/截断错位）"""
        texts = ["独立文本A", "独立文本B", "独立文本C"]
        batch_resp = client.embed(input=texts, model=MODEL)
        assert batch_resp.status_code == 200
        batch_vecs = {
            d["index"]: np.array(d["embedding"]) for d in batch_resp.json()["data"]
        }

        for i, text in enumerate(texts):
            single_resp = client.embed(input=text, model=MODEL)
            assert single_resp.status_code == 200
            single_vec = np.array(single_resp.json()["data"][0]["embedding"])
            sim = cosine(batch_vecs[i], single_vec)
            assert sim > 0.999, f"文本[{text}]批量与单独调用结果差异过大 (相似度={sim})"


# ============================================================
# 任务3：多模型对比
# ============================================================

class TestMultiModelComparison:

    @pytest.mark.parametrize("model", COMPARE_MODELS)
    def test_each_model_returns_valid_vectors(self, client, sample_texts, model):
        resp = client.embed(input=sample_texts, model=model)
        assert resp.status_code == 200, f"[{model}] 请求失败: {resp.text}"
        data = resp.json()["data"]
        assert len(data) == len(sample_texts)

    def test_latency_comparison_report(self, client, sample_texts):
        """非断言性，仅采集各模型延迟做对比报告（打印到测试日志）"""
        report = {}
        for model in COMPARE_MODELS:
            start = time.time()
            resp = client.embed(input=sample_texts, model=model)
            elapsed_ms = (time.time() - start) * 1000
            if resp.status_code == 200:
                report[model] = round(elapsed_ms, 2)
        print(f"\n多模型延迟对比(ms): {report}")
        assert len(report) > 0, "没有任何模型请求成功"


# ============================================================
# 任务4：dimensions参数
# ============================================================

class TestDimensionsParam:

    @pytest.mark.parametrize("target_dim", [64, 256, 512])
    def test_valid_truncated_dimensions(self, client, target_dim):
        resp = client.embed(input="维度裁剪测试", model=MODEL_LARGE, dimensions=target_dim)
        assert resp.status_code == 200, resp.text
        vec = resp.json()["data"][0]["embedding"]
        assert len(vec) == target_dim

    def test_dimensions_over_native_rejected(self, client):
        resp = client.embed(input="超限维度测试", model=MODEL_LARGE, dimensions=NATIVE_DIM + 1000)
        assert resp.status_code == EXPECTED["invalid_dimensions"], (
            f"超原生维度应返回{EXPECTED['invalid_dimensions']}，实际{resp.status_code}"
        )

    def test_dimensions_zero_or_negative_rejected(self, client):
        resp = client.embed(input="非法维度测试", model=MODEL_LARGE, dimensions=0)
        assert resp.status_code == EXPECTED["invalid_dimensions"]


# ============================================================
# 任务5：encoding_format (float / base64)
# ============================================================

class TestEncodingFormat:

    def test_float_and_base64_numerically_consistent(self, client):
        text = "编码格式一致性测试"
        resp_float = client.embed(input=text, model=MODEL, encoding_format="float")
        resp_b64 = client.embed(input=text, model=MODEL, encoding_format="base64")
        assert resp_float.status_code == 200 and resp_b64.status_code == 200

        vec_float = np.array(resp_float.json()["data"][0]["embedding"])
        raw_field = resp_b64.json()["data"][0]["embedding"]
        assert isinstance(raw_field, str), "base64格式应返回字符串"
        vec_b64 = decode_base64_to_floats(raw_field)

        assert vec_float.shape == vec_b64.shape
        assert np.allclose(vec_float, vec_b64, atol=1e-5), "float与base64解码后数值不一致"

    def test_invalid_encoding_format_rejected(self, client):
        resp = client.embed(input="非法格式测试", model=MODEL, encoding_format="xml")
        assert resp.status_code == EXPECTED["invalid_encoding_format"]

    def test_default_format_when_unspecified(self, client):
        """不传encoding_format时应有明确默认值（通常是float）"""
        resp = client.embed(input="默认格式测试", model=MODEL)
        assert resp.status_code == 200
        vec = resp.json()["data"][0]["embedding"]
        assert isinstance(vec, list), "默认格式期望是float数组，如果你的接口默认base64需调整此断言"


# ============================================================
# 任务6：错误码透传
# ============================================================

class TestErrorPassthrough:

    @pytest.mark.parametrize("case_name,expected_status,make_request", [
        ("空字符串输入", "empty_input", lambda c: c.embed(input="", model=MODEL)),
        ("空数组输入", "empty_input", lambda c: c.embed(input=[], model=MODEL)),
        ("模型不存在", "model_not_found", lambda c: c.embed(input="测试", model="not-a-real-model-xyz")),
        ("鉴权失败", "auth_failed", lambda c: c.embed(input="测试", model=MODEL, api_key="invalid-key-000")),
        ("超长文本", "text_too_long", lambda c: c.embed(input="测试" * 100000, model=MODEL)),
    ])
    def test_error_cases(self, client, case_name, expected_status, make_request):
        resp = make_request(client)
        expected_code = EXPECTED[expected_status]
        assert resp.status_code == expected_code, (
            f"[{case_name}] 期望{expected_code}，实际{resp.status_code}: {resp.text[:200]}"
        )
        # 4xx错误不应被包装成裸500，应保留结构化错误体
        try:
            body = resp.json()
            assert "error" in body or "code" in body, f"[{case_name}] 错误体缺少结构化字段: {body}"
        except ValueError:
            pytest.fail(f"[{case_name}] 错误响应不是合法JSON: {resp.text[:200]}")

    def test_4xx_errors_should_not_retry_indicator(self, client):
        """4xx类错误不应带Retry-After（这是5xx/429的语义），若带了说明网关语义搞混了"""
        resp = client.embed(input="测试", model=MODEL, api_key="invalid-key-000")
        assert resp.status_code == 401
        assert "Retry-After" not in resp.headers, "401错误不应包含Retry-After头"

    @pytest.mark.slow
    def test_rate_limit_returns_429_with_retry_after(self, client, burst_count=100):
        """高频连续请求触发限流，验证429及Retry-After头"""
        triggered = False
        for _ in range(burst_count):
            resp = client.embed(input="限流测试", model=MODEL)
            if resp.status_code == 429:
                triggered = True
                assert "Retry-After" in resp.headers, "429响应应带Retry-After头以指导客户端退避"
                break
        if not triggered:
            pytest.skip(f"连续{burst_count}次请求未触发限流，可能限流阈值更高，非失败")


# ============================================================
# 补充场景：并发一致性
# ============================================================

class TestConcurrency:

    @pytest.mark.slow
    def test_concurrent_requests_index_alignment(self, client, sample_texts, workers=10):
        """高并发下多次批量请求，验证每次响应内部index仍然正确对齐，不会串批"""

        def call():
            resp = client.embed(input=sample_texts, model=MODEL)
            assert resp.status_code == 200
            data = sorted(resp.json()["data"], key=lambda x: x["index"])
            return [d["index"] for d in data]

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(call) for _ in range(workers)]
            for f in as_completed(futures):
                indices = f.result()
                assert indices == list(range(len(sample_texts))), f"并发场景下index错位: {indices}"

    @pytest.mark.slow
    def test_concurrent_single_requests_consistency(self, client, workers=10):
        """并发对同一文本发多次单条请求，结果应两两高度相似（验证无线程间数据串扰）"""
        text = "并发一致性测试文本"

        def call():
            resp = client.embed(input=text, model=MODEL)
            assert resp.status_code == 200
            return np.array(resp.json()["data"][0]["embedding"])

        with ThreadPoolExecutor(max_workers=workers) as executor:
            vecs = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        base = vecs[0]
        for v in vecs[1:]:
            assert cosine(base, v) > 0.9999, "并发请求同一文本返回的向量不一致，疑似串扰"


# ============================================================
# pytest配置：标记slow用例（默认跑全部，可用 -m "not slow" 跳过）
# ============================================================

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 耗时较长的用例(并发/限流探测)")
