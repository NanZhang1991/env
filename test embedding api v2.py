"""
Embedding API pytest测试套件（配置驱动版）

设计原则：代码里不出现任何具体的测试文本/期望状态码/模型名，
全部从 test_cases.yaml 读取。改测试用例只改yaml，不用碰这个文件。

依赖:
    pip install pytest requests numpy jsonschema pyyaml

运行:
    pytest test_embedding_api_v2.py -v --html=report.html --self-contained-html
    pytest test_embedding_api_v2.py -v -m "not slow"
    EMBEDDING_TEST_CONFIG=my_cases.yaml pytest test_embedding_api_v2.py   # 切换配置文件
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
import yaml
from jsonschema import validate as jsonschema_validate, ValidationError


CONFIG_PATH = os.environ.get(
    "EMBEDDING_TEST_CONFIG",
    os.path.join(os.path.dirname(__file__), "test_cases.yaml"),
)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()

BASE_URL = os.environ.get(CONFIG["connection"]["base_url_env"], "https://api.example.com/v1")
API_KEY = os.environ.get(CONFIG["connection"]["api_key_env"], "YOUR_API_KEY")
TIMEOUT = CONFIG["connection"]["timeout_seconds"]

MODEL = CONFIG["models"]["default"]
MODEL_LARGE = CONFIG["models"]["large"]
COMPARE_MODELS = CONFIG["models"]["compare_group"]
NATIVE_DIM = CONFIG["models"]["native_dim"]
MAX_BATCH_SIZE = CONFIG["models"]["max_batch_size"]

EXPECTED = CONFIG["expected_status"]
THRESHOLDS = CONFIG["thresholds"]
ENCODING_TEST_CFG = CONFIG["encoding_format_test"]


def get_numeric_tolerance(model: str) -> dict:
    """按模型名查找是否有独立的atol/rtol覆盖(不同模型可能跑在不同硬件/精度上)，
    没有则回退到默认值。"""
    for override in ENCODING_TEST_CFG.get("overrides", []):
        if override.get("model") == model:
            return {
                "atol": float(override.get("atol", ENCODING_TEST_CFG["atol"])),
                "rtol": float(override.get("rtol", ENCODING_TEST_CFG["rtol"])),
            }
    return {
        "atol": float(ENCODING_TEST_CFG["atol"]),
        "rtol": float(ENCODING_TEST_CFG["rtol"]),
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
                    "embedding": {"type": ["array", "string"]},
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
    return np.array(struct.unpack(f"<{len(raw)//4}f", raw))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def resolve_input(case: dict):
    """从boundary_cases配置项还原出实际input值，支持字符串/数组/repeat语法"""
    if "input_repeat" in case:
        text, times = case["input_repeat"]
        return text * times
    return case["input"]


def resolve_expected_status(case: dict) -> int:
    """用例可以直接写expected_status(具体数字)，也可以用expected_key引用字典"""
    if "expected_status" in case:
        return int(case["expected_status"])
    return EXPECTED[case["expected_key"]]


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def client() -> EmbeddingClient:
    return EmbeddingClient(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)


@pytest.fixture(scope="session")
def sample_texts() -> List[str]:
    return CONFIG["sample_texts"]["batch_default"]


# ============================================================
# 动态参数化：从yaml生成pytest用例，而不是写死在装饰器里
# ============================================================

def pytest_generate_tests(metafunc):
    if "boundary_case" in metafunc.fixturenames:
        cases = CONFIG["boundary_cases"]
        metafunc.parametrize(
            "boundary_case",
            cases,
            ids=[c["name"] for c in cases],
        )

    if "multilingual_case" in metafunc.fixturenames:
        cases = CONFIG["sample_texts"]["multilingual"]
        metafunc.parametrize(
            "multilingual_case",
            cases,
            ids=[c["label"] for c in cases],
        )

    if "valid_dim" in metafunc.fixturenames:
        metafunc.parametrize("valid_dim", CONFIG["dimensions_test"]["valid_targets"])

    if "invalid_dim" in metafunc.fixturenames:
        metafunc.parametrize("invalid_dim", CONFIG["dimensions_test"]["invalid_values"])

    if "compare_model" in metafunc.fixturenames:
        metafunc.parametrize("compare_model", COMPARE_MODELS)


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

    def test_latency_within_threshold(self, client):
        start = time.time()
        resp = client.embed(input="延迟测试文本", model=MODEL)
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < THRESHOLDS["single_latency_ms"], (
            f"延迟{elapsed_ms:.0f}ms超过阈值{THRESHOLDS['single_latency_ms']}ms"
        )

    def test_multilingual_mixed_input(self, client, multilingual_case):
        resp = client.embed(input=multilingual_case["text"], model=MODEL)
        assert resp.status_code == 200, (
            f"[{multilingual_case['label']}] 失败: {resp.text}"
        )
        assert len(resp.json()["data"][0]["embedding"]) > 0

    def test_idempotency(self, client):
        text = "幂等性测试文本"
        vec1 = np.array(client.embed(input=text, model=MODEL).json()["data"][0]["embedding"])
        vec2 = np.array(client.embed(input=text, model=MODEL).json()["data"][0]["embedding"])
        sim = cosine(vec1, vec2)
        assert sim > THRESHOLDS["idempotency_min_cosine"], f"相似度仅{sim}"


# ============================================================
# 任务2：批量嵌入
# ============================================================

class TestBatchEmbedding:

    def test_count_and_index_alignment(self, client, sample_texts):
        resp = client.embed(input=sample_texts, model=MODEL)
        assert resp.status_code == 200, resp.text
        results_sorted = sorted(resp.json()["data"], key=lambda x: x["index"])
        indices = [r["index"] for r in results_sorted]
        assert indices == list(range(len(sample_texts)))

    def test_batch_over_limit_returns_error(self, client):
        texts = [f"文本{i}" for i in range(MAX_BATCH_SIZE + 1)]
        resp = client.embed(input=texts, model=MODEL)
        assert resp.status_code == EXPECTED["batch_over_limit"]

    def test_batch_result_matches_individual_calls(self, client, sample_texts):
        batch_resp = client.embed(input=sample_texts, model=MODEL)
        batch_vecs = {
            d["index"]: np.array(d["embedding"]) for d in batch_resp.json()["data"]
        }
        for i, text in enumerate(sample_texts):
            single_vec = np.array(
                client.embed(input=text, model=MODEL).json()["data"][0]["embedding"]
            )
            sim = cosine(batch_vecs[i], single_vec)
            assert sim > THRESHOLDS["batch_vs_single_min_cosine"], (
                f"文本[{text}]批量与单独调用差异过大 (相似度={sim})"
            )


# ============================================================
# 任务3：多模型对比
# ============================================================

class TestMultiModelComparison:

    def test_each_model_returns_valid_vectors(self, client, sample_texts, compare_model):
        resp = client.embed(input=sample_texts, model=compare_model)
        assert resp.status_code == 200, f"[{compare_model}] 失败: {resp.text}"
        assert len(resp.json()["data"]) == len(sample_texts)


# ============================================================
# 任务4：dimensions参数
# ============================================================

class TestDimensionsParam:

    def test_valid_truncated_dimensions(self, client, valid_dim):
        resp = client.embed(input="维度裁剪测试", model=MODEL_LARGE, dimensions=valid_dim)
        assert resp.status_code == 200, resp.text
        assert len(resp.json()["data"][0]["embedding"]) == valid_dim

    def test_dimensions_over_native_rejected(self, client):
        offset = CONFIG["dimensions_test"]["over_native_offset"]
        resp = client.embed(input="超限维度测试", model=MODEL_LARGE, dimensions=NATIVE_DIM + offset)
        assert resp.status_code == EXPECTED["invalid_dimensions"]

    def test_invalid_dimension_values_rejected(self, client, invalid_dim):
        resp = client.embed(input="非法维度测试", model=MODEL_LARGE, dimensions=invalid_dim)
        assert resp.status_code == EXPECTED["invalid_dimensions"]


# ============================================================
# 任务5：encoding_format
# ============================================================

class TestEncodingFormat:

    def test_float_and_base64_numerically_consistent(self, client):
        text = "编码格式一致性测试"
        resp_float = client.embed(input=text, model=MODEL, encoding_format="float")
        resp_b64 = client.embed(input=text, model=MODEL, encoding_format="base64")
        assert resp_float.status_code == 200 and resp_b64.status_code == 200

        vec_float = np.array(resp_float.json()["data"][0]["embedding"])
        vec_b64 = decode_base64_to_floats(resp_b64.json()["data"][0]["embedding"])

        tol = get_numeric_tolerance(MODEL)
        diff = np.abs(vec_float - vec_b64)
        is_close = np.allclose(vec_float, vec_b64, atol=tol["atol"], rtol=tol["rtol"])
        assert is_close, (
            f"float与base64数值不一致 (dtype={ENCODING_TEST_CFG['numeric_dtype']}, "
            f"atol={tol['atol']}, rtol={tol['rtol']}) -> "
            f"max_diff={diff.max():.3e}, mean_diff={diff.mean():.3e}, "
            f"p99_diff={np.percentile(diff, 99):.3e}"
        )

    def test_invalid_encoding_format_rejected(self, client):
        resp = client.embed(input="非法格式测试", model=MODEL, encoding_format="xml")
        assert resp.status_code == EXPECTED["invalid_encoding_format"]

    @pytest.mark.calibration
    def test_measure_real_numeric_noise(self, client, sample_texts):
        """诊断用例，不做断言。多条文本反复测float/base64误差，
        打印出真实的max/mean/p99差异，用于回填yaml里的atol/rtol，
        而不是凭感觉设置阈值。默认不随主套件运行：
            pytest test_embedding_api_v2.py -v -m calibration
        """
        all_diffs = []
        for text in sample_texts:
            resp_float = client.embed(input=text, model=MODEL, encoding_format="float")
            resp_b64 = client.embed(input=text, model=MODEL, encoding_format="base64")
            if resp_float.status_code != 200 or resp_b64.status_code != 200:
                continue
            vf = np.array(resp_float.json()["data"][0]["embedding"])
            vb = decode_base64_to_floats(resp_b64.json()["data"][0]["embedding"])
            all_diffs.append(np.abs(vf - vb))

        assert all_diffs, "没有任何成功的请求，无法采集误差数据"
        diffs = np.concatenate(all_diffs)
        print(
            f"\n[误差校准结果] dtype={ENCODING_TEST_CFG['numeric_dtype']} "
            f"样本数={len(diffs)} "
            f"max={diffs.max():.3e} mean={diffs.mean():.3e} "
            f"p99={np.percentile(diffs, 99):.3e} p999={np.percentile(diffs, 99.9):.3e}\n"
            f"建议：atol 设为 max_diff 的 5~10 倍留余量，回填到 test_cases.yaml "
            f"的 encoding_format_test.atol"
        )


# ============================================================
# 任务6：错误码透传（用例完全来自yaml的 error_cases）
# ============================================================

class TestBoundaryAndErrorHandling:
    """测试各类边界/异常输入。不假设都会报错——同一种边界输入在不同实现下
    可能是合法的(如vLLM把空字符串当合法输入返回200)，也可能是非法的。
    按每条用例实际期望的状态码，分别走成功响应校验或错误响应校验。"""

    def test_boundary_cases(self, client, boundary_case):
        kwargs = {
            "input": resolve_input(boundary_case),
            "model": boundary_case.get("model_override", MODEL),
        }
        if "api_key_override" in boundary_case:
            kwargs["api_key"] = boundary_case["api_key_override"]

        resp = client.embed(**kwargs)
        expected_code = resolve_expected_status(boundary_case)
        name = boundary_case["name"]

        assert resp.status_code == expected_code, (
            f"[{name}] 期望状态码{expected_code}，实际{resp.status_code}: {resp.text[:200]}"
        )

        if expected_code < 400:
            # 期望是合法请求：应返回符合标准schema的成功响应
            try:
                body = resp.json()
            except ValueError:
                pytest.fail(f"[{name}] 期望成功响应，但响应体不是合法JSON: {resp.text[:200]}")
            try:
                jsonschema_validate(instance=body, schema=RESPONSE_SCHEMA)
            except ValidationError as e:
                pytest.fail(f"[{name}] 成功响应不符合schema: {e.message}")
        else:
            # 期望是错误响应：应返回结构化错误体，而不是被网关包装成裸500或空body
            try:
                body = resp.json()
            except ValueError:
                pytest.fail(f"[{name}] 错误响应不是合法JSON: {resp.text[:200]}")
            assert "error" in body or "code" in body, (
                f"[{name}] 错误体缺少结构化字段(error/code): {body}"
            )

    @pytest.mark.slow
    def test_rate_limit_returns_429_with_retry_after(self, client):
        burst_count = CONFIG["concurrency"]["rate_limit_burst_count"]
        for _ in range(burst_count):
            resp = client.embed(input="限流测试", model=MODEL)
            if resp.status_code == 429:
                assert "Retry-After" in resp.headers
                return
        pytest.skip(f"连续{burst_count}次请求未触发限流")


# ============================================================
# 补充场景：并发一致性
# ============================================================

class TestConcurrency:

    @pytest.mark.slow
    def test_concurrent_requests_index_alignment(self, client, sample_texts):
        workers = CONFIG["concurrency"]["workers"]

        def call():
            resp = client.embed(input=sample_texts, model=MODEL)
            data = sorted(resp.json()["data"], key=lambda x: x["index"])
            return [d["index"] for d in data]

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(call) for _ in range(workers)]
            for f in as_completed(futures):
                assert f.result() == list(range(len(sample_texts)))

    @pytest.mark.slow
    def test_concurrent_single_requests_consistency(self, client):
        workers = CONFIG["concurrency"]["workers"]
        text = "并发一致性测试文本"

        def call():
            resp = client.embed(input=text, model=MODEL)
            return np.array(resp.json()["data"][0]["embedding"])

        with ThreadPoolExecutor(max_workers=workers) as executor:
            vecs = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        base = vecs[0]
        for v in vecs[1:]:
            assert cosine(base, v) > THRESHOLDS["concurrency_min_cosine"]


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: 耗时较长的用例(并发/限流探测)")
    config.addinivalue_line("markers", "calibration: 阈值校准用诊断用例，不随主套件默认运行")
