"""
conftest.py

作用：把每条测试用例中产生的 Python warnings（warnings.warn(...)）
自动附加到 pytest-html 报告里对应那一行的 Links 区域，
同时不影响warnings在终端的正常打印和pytest自身的warnings summary。

环境要求：pytest-html 4.2（只用了 report.extras，不兼容<4.0的report.extra）。

实现要点（踩过的两个坑）：
1. 不能用 warnings.catch_warnings(record=True) 整体接管——会把警告吞进
   自己的列表，导致pytest自身的采集机制收不到，终端就不再打印。
2. 不能依赖 pytest_warning_recorded 钩子——pytest是在整条用例
   setup+call+teardown全部结束后才统一触发这个钩子的，这时"call"阶段的
   report早就生成完了，我们的makereport钩子读到的永远是空数据。

正确做法：在测试setup阶段就接管 warnings.showwarning，警告产生的那一刻
立即记录一份副本（这样时序上绝对不会晚），同时照常调用原始的
showwarning（也就是pytest自己的记录函数），把警告转发出去，保证pytest
自身的机制和终端打印完全不受影响。
"""

from collections import defaultdict

import pytest
import warnings

# nodeid -> 该用例执行期间产生的所有warning，实时写入，不等事后通知
_warnings_by_nodeid = defaultdict(list)


@pytest.fixture(autouse=True)
def _capture_warnings_for_html(request):
    nodeid = request.node.nodeid
    original_showwarning = warnings.showwarning

    def _showwarning_and_forward(message, category, filename, lineno, file=None, line=None):
        # 先记一份副本给html用
        _warnings_by_nodeid[nodeid].append(
            warnings.WarningMessage(message, category, filename, lineno, file, line)
        )
        # 再照常转发给原来的showwarning(此时是pytest自己的记录函数)，
        # 保证pytest自身机制和终端打印不受影响
        original_showwarning(message, category, filename, lineno, file, line)

    warnings.showwarning = _showwarning_and_forward
    try:
        yield
    finally:
        warnings.showwarning = original_showwarning


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    captured = _warnings_by_nodeid.get(item.nodeid)
    if not captured:
        return

    try:
        from pytest_html import extras
    except ImportError:
        # 没装pytest-html时，静默跳过，不影响正常跑测试
        return

    warning_lines = [
        f"[{w.category.__name__}] {w.message}" for w in captured
    ]
    full_text = "\n".join(warning_lines)

    # 关键：extras.text(content, name=...) 里的 name 才是显示在行内Links区域、
    # 不用点开就能直接看到的文字。之前name写死成"Warnings"，导致必须点进去
    # 才能看到具体内容。现在把警告原文本身放进name里，直接可见。
    preview = " | ".join(warning_lines)
    if len(preview) > 200:
        preview = preview[:200] + "…（完整内容见链接）"
    extra_block = extras.text(full_text, name=preview)

    extras_list = getattr(report, "extras", [])
    extras_list.append(extra_block)
    report.extras = extras_list


def pytest_html_results_summary(prefix, summary, postfix):
    """在html报告顶部summary区域加一行说明，方便阅读者知道Warnings区域是干什么的"""
    prefix.extend([
        "<p style='color:#856404;background:#fff3cd;padding:8px;border-radius:4px;'>"
        "带有 Warnings 展开项的用例表示：测试断言通过，但存在需要关注的软性问题"
        "（如接近阈值、精度余量收窄等），建议点开查看。"
        "</p>"
    ])
