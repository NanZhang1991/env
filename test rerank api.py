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

import os
import time
import warnings
from typing import List, Optional, Union

import numpy as np
import pytest
import requests
import yaml
from jsonschema import validate as jsonschema_validate, ValidationError


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
