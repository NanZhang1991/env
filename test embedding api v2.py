"""
Embedding API pytest测试套件（配置驱动版）

设计原则：代码里不出现任何具体的测试文本/期望状态码/模型名，
全部从 test_cases.yaml 读取。改测试用例只改yaml，不用碰这个文件。

依赖:
    pip install pytest requests numpy jsonschema pyyaml
    pip install httpx   # 可选，异步并发测试需要，不装的话相关用例会自动跳过

运行:
    pytest test_embedding_api_v2.py -v --html=report.html --self-contained-html
    pytest test_embedding_api_v2.py -v -m "not slow"
    EMBEDDING_TEST_CONFIG=my_cases.yaml pytest test_embedding_api_v2.py   # 切换配置文件
"""

import asyncio
import base64
import json
import os
import struct
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pytest
import requests
import yaml
from jsonschema import validate as jsonschema_validate, ValidationError

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


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

    def test_canary_warning_plumbing(self):
        """金丝雀用例：无条件触发一次warning，跟业务逻辑无关。
        只用于验证 conftest.py 里的html警告收集机制本身是否工作正常。
        确认没问题后可以删掉这条用例。"""
        warnings.warn(
            "这是一条金丝雀警告，用于验证warnings能否正确出现在终端和HTML报告的Warnings区域里",
            UserWarning,
        )
        assert True

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
        threshold = THRESHOLDS["single_latency_ms"]
        assert elapsed_ms < threshold, f"延迟{elapsed_ms:.0f}ms超过阈值{threshold}ms"

        # 软性警告：还没超阈值，但已经逼近了(超过80%)，提前预警性能在恶化
        warn_ratio = 0.8
        if elapsed_ms > threshold * warn_ratio:
            warnings.warn(
                f"延迟{elapsed_ms:.0f}ms已达到阈值{threshold}ms的{elapsed_ms/threshold:.0%}，"
                f"虽未失败但已接近上限，建议关注",
                UserWarning,
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

        # 软性警告：数值一致，但误差已经逼近atol容忍上限(超过50%)，
        # 说明精度余量在收窄，值得留意，不代表当前测试失败
        warn_ratio = 0.5
        if diff.max() > tol["atol"] * warn_ratio:
            warnings.warn(
                f"float/base64最大误差{diff.max():.3e}已达到atol({tol['atol']:.3e})的"
                f"{diff.max()/tol['atol']:.0%}，精度余量正在收窄，建议重新校准阈值",
                UserWarning,
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
        """注意：这条用同一文本并发，只能验证幂等性，
        无法检测服务端把结果错位分发给别的并发请求这类串扰bug——
        因为文本相同，就算真的串了，结果看起来也还是"一致"的。
        真正能检测串扰的是下面的 test_concurrent_distinct_requests_no_crosstalk。"""
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

    @pytest.mark.slow
    def test_concurrent_distinct_requests_no_crosstalk(self, client):
        """每个线程发不同的文本，提前串行算好每条文本的基准向量。
        并发跑完后，把每个线程实际收到的向量跟"它自己那条文本"的基准比对，
        而不是线程之间互相比对——这样如果服务端把响应错位分发给了
        别的并发请求，能够被检测出来(错位后向量对不上对应文本的基准)。"""
        workers = CONFIG["concurrency"]["workers"]
        texts = [f"并发串扰测试文本第{i}条-{'x' * i}" for i in range(workers)]

        # 第一步：低并发(串行)建立基准，作为"标准答案"
        baseline = {}
        for text in texts:
            resp = client.embed(input=text, model=MODEL)
            assert resp.status_code == 200, f"基准建立失败: {resp.text}"
            baseline[text] = np.array(resp.json()["data"][0]["embedding"])

        # 第二步：并发重新请求同一批文本
        def call(text):
            resp = client.embed(input=text, model=MODEL)
            assert resp.status_code == 200
            return text, np.array(resp.json()["data"][0]["embedding"])

        mismatches = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(call, t) for t in texts]
            for f in as_completed(futures):
                text, vec = f.result()
                sim = cosine(baseline[text], vec)
                if sim <= THRESHOLDS["concurrency_min_cosine"]:
                    mismatches.append((text, sim))

        assert not mismatches, (
            f"并发场景下检测到{len(mismatches)}条请求返回的向量与自身文本的基准不匹配，"
            f"疑似响应错位/串扰: {mismatches}"
        )

    @pytest.mark.slow
    def test_concurrent_latency_percentiles(self, client, sample_texts):
        """非纯正确性断言：采集并发压力下的延迟分位数，
        如果P95显著劣化(超过单请求延迟阈值的3倍)，发软性警告而非直接失败，
        因为"并发下变慢多少算合理"跟具体接口的限流/扩容策略有关，
        不该在通用测试里硬编码一个失败阈值。"""
        workers = CONFIG["concurrency"]["workers"]

        def call():
            start = time.time()
            resp = client.embed(input=sample_texts, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200
            return elapsed_ms

        with ThreadPoolExecutor(max_workers=workers) as executor:
            latencies = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        latencies_arr = np.array(latencies)
        p50 = float(np.percentile(latencies_arr, 50))
        p95 = float(np.percentile(latencies_arr, 95))
        p99 = float(np.percentile(latencies_arr, 99))
        print(f"\n[并发延迟分位数] workers={workers} P50={p50:.0f}ms P95={p95:.0f}ms P99={p99:.0f}ms")

        single_threshold = THRESHOLDS["single_latency_ms"]
        if p95 > single_threshold * 3:
            warnings.warn(
                f"并发{workers}路时P95延迟{p95:.0f}ms，是单请求阈值{single_threshold}ms的"
                f"{p95/single_threshold:.1f}倍，性能劣化明显，建议关注",
                UserWarning,
            )


# ============================================================
# 补充场景：变长文本混合并发（检测队头阻塞/长文本饿死短文本）
# ============================================================

class TestVariableLengthConcurrency:

    @pytest.mark.slow
    def test_mixed_length_no_starvation(self, client):
        """短/中/长/超长文本混合并发发出，按长度分组统计各组延迟。
        如果短文本因为排在长文本后面而被迫等更久(队头阻塞)，
        短文本组的延迟会显著劣化，用这个来发现调度不公平的问题。"""
        cfg = CONFIG["concurrency"]["variable_length"]
        n = cfg["requests_per_length"]

        groups = {
            "short": ["测" * cfg["short_chars"]] * n,
            "medium": ["测" * cfg["medium_chars"]] * n,
            "long": ["测" * cfg["long_chars"]] * n,
            "extreme": ["测" * cfg["extreme_chars"]] * n,
        }

        def call(label, text):
            start = time.time()
            resp = client.embed(input=text, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200, f"[{label}] 请求失败: {resp.text[:200]}"
            return label, elapsed_ms

        tasks = [(label, text) for label, texts in groups.items() for text in texts]
        results_by_label = {label: [] for label in groups}

        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = [executor.submit(call, label, text) for label, text in tasks]
            for f in as_completed(futures):
                label, elapsed_ms = f.result()
                results_by_label[label].append(elapsed_ms)

        report = {
            label: {
                "mean_ms": round(float(np.mean(v)), 1),
                "max_ms": round(float(np.max(v)), 1),
            }
            for label, v in results_by_label.items()
        }
        print(f"\n[变长文本混合并发延迟] {report}")

        # 短文本的平均延迟不应该因为混跑了长文本而被拖到跟长文本一个量级，
        # 这里用"短文本均值 vs 长文本均值"的比值做一个软性预警，
        # 具体倍数没有绝对标准，需按你接口的调度策略调整
        short_mean = report["short"]["mean_ms"]
        extreme_mean = report["extreme"]["mean_ms"]
        if extreme_mean > 0 and short_mean > extreme_mean * 0.8:
            warnings.warn(
                f"短文本平均延迟({short_mean}ms)已经接近超长文本平均延迟({extreme_mean}ms)的80%，"
                f"疑似存在队头阻塞，短请求被长请求拖慢，建议关注调度策略",
                UserWarning,
            )


# ============================================================
# 补充场景：长尾延迟深挖（多轮重复，观察P99稳定性）
# ============================================================

class TestTailLatencyDeepDive:

    @pytest.mark.slow
    def test_p99_stability_across_rounds(self, client, sample_texts):
        """多轮重复跑并发请求，记录每轮的P99，
        看P99本身是不是稳定的——如果每轮P99差异很大，
        说明背后可能有间歇性问题(GC/缓存抖动/限流边界效应等)，
        这个信息比单次P99数值本身更有诊断价值。"""
        cfg = CONFIG["concurrency"]["tail_latency"]
        rounds = cfg["rounds"]
        workers = cfg["workers_per_round"]

        def call():
            start = time.time()
            resp = client.embed(input=sample_texts, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200
            return elapsed_ms

        p99_per_round = []
        for round_idx in range(rounds):
            with ThreadPoolExecutor(max_workers=workers) as executor:
                latencies = [
                    f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])
                ]
            p99 = float(np.percentile(latencies, 99))
            p99_per_round.append(p99)

        p99_arr = np.array(p99_per_round)
        mean_p99 = float(np.mean(p99_arr))
        std_p99 = float(np.std(p99_arr))
        cv = std_p99 / mean_p99 if mean_p99 > 0 else 0  # 变异系数：标准差/均值

        print(
            f"\n[P99稳定性] {rounds}轮结果={[round(x, 1) for x in p99_per_round]} "
            f"均值={mean_p99:.1f}ms 标准差={std_p99:.1f}ms 变异系数={cv:.2f}"
        )

        # 变异系数超过0.5，说明P99在轮次间波动剧烈，稳定性存疑，发软性警告
        if cv > 0.5:
            warnings.warn(
                f"P99延迟在{rounds}轮之间波动较大(变异系数={cv:.2f})，"
                f"说明长尾延迟不够稳定，建议排查是否有间歇性瓶颈",
                UserWarning,
            )


# ============================================================
# 补充场景：限流韧性（触发429后能否按退避策略最终成功）
# ============================================================

class TestRateLimitResilience:

    @pytest.mark.slow
    def test_backoff_and_recover_after_429(self, client, sample_texts):
        """先用突发请求触发限流，触发后严格按Retry-After退避重试，
        验证最终能在合理的重试次数/总耗时预算内拿到成功响应——
        而不只是验证"确实触发了429"就完事。"""
        cfg = CONFIG["concurrency"]["rate_limit_resilience"]
        max_attempts = cfg["max_retry_attempts"]
        max_total_wait = cfg["max_total_wait_seconds"]
        burst_count = cfg["burst_count"]

        # 第一步：突发请求触发限流
        triggered = False
        for _ in range(burst_count):
            resp = client.embed(input=sample_texts, model=MODEL)
            if resp.status_code == 429:
                triggered = True
                break
        if not triggered:
            pytest.skip(f"连续{burst_count}次请求未触发限流，跳过退避恢复验证")

        # 第二步：严格按Retry-After退避重试，验证最终能成功
        total_waited = 0.0
        succeeded = False
        for attempt in range(max_attempts):
            retry_after = float(resp.headers.get("Retry-After", 1))
            if total_waited + retry_after > max_total_wait:
                break
            time.sleep(retry_after)
            total_waited += retry_after

            resp = client.embed(input=sample_texts, model=MODEL)
            if resp.status_code == 200:
                succeeded = True
                break
            assert resp.status_code == 429, (
                f"退避重试第{attempt+1}次后返回了非429/200的状态码{resp.status_code}，"
                f"限流状态下不应该出现意料之外的错误"
            )

        assert succeeded, (
            f"按Retry-After退避重试{max_attempts}次(累计等待{total_waited:.1f}s)后仍未成功，"
            f"限流恢复能力不达预期"
        )

    @pytest.mark.slow
    def test_service_recovers_immediately_after_limit_window(self, client, sample_texts):
        """限流窗口过后，服务应该能立刻恢复正常响应，
        而不是过度限流(限流窗口过了还继续拒绝)或者出现雪崩(恢复瞬间大量失败)。"""
        cfg = CONFIG["concurrency"]["rate_limit_resilience"]
        burst_count = cfg["burst_count"]

        resp = None
        for _ in range(burst_count):
            resp = client.embed(input=sample_texts, model=MODEL)
            if resp.status_code == 429:
                break
        if resp is None or resp.status_code != 429:
            pytest.skip(f"连续{burst_count}次请求未触发限流，跳过恢复验证")

        retry_after = float(resp.headers.get("Retry-After", 1))
        time.sleep(retry_after + 0.5)  # 多等0.5秒留余量，避免卡在窗口边界

        resp_after = client.embed(input=sample_texts, model=MODEL)
        assert resp_after.status_code == 200, (
            f"限流窗口({retry_after}s)过后再次请求，期望恢复正常(200)，"
            f"实际返回{resp_after.status_code}，疑似过度限流或恢复延迟"
        )


# ============================================================
# 补充场景：异步并发（asyncio+httpx，客户端开销更小，能压更高并发）
# ============================================================

class TestAsyncConcurrency:

    @pytest.mark.slow
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="需要安装httpx: pip install httpx")
    def test_high_concurrency_via_asyncio(self, sample_texts):
        """用asyncio+httpx发起比线程池更高的并发数。线程并发受OS线程调度和
        GIL切换开销限制，实际测不出服务端的真实并发上限；协程调度开销小得多，
        能更准确地把压力打在服务端而不是耗在客户端自己身上。"""
        workers = CONFIG["concurrency"]["async_workers"]

        async def run():
            async with httpx.AsyncClient(
                base_url=BASE_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                timeout=TIMEOUT,
            ) as ac:

                async def call():
                    start = time.time()
                    resp = await ac.post("/embeddings", json={"input": sample_texts, "model": MODEL})
                    elapsed_ms = (time.time() - start) * 1000
                    return resp.status_code, elapsed_ms

                return await asyncio.gather(*[call() for _ in range(workers)])

        results = asyncio.run(run())
        status_codes = [r[0] for r in results]
        latencies = [r[1] for r in results]

        fail_count = sum(1 for code in status_codes if code != 200)
        assert fail_count == 0, f"{workers}路异步并发中有{fail_count}条请求失败: {status_codes}"

        p95 = float(np.percentile(latencies, 95))
        print(f"\n[异步并发{workers}路] P95={p95:.0f}ms 全部成功")


# ============================================================
# 闭环监控共用工具：本地趋势历史 + Prometheus文本格式指标抓取
# ============================================================

def _history_path() -> Path:
    return Path(CONFIG["concurrency"]["monitoring"]["history_file"])


def _append_history(record: dict):
    with open(_history_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _load_recent_history(window: int) -> List[dict]:
    path = _history_path()
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    return lines[-window:]


def fetch_prometheus_metrics(url: str, metrics_of_interest: List[str]) -> dict:
    """抓取Prometheus文本暴露格式的指标(vLLM等推理框架自带的/metrics端点就是这个格式)，
    只解析我们关心的指标名，同名多个label组合的series取值累加(比如按GPU编号分片的指标)。
    简单正则解析，不引入额外依赖(如prometheus_client)。"""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    result = {name: 0.0 for name in metrics_of_interest}
    found = {name: False for name in metrics_of_interest}

    for line in resp.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 格式: metric_name{label="x"} value  或  metric_name value
        metric_part, _, value_part = line.rpartition(" ")
        if not metric_part:
            continue
        metric_name = metric_part.split("{")[0].strip()
        if metric_name in metrics_of_interest:
            try:
                result[metric_name] += float(value_part)
                found[metric_name] = True
            except ValueError:
                continue

    missing = [name for name, ok in found.items() if not ok]
    if missing:
        warnings.warn(
            f"从{url}抓取指标时，以下指标未找到(可能是版本/框架不同导致指标名不一致，"
            f"需对照实际/metrics输出核对配置): {missing}",
            UserWarning,
        )
    return result


# ============================================================
# 补充场景：闭环监控(轻量版) —— 本地历史趋势对比，非完整监控系统
# ============================================================

class TestPerformanceTrend:

    @pytest.mark.slow
    def test_p95_regression_against_history(self, client, sample_texts):
        """把这次跑的P95延迟记录到本地历史文件，并跟最近N次历史均值对比。
        本质是给pytest加一点"趋势感知"，不是完整监控系统——
        真正需要持续监控告警的话，应该把这里采集到的指标推给
        Prometheus pushgateway或写入CI的历史构建记录，而不是靠本地文件长期攒数据。"""
        cfg = CONFIG["concurrency"]["monitoring"]
        workers = CONFIG["concurrency"]["workers"]

        def call():
            start = time.time()
            resp = client.embed(input=sample_texts, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200
            return elapsed_ms

        with ThreadPoolExecutor(max_workers=workers) as executor:
            latencies = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        p95 = float(np.percentile(latencies, 95))

        history = _load_recent_history(cfg["history_window"])
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "workers": workers,
            "p95_ms": round(p95, 1),
        }

        if history:
            baseline_mean = float(np.mean([h["p95_ms"] for h in history]))
            ratio = p95 / baseline_mean if baseline_mean > 0 else 1.0
            print(
                f"\n[性能趋势] 本次P95={p95:.0f}ms，"
                f"最近{len(history)}次历史均值={baseline_mean:.0f}ms，比值={ratio:.2f}"
            )
            if ratio > cfg["regression_warn_ratio"]:
                warnings.warn(
                    f"本次P95延迟({p95:.0f}ms)是最近{len(history)}次历史均值"
                    f"({baseline_mean:.0f}ms)的{ratio:.2f}倍，超过预警线"
                    f"{cfg['regression_warn_ratio']}，疑似性能退化，建议关注",
                    UserWarning,
                )
        else:
            print(f"\n[性能趋势] 本次P95={p95:.0f}ms，暂无历史记录用于对比(首次运行)")

        _append_history(record)


# ============================================================
# 补充场景：真正的闭环 —— 压测的同时同步采集服务端指标，
# 把客户端观测到的延迟跟服务端真实负载状态关联起来看，
# 而不是只盯客户端这一侧的数字。
# ============================================================

class TestClosedLoopServerMonitoring:

    @pytest.mark.slow
    def test_load_with_server_metrics_correlation(self, client, sample_texts):
        """压测前后分别抓一次服务端/metrics快照，跟客户端本次的P95放在一起看：
        - 排队请求数(num_requests_waiting)在压测后是否清零，没清零说明积压没消化完
        - GPU KV cache占用(gpu_cache_usage_perc)是否接近打满，接近打满是延迟劣化的
          真正原因，而不是网络或客户端的问题
        这才是"闭环"：客户端现象 + 服务端根因，两者对上号。"""
        cfg = CONFIG["concurrency"]["monitoring"]
        metrics_url = cfg.get("server_metrics_url", "")
        if not metrics_url:
            pytest.skip("未配置 monitoring.server_metrics_url，跳过服务端指标关联采集")

        metrics_of_interest = cfg["server_metrics_of_interest"]
        workers = CONFIG["concurrency"]["workers"]

        # 压测前快照
        before = fetch_prometheus_metrics(metrics_url, metrics_of_interest)

        def call():
            start = time.time()
            resp = client.embed(input=sample_texts, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200
            return elapsed_ms

        with ThreadPoolExecutor(max_workers=workers) as executor:
            latencies = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        # 压测后快照(留一点时间让服务端指标刷新到最新一次采集周期)
        time.sleep(1)
        after = fetch_prometheus_metrics(metrics_url, metrics_of_interest)

        p95 = float(np.percentile(latencies, 95))
        delta = {name: round(after[name] - before[name], 3) for name in metrics_of_interest}

        print(
            f"\n[闭环压测报告] workers={workers} 客户端P95={p95:.0f}ms\n"
            f"  服务端指标(压测前 -> 压测后, 变化量): "
            + ", ".join(f"{name}: {before[name]:.2f} -> {after[name]:.2f} (Δ{delta[name]:+.2f})"
                        for name in metrics_of_interest)
        )

        # 记录到同一份历史文件，客户端+服务端指标一起沉淀，方便后续做趋势对比
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "workers": workers,
            "p95_ms": round(p95, 1),
            "server_metrics_before": before,
            "server_metrics_after": after,
        }
        _append_history(record)

        # 排队积压未消化：压测结束后等待队列仍大于阈值，说明服务端没能及时消化掉这波压力
        waiting_key = "vllm:num_requests_waiting"
        if waiting_key in after and after[waiting_key] > cfg["queue_saturation_warn_threshold"]:
            warnings.warn(
                f"压测结束后服务端等待队列({waiting_key})仍为{after[waiting_key]}，"
                f"超过阈值{cfg['queue_saturation_warn_threshold']}，积压未消化，"
                f"说明当前workers={workers}的压力已经超过服务端实时处理能力",
                UserWarning,
            )

        # GPU显存/KV cache紧张：这通常是延迟劣化的真正根因
        gpu_cache_key = "vllm:gpu_cache_usage_perc"
        if gpu_cache_key in after and after[gpu_cache_key] > cfg["gpu_cache_warn_ratio"]:
            warnings.warn(
                f"压测期间GPU KV cache占用({gpu_cache_key})达到{after[gpu_cache_key]:.1%}，"
                f"超过预警线{cfg['gpu_cache_warn_ratio']:.0%}，显存接近打满，"
                f"这很可能是客户端观测到延迟升高/请求被拒绝的真正根因",
                UserWarning,
            )

    @pytest.mark.slow
    def test_server_metrics_endpoint_reachable(self):
        """最基础的前置检查：服务端指标端点是否可达、格式是否可解析。
        如果这条都失败，上面那条关联测试的数据就不可信，需要先排查这里。"""
        cfg = CONFIG["concurrency"]["monitoring"]
        metrics_url = cfg.get("server_metrics_url", "")
        if not metrics_url:
            pytest.skip("未配置 monitoring.server_metrics_url")

        resp = requests.get(metrics_url, timeout=10)
        assert resp.status_code == 200, f"服务端指标端点不可达: {resp.status_code}"
        assert resp.text.strip(), "服务端指标端点返回了空内容"
