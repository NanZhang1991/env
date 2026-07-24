"""
Rerank API pytest测试套件（配置驱动版，风格与 test_embedding_api_v2.py 一致）

设计原则：代码里不出现任何具体的测试文本/期望状态码/模型名，
全部从 rerank_test_cases.yaml 读取。改测试用例只改yaml，不用碰这个文件。

依赖:
    pip install pytest requests numpy jsonschema pyyaml pytest-html

配套文件(与embedding套件共用，无需修改)：
    conftest.py   —— 警告收集/HTML报告展示，通用逻辑，不针对embedding
    pytest.ini    —— marker注册、filterwarnings配置

运行:
    pytest test_rerank_api.py -v --html=report.html --self-contained-html
    pytest test_rerank_api.py -v -m "not slow"
    RERANK_TEST_CONFIG=my_cases.yaml pytest test_rerank_api.py   # 切换配置文件

假设的接口结构(如果你的接口字段名不同，需要调整 RerankClient 和 RESPONSE_SCHEMA)：
    请求: {"model": ..., "query": ..., "documents": [...], "top_n": ..., "return_documents": ...}
    响应: {"results": [{"index": int, "relevance_score": float, "document": {...}}], "model": ...}
"""

import asyncio
import json
import os
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
    "RERANK_TEST_CONFIG",
    os.path.join(os.path.dirname(__file__), "rerank_test_cases.yaml"),
)


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()

BASE_URL = os.environ.get(CONFIG["connection"]["base_url_env"], "https://api.example.com/v1")
API_KEY = os.environ.get(CONFIG["connection"]["api_key_env"], "YOUR_API_KEY")
TIMEOUT = CONFIG["connection"]["timeout_seconds"]

MODEL = CONFIG["models"]["default"]
MAX_DOCUMENTS = CONFIG["models"]["max_documents"]

EXPECTED = CONFIG["expected_status"]
THRESHOLDS = CONFIG["thresholds"]

SAMPLE_QUERY = CONFIG["sample_query"]
SAMPLE_DOCUMENTS = CONFIG["sample_documents"]

OBJECT_FIELD_NAME = CONFIG["document_object_format_test"]["object_field_name"]

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["results"],
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["index", "relevance_score"],
                "properties": {
                    "index": {"type": "integer"},
                    "relevance_score": {"type": "number"},
                },
            },
        },
        "model": {"type": "string"},
    },
}


# ============================================================
# 客户端
# ============================================================

class RerankClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self, api_key: Optional[str] = None) -> dict:
        key = api_key if api_key is not None else self.api_key
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def rerank(
        self,
        query: str,
        documents: List[Union[str, dict]],
        model: str,
        top_n: Optional[int] = None,
        return_documents: Optional[bool] = None,
        api_key: Optional[str] = None,
    ) -> requests.Response:
        payload = {"model": model, "query": query, "documents": documents}
        if top_n is not None:
            payload["top_n"] = top_n
        if return_documents is not None:
            payload["return_documents"] = return_documents
        return requests.post(
            f"{self.base_url}/rerank",
            json=payload,
            headers=self._headers(api_key),
            timeout=self.timeout,
        )


def resolve_query(case: dict) -> str:
    if case.get("use_sample_query"):
        return SAMPLE_QUERY
    return case.get("query", "")


def resolve_documents(case: dict) -> list:
    if "documents_repeat" in case:
        text, times = case["documents_repeat"]
        return [text] * times
    if "documents_repeat_long" in case:
        text, times = case["documents_repeat_long"]
        return [text * times]
    if case.get("use_sample_documents"):
        return SAMPLE_DOCUMENTS
    return case.get("documents", SAMPLE_DOCUMENTS)


def resolve_expected_status(case: dict) -> int:
    if "expected_status" in case:
        return int(case["expected_status"])
    return EXPECTED[case["expected_key"]]


def generate_documents(count: int) -> List[str]:
    template = CONFIG["multi_document_test"]["text_template"]
    return [template.format(i=i) for i in range(count)]


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="session")
def client() -> RerankClient:
    return RerankClient(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)


def pytest_generate_tests(metafunc):
    if "boundary_case" in metafunc.fixturenames:
        cases = CONFIG["boundary_cases"]
        metafunc.parametrize("boundary_case", cases, ids=[c["name"] for c in cases])

    if "valid_top_n" in metafunc.fixturenames:
        metafunc.parametrize("valid_top_n", CONFIG["top_n_test"]["valid_values"])

    if "doc_count" in metafunc.fixturenames:
        metafunc.parametrize("doc_count", CONFIG["multi_document_test"]["document_counts"])


# ============================================================
# 任务1：基本重排
# ============================================================

class TestBasicRerank:

    def test_basic_response_structure(self, client):
        resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        try:
            jsonschema_validate(instance=body, schema=RESPONSE_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"响应结构不符合schema: {e.message}")

        results = body["results"]
        assert len(results) > 0, "重排结果不能为空"

        indices = [r["index"] for r in results]
        assert len(set(indices)) == len(indices), f"index出现重复: {indices}"
        assert all(0 <= i < len(SAMPLE_DOCUMENTS) for i in indices), f"index超出文档范围: {indices}"

    def test_results_sorted_by_score_descending(self, client):
        resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp.status_code == 200, resp.text
        scores = [r["relevance_score"] for r in resp.json()["results"]]
        assert scores == sorted(scores, reverse=True), (
            f"结果未按relevance_score降序排列: {scores}"
        )

    def test_most_relevant_document_ranks_first(self, client):
        """构造一条跟query明显强相关的文档放在最后位置，验证重排后被排到第一，
        而不只是简单校验分数单调递减(那个即使模型没有真正理解语义也能造出来)。"""
        distractors = ["苹果是一种水果", "今天天气晴朗", "北京是中国的首都"]
        relevant_doc = "向量检索利用embedding计算相似度进行语义匹配"
        documents = distractors + [relevant_doc]  # 相关文档故意放最后一位(index=3)

        resp = client.rerank(query="什么是向量检索", documents=documents, model=MODEL)
        assert resp.status_code == 200, resp.text
        results = resp.json()["results"]
        top_index = results[0]["index"]
        assert top_index == len(documents) - 1, (
            f"期望语义最相关的文档(index={len(documents)-1})排第一，实际排第一的是index={top_index}，"
            f"重排效果可能有问题"
        )

    def test_latency_within_threshold(self, client):
        start = time.time()
        resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        threshold = THRESHOLDS["single_latency_ms"]
        assert elapsed_ms < threshold, f"延迟{elapsed_ms:.0f}ms超过阈值{threshold}ms"

        if elapsed_ms > threshold * 0.8:
            warnings.warn(
                f"延迟{elapsed_ms:.0f}ms已达到阈值{threshold}ms的{elapsed_ms/threshold:.0%}，建议关注",
                UserWarning,
            )

    def test_idempotency(self, client):
        """同一query+documents调用两次，每个index对应的relevance_score应该基本一致"""
        resp1 = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        resp2 = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp1.status_code == 200 and resp2.status_code == 200

        scores1 = {r["index"]: r["relevance_score"] for r in resp1.json()["results"]}
        scores2 = {r["index"]: r["relevance_score"] for r in resp2.json()["results"]}

        max_diff_allowed = THRESHOLDS["idempotency_max_score_diff"]
        for idx in scores1:
            if idx not in scores2:
                continue
            diff = abs(scores1[idx] - scores2[idx])
            assert diff <= max_diff_allowed, (
                f"index={idx}两次调用score差异{diff}超过容忍值{max_diff_allowed}"
            )


# ============================================================
# 任务2：top_n 参数
# ============================================================

class TestTopN:

    def test_valid_top_n_limits_result_count(self, client, valid_top_n):
        resp = client.rerank(
            query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL, top_n=valid_top_n
        )
        assert resp.status_code == 200, resp.text
        results = resp.json()["results"]
        assert len(results) == valid_top_n, (
            f"top_n={valid_top_n}，期望返回{valid_top_n}条，实际{len(results)}条"
        )

    def test_top_n_greater_than_document_count(self, client):
        """top_n超过文档总数时，期望的通常行为是返回全部文档(不报错)，
        而不是报错或截断成负数——如果你的接口在这种情况下报错，
        需要把这条改成走boundary_cases那种错误校验路径。"""
        offset = CONFIG["top_n_test"]["over_document_count_offset"]
        big_top_n = len(SAMPLE_DOCUMENTS) + offset

        resp = client.rerank(
            query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL, top_n=big_top_n
        )
        assert resp.status_code == 200, (
            f"top_n({big_top_n})超过文档数({len(SAMPLE_DOCUMENTS)})时返回了{resp.status_code}，"
            f"如果你的接口对此场景应该报错，请把这条用例迁移到boundary_cases里配置"
        )
        results = resp.json()["results"]
        assert len(results) == len(SAMPLE_DOCUMENTS), (
            f"top_n超过文档数时，期望返回全部{len(SAMPLE_DOCUMENTS)}条，实际{len(results)}条"
        )

    def test_no_top_n_returns_all_documents(self, client):
        """不传top_n时的默认行为：期望返回全部文档的重排结果。
        如果你的接口有不同的默认截断行为(比如默认只返回前10条)，
        需要相应调整这条断言。"""
        resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == len(SAMPLE_DOCUMENTS), (
            f"未传top_n时，期望返回全部{len(SAMPLE_DOCUMENTS)}条，实际{len(results)}条，"
            f"说明接口有默认截断行为，需要在测试里显式记录这个默认值"
        )


# ============================================================
# 任务3：return_documents 开关
# ============================================================

class TestReturnDocuments:

    def test_return_documents_true_includes_content(self, client):
        resp = client.rerank(
            query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL, return_documents=True
        )
        assert resp.status_code == 200, resp.text
        results = resp.json()["results"]
        for r in results:
            assert "document" in r and r["document"], (
                f"return_documents=True时，结果里应包含document字段: {r}"
            )

    def test_return_documents_false_excludes_content(self, client):
        resp = client.rerank(
            query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL, return_documents=False
        )
        assert resp.status_code == 200, resp.text
        results = resp.json()["results"]
        for r in results:
            assert not r.get("document"), (
                f"return_documents=False时，结果里不应包含document内容，实际: {r}"
            )

    def test_return_documents_content_matches_original(self, client):
        """return_documents=True时，返回的document内容应该跟原始输入对应，
        而不只是校验字段存在——要验证index和document的对应关系是对的。"""
        resp = client.rerank(
            query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL, return_documents=True
        )
        assert resp.status_code == 200
        for r in resp.json()["results"]:
            original_text = SAMPLE_DOCUMENTS[r["index"]]
            returned = r["document"]
            returned_text = returned.get(OBJECT_FIELD_NAME) if isinstance(returned, dict) else returned
            assert returned_text == original_text, (
                f"index={r['index']}返回的document内容({returned_text!r})"
                f"与原始文档({original_text!r})不一致，疑似index错位"
            )


# ============================================================
# 任务4：多文档（>10）
# ============================================================

class TestMultiDocument:

    def test_large_document_set_ranking_integrity(self, client, doc_count):
        documents = generate_documents(doc_count)
        start = time.time()
        resp = client.rerank(query=SAMPLE_QUERY, documents=documents, model=MODEL)
        elapsed_ms = (time.time() - start) * 1000

        assert resp.status_code == 200, f"文档数={doc_count}时请求失败: {resp.text[:200]}"
        results = resp.json()["results"]

        assert len(results) == doc_count, (
            f"文档数={doc_count}，期望返回{doc_count}条结果，实际{len(results)}条"
        )
        indices = [r["index"] for r in results]
        assert set(indices) == set(range(doc_count)), (
            f"文档数={doc_count}时index集合不完整/有重复"
        )
        scores = [r["relevance_score"] for r in results]
        assert scores == sorted(scores, reverse=True), (
            f"文档数={doc_count}时结果未按分数降序排列"
        )

        print(f"\n[多文档规模测试] doc_count={doc_count} 延迟={elapsed_ms:.0f}ms")


# ============================================================
# 任务5：文档对象格式
# ============================================================

class TestDocumentObjectFormat:

    def test_plain_string_documents(self, client):
        resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp.status_code == 200, f"纯字符串数组格式失败: {resp.text[:200]}"

    def test_object_format_documents(self, client):
        object_documents = [{OBJECT_FIELD_NAME: text} for text in SAMPLE_DOCUMENTS]
        resp = client.rerank(query=SAMPLE_QUERY, documents=object_documents, model=MODEL)
        assert resp.status_code == 200, (
            f"对象格式(字段名={OBJECT_FIELD_NAME})documents请求失败: {resp.text[:200]}，"
            f"如果你的接口不支持对象格式，或字段名不是'{OBJECT_FIELD_NAME}'，需要调整配置"
        )
        results = resp.json()["results"]
        indices = [r["index"] for r in results]
        assert set(indices) == set(range(len(object_documents)))

    def test_string_and_object_results_equivalent(self, client):
        """同样的内容分别用纯字符串格式和对象格式请求，排序结果应该一致，
        证明两种格式在服务端被解析成了相同的语义。"""
        string_resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        object_documents = [{OBJECT_FIELD_NAME: text} for text in SAMPLE_DOCUMENTS]
        object_resp = client.rerank(query=SAMPLE_QUERY, documents=object_documents, model=MODEL)

        assert string_resp.status_code == 200 and object_resp.status_code == 200

        string_order = [r["index"] for r in string_resp.json()["results"]]
        object_order = [r["index"] for r in object_resp.json()["results"]]
        assert string_order == object_order, (
            f"字符串格式排序{string_order}与对象格式排序{object_order}不一致，"
            f"两种documents格式在服务端解析结果应该等价"
        )

    def test_mixed_format_documents(self, client):
        """字符串和对象混用在同一个documents数组里。
        期望行为由配置里的mixed_format_should_error决定：
        有的接口会报错拒绝，有的接口会尽量兼容解析——按你实际接口行为配置。"""
        should_error = CONFIG["document_object_format_test"]["mixed_format_should_error"]
        mixed_documents = [
            SAMPLE_DOCUMENTS[0],
            {OBJECT_FIELD_NAME: SAMPLE_DOCUMENTS[1]},
        ]
        resp = client.rerank(query=SAMPLE_QUERY, documents=mixed_documents, model=MODEL)

        if should_error:
            assert resp.status_code >= 400, (
                f"配置期望混用格式应报错，实际返回{resp.status_code}"
            )
        else:
            assert resp.status_code == 200, (
                f"配置期望混用格式应被兼容处理，实际返回{resp.status_code}: {resp.text[:200]}"
            )

    def test_object_missing_required_field_rejected(self, client):
        """对象格式缺少必需字段(如text)时应该报错，而不是静默处理成空内容。"""
        broken_documents = [{"wrong_field_name": SAMPLE_DOCUMENTS[0]}]
        resp = client.rerank(query=SAMPLE_QUERY, documents=broken_documents, model=MODEL)
        assert resp.status_code == EXPECTED["invalid_document_format"], (
            f"对象格式缺少必需字段时，期望{EXPECTED['invalid_document_format']}，"
            f"实际{resp.status_code}: {resp.text[:200]}"
        )


# ============================================================
# 任务6：错误码透传（边界用例，config驱动）
# ============================================================

class TestBoundaryAndErrorHandling:
    """跟embedding套件同样的设计：不假设所有边界输入都是错误场景，
    按每条用例配置的expected_status分流校验：2xx走成功schema校验，
    4xx/5xx走错误结构校验。"""

    def test_boundary_cases(self, client, boundary_case):
        kwargs = {
            "query": resolve_query(boundary_case),
            "documents": resolve_documents(boundary_case),
            "model": boundary_case.get("model_override", MODEL),
        }
        if "top_n" in boundary_case:
            kwargs["top_n"] = boundary_case["top_n"]
        if "api_key_override" in boundary_case:
            kwargs["api_key"] = boundary_case["api_key_override"]

        resp = client.rerank(**kwargs)
        expected_code = resolve_expected_status(boundary_case)
        name = boundary_case["name"]

        assert resp.status_code == expected_code, (
            f"[{name}] 期望状态码{expected_code}，实际{resp.status_code}: {resp.text[:200]}"
        )

        if expected_code < 400:
            try:
                body = resp.json()
            except ValueError:
                pytest.fail(f"[{name}] 期望成功响应，但响应体不是合法JSON: {resp.text[:200]}")
            try:
                jsonschema_validate(instance=body, schema=RESPONSE_SCHEMA)
            except ValidationError as e:
                pytest.fail(f"[{name}] 成功响应不符合schema: {e.message}")
        else:
            try:
                body = resp.json()
            except ValueError:
                pytest.fail(f"[{name}] 错误响应不是合法JSON: {resp.text[:200]}")
            assert "error" in body or "code" in body, (
                f"[{name}] 错误体缺少结构化字段(error/code): {body}"
            )

    @pytest.mark.slow
    def test_documents_count_at_max_boundary(self, client):
        """恰好等于最大文档数上限时应该成功，超过1条才报错——
        验证边界值不是"差一错误"(off-by-one)。"""
        documents = generate_documents(MAX_DOCUMENTS)
        resp = client.rerank(query=SAMPLE_QUERY, documents=documents, model=MODEL)
        assert resp.status_code == 200, (
            f"文档数恰好等于上限{MAX_DOCUMENTS}时应该成功，实际返回{resp.status_code}: {resp.text[:200]}"
        )


# ============================================================
# 闭环监控共用工具：本地趋势历史 + Prometheus文本格式指标抓取
# (与embedding套件同款实现，历史文件路径不同，互不干扰)
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
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    result = {name: 0.0 for name in metrics_of_interest}
    found = {name: False for name in metrics_of_interest}

    for line in resp.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
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
            f"从{url}抓取指标时，以下指标未找到(可能是版本/框架不同导致指标名不一致): {missing}",
            UserWarning,
        )
    return result


# ============================================================
# 并发测试1：防串扰（不同query并发，跟自己的基准比对，而不是互相比对）
# ============================================================

class TestConcurrency:

    @pytest.mark.slow
    def test_concurrent_distinct_requests_no_crosstalk(self, client):
        """每个线程用不同的query(配合同一批documents)，先串行建立基准排序+分数，
        再并发重跑，逐个比对——如果服务端把某个并发请求的结果错发给了别的线程，
        这里能检测出来(顺序或分数对不上自己的基准)。"""
        workers = CONFIG["concurrency"]["workers"]
        queries = [f"并发rerank串扰测试查询第{i}条" for i in range(workers)]

        baseline = {}
        for q in queries:
            resp = client.rerank(query=q, documents=SAMPLE_DOCUMENTS, model=MODEL)
            assert resp.status_code == 200, f"基准建立失败: {resp.text[:200]}"
            baseline[q] = [(r["index"], r["relevance_score"]) for r in resp.json()["results"]]

        def call(q):
            resp = client.rerank(query=q, documents=SAMPLE_DOCUMENTS, model=MODEL)
            assert resp.status_code == 200
            return q, [(r["index"], r["relevance_score"]) for r in resp.json()["results"]]

        mismatches = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(call, q) for q in queries]
            for f in as_completed(futures):
                q, result = f.result()
                base_indices = [i for i, _ in baseline[q]]
                result_indices = [i for i, _ in result]
                if result_indices != base_indices:
                    mismatches.append((q, "顺序不一致", base_indices, result_indices))
                    continue
                for (bi, bs), (ri, rs) in zip(baseline[q], result):
                    diff = abs(bs - rs)
                    if diff > THRESHOLDS["idempotency_max_score_diff"]:
                        mismatches.append((q, "分数偏差过大", bi, bs, rs))

        assert not mismatches, (
            f"并发场景下检测到{len(mismatches)}条请求结果与自身基准不匹配，"
            f"疑似响应错位/串扰: {mismatches}"
        )

    @pytest.mark.slow
    def test_concurrent_identical_requests_consistency(self, client):
        """同一(query,documents)并发多次，各次分数应该基本一致。
        注意：跟embedding套件一样，这条只能测幂等性，测不出串扰
        (因为请求相同，串了也看不出来)，真正测串扰靠上面那条。"""
        workers = CONFIG["concurrency"]["workers"]

        def call():
            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
            assert resp.status_code == 200
            return {r["index"]: r["relevance_score"] for r in resp.json()["results"]}

        with ThreadPoolExecutor(max_workers=workers) as executor:
            all_scores = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

        base = all_scores[0]
        max_diff_allowed = THRESHOLDS["idempotency_max_score_diff"]
        for scores in all_scores[1:]:
            for idx in base:
                if idx not in scores:
                    continue
                diff = abs(base[idx] - scores[idx])
                assert diff <= max_diff_allowed, f"index={idx}并发多次调用分数差异{diff}超过容忍值"


# ============================================================
# 并发测试2：文档数x并发数矩阵（rerank独有，两个维度会互相放大压力）
# ============================================================

class TestDocCountConcurrencyMatrix:

    @pytest.mark.slow
    def test_doc_count_concurrency_matrix(self, client):
        """embedding的计算量跟并发数基本无关，但rerank一次请求内部要对
        query和每个文档都算一次相关性，文档数本身就是隐藏的计算量因子。
        这里把"文档数"和"并发请求数"做成矩阵一起测，观察两个维度叠加时
        哪个组合先出现失败或延迟异常飙升，而不是只看并发数一个维度。"""
        cfg = CONFIG["concurrency"]["doc_count_concurrency_matrix"]
        doc_counts = cfg["doc_counts"]
        worker_counts = cfg["worker_counts"]

        matrix_report = {}
        baseline_p95 = None

        for doc_count in doc_counts:
            documents = generate_documents(doc_count)
            for workers in worker_counts:

                def call():
                    start = time.time()
                    resp = client.rerank(query=SAMPLE_QUERY, documents=documents, model=MODEL)
                    elapsed_ms = (time.time() - start) * 1000
                    return resp.status_code, elapsed_ms

                with ThreadPoolExecutor(max_workers=workers) as executor:
                    results = [
                        f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])
                    ]

                statuses = [r[0] for r in results]
                latencies = [r[1] for r in results]
                fail_count = sum(1 for s in statuses if s != 200)
                p95 = float(np.percentile(latencies, 95))

                matrix_report[(doc_count, workers)] = {"fail_count": fail_count, "p95_ms": round(p95, 1)}
                if baseline_p95 is None:
                    baseline_p95 = p95

        print("\n[文档数x并发数矩阵] (doc_count, workers) -> P95延迟 / 失败数")
        for (doc_count, workers), stats in matrix_report.items():
            print(f"  doc_count={doc_count:>4} workers={workers:>4} -> "
                  f"P95={stats['p95_ms']:>8.0f}ms  fail={stats['fail_count']}")

        failing_combos = {k: v for k, v in matrix_report.items() if v["fail_count"] > 0}
        if failing_combos:
            warnings.warn(
                f"以下(doc_count, workers)组合出现请求失败: {failing_combos}，"
                f"说明该负载水平已超过服务端承载能力，建议作为容量规划参考",
                UserWarning,
            )

        worst_p95 = max(v["p95_ms"] for v in matrix_report.values())
        if baseline_p95 and worst_p95 > baseline_p95 * 5:
            warnings.warn(
                f"矩阵中最差P95({worst_p95:.0f}ms)是最小负载组合基线({baseline_p95:.0f}ms)的"
                f"{worst_p95/baseline_p95:.1f}倍，负载敏感度较高，建议关注扩容策略",
                UserWarning,
            )


# ============================================================
# 并发测试3：按文档规模分桶的长尾延迟（而不是笼统一个P99）
# ============================================================

class TestTailLatencyByDocCount:

    @pytest.mark.slow
    def test_p99_stability_by_doc_count(self, client):
        """延迟本来就该随文档数变化，如果把不同文档规模的请求混在一起算P99，
        数据没有诊断意义。这里分别对"小文档规模"和"大文档规模"两个桶，
        各自多轮重复统计P99变异系数，看长尾延迟在各自规模下是否稳定。"""
        cfg = CONFIG["concurrency"]["tail_latency"]
        rounds = cfg["rounds"]
        workers = cfg["workers_per_round"]
        doc_counts = CONFIG["concurrency"]["doc_count_concurrency_matrix"]["doc_counts"]
        buckets = {"small": min(doc_counts), "large": max(doc_counts)}

        report = {}
        for label, doc_count in buckets.items():
            documents = generate_documents(doc_count)

            def call():
                start = time.time()
                resp = client.rerank(query=SAMPLE_QUERY, documents=documents, model=MODEL)
                elapsed_ms = (time.time() - start) * 1000
                assert resp.status_code == 200
                return elapsed_ms

            p99_per_round = []
            for _ in range(rounds):
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    latencies = [
                        f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])
                    ]
                p99_per_round.append(float(np.percentile(latencies, 99)))

            mean_p99 = float(np.mean(p99_per_round))
            std_p99 = float(np.std(p99_per_round))
            cv = std_p99 / mean_p99 if mean_p99 > 0 else 0.0
            report[label] = {
                "doc_count": doc_count,
                "p99_per_round": [round(x, 1) for x in p99_per_round],
                "mean_p99_ms": round(mean_p99, 1),
                "cv": round(cv, 2),
            }

        print(f"\n[按文档规模分桶的P99稳定性] {report}")

        for label, stats in report.items():
            if stats["cv"] > 0.5:
                warnings.warn(
                    f"[{label}文档桶, doc_count={stats['doc_count']}] "
                    f"P99变异系数={stats['cv']}，波动较大，建议排查该文档规模下是否有间歇性瓶颈",
                    UserWarning,
                )


# ============================================================
# 并发测试4：限流韧性
# ============================================================

class TestRateLimitResilience:

    @pytest.mark.slow
    def test_backoff_and_recover_after_429(self, client):
        cfg = CONFIG["concurrency"]["rate_limit_resilience"]
        max_attempts = cfg["max_retry_attempts"]
        max_total_wait = cfg["max_total_wait_seconds"]
        burst_count = cfg["burst_count"]

        triggered = False
        resp = None
        for _ in range(burst_count):
            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
            if resp.status_code == 429:
                triggered = True
                break
        if not triggered:
            pytest.skip(f"连续{burst_count}次请求未触发限流，跳过退避恢复验证")

        total_waited = 0.0
        succeeded = False
        for attempt in range(max_attempts):
            retry_after = float(resp.headers.get("Retry-After", 1))
            if total_waited + retry_after > max_total_wait:
                break
            time.sleep(retry_after)
            total_waited += retry_after

            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
            if resp.status_code == 200:
                succeeded = True
                break
            assert resp.status_code == 429, (
                f"退避重试第{attempt+1}次后返回了非429/200的状态码{resp.status_code}"
            )

        assert succeeded, (
            f"按Retry-After退避重试{max_attempts}次(累计等待{total_waited:.1f}s)后仍未成功"
        )

    @pytest.mark.slow
    def test_service_recovers_immediately_after_limit_window(self, client):
        cfg = CONFIG["concurrency"]["rate_limit_resilience"]
        burst_count = cfg["burst_count"]

        resp = None
        for _ in range(burst_count):
            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
            if resp.status_code == 429:
                break
        if resp is None or resp.status_code != 429:
            pytest.skip(f"连续{burst_count}次请求未触发限流，跳过恢复验证")

        retry_after = float(resp.headers.get("Retry-After", 1))
        time.sleep(retry_after + 0.5)

        resp_after = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
        assert resp_after.status_code == 200, (
            f"限流窗口({retry_after}s)过后再次请求，期望恢复正常(200)，实际{resp_after.status_code}"
        )


# ============================================================
# 并发测试5：异步高并发（asyncio+httpx，排除线程调度开销）
# ============================================================

class TestAsyncConcurrency:

    @pytest.mark.slow
    @pytest.mark.skipif(not HTTPX_AVAILABLE, reason="需要安装httpx: pip install httpx")
    def test_high_concurrency_via_asyncio(self):
        workers = CONFIG["concurrency"]["async_workers"]

        async def run():
            async with httpx.AsyncClient(
                base_url=BASE_URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                timeout=TIMEOUT,
            ) as ac:

                async def call():
                    start = time.time()
                    resp = await ac.post(
                        "/rerank",
                        json={"model": MODEL, "query": SAMPLE_QUERY, "documents": SAMPLE_DOCUMENTS},
                    )
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
# 并发测试6：闭环监控 —— 压测同时关联服务端Prometheus指标
# ============================================================

class TestClosedLoopServerMonitoring:

    @pytest.mark.slow
    def test_server_metrics_endpoint_reachable(self):
        cfg = CONFIG["concurrency"]["monitoring"]
        metrics_url = cfg.get("server_metrics_url", "")
        if not metrics_url:
            pytest.skip("未配置 monitoring.server_metrics_url")

        resp = requests.get(metrics_url, timeout=10)
        assert resp.status_code == 200, f"服务端指标端点不可达: {resp.status_code}"
        assert resp.text.strip(), "服务端指标端点返回了空内容"

    @pytest.mark.slow
    def test_load_with_server_metrics_correlation(self, client):
        """rerank是compute-heavy的cross-encoder，GPU打满比embedding更容易发生，
        服务端指标关联的诊断价值比embedding场景更大——延迟升高时能立刻知道
        是不是GPU显存/KV cache的问题，而不是瞎猜。"""
        cfg = CONFIG["concurrency"]["monitoring"]
        metrics_url = cfg.get("server_metrics_url", "")
        if not metrics_url:
            pytest.skip("未配置 monitoring.server_metrics_url，跳过服务端指标关联采集")

        metrics_of_interest = cfg["server_metrics_of_interest"]
        workers = CONFIG["concurrency"]["workers"]

        before = fetch_prometheus_metrics(metrics_url, metrics_of_interest)

        def call():
            start = time.time()
            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
            elapsed_ms = (time.time() - start) * 1000
            assert resp.status_code == 200
            return elapsed_ms

        with ThreadPoolExecutor(max_workers=workers) as executor:
            latencies = [f.result() for f in as_completed([executor.submit(call) for _ in range(workers)])]

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

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": MODEL,
            "workers": workers,
            "p95_ms": round(p95, 1),
            "server_metrics_before": before,
            "server_metrics_after": after,
        }
        _append_history(record)

        waiting_key = "vllm:num_requests_waiting"
        if waiting_key in after and after[waiting_key] > cfg["queue_saturation_warn_threshold"]:
            warnings.warn(
                f"压测结束后服务端等待队列({waiting_key})仍为{after[waiting_key]}，"
                f"超过阈值{cfg['queue_saturation_warn_threshold']}，积压未消化",
                UserWarning,
            )

        gpu_cache_key = "vllm:gpu_cache_usage_perc"
        if gpu_cache_key in after and after[gpu_cache_key] > cfg["gpu_cache_warn_ratio"]:
            warnings.warn(
                f"压测期间GPU KV cache占用({gpu_cache_key})达到{after[gpu_cache_key]:.1%}，"
                f"超过预警线{cfg['gpu_cache_warn_ratio']:.0%}，这很可能是延迟升高的真正根因",
                UserWarning,
            )

    @pytest.mark.slow
    def test_p95_regression_against_history(self, client):
        """本次P95跟本地历史记录均值对比，发现趋势性劣化(轻量版闭环，非完整监控系统)。"""
        cfg = CONFIG["concurrency"]["monitoring"]
        workers = CONFIG["concurrency"]["workers"]

        def call():
            start = time.time()
            resp = client.rerank(query=SAMPLE_QUERY, documents=SAMPLE_DOCUMENTS, model=MODEL)
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
            history_p95_values = [h["p95_ms"] for h in history if "p95_ms" in h]
            if history_p95_values:
                baseline_mean = float(np.mean(history_p95_values))
                ratio = p95 / baseline_mean if baseline_mean > 0 else 1.0
                print(
                    f"\n[性能趋势] 本次P95={p95:.0f}ms，"
                    f"最近{len(history_p95_values)}次历史均值={baseline_mean:.0f}ms，比值={ratio:.2f}"
                )
                if ratio > cfg["regression_warn_ratio"]:
                    warnings.warn(
                        f"本次P95延迟({p95:.0f}ms)是历史均值({baseline_mean:.0f}ms)的{ratio:.2f}倍，"
                        f"超过预警线{cfg['regression_warn_ratio']}，疑似性能退化",
                        UserWarning,
                    )
        else:
            print(f"\n[性能趋势] 本次P95={p95:.0f}ms，暂无历史记录用于对比(首次运行)")

        _append_history(record)
