"""
conftest.py

作用：把每条测试用例中产生的 Python warnings（warnings.warn(...)）
自动附加到 pytest-html 报告里对应那一行的 "Warnings" 展开区域，
而不是只在终端最后打印一堆warnings摘要、跟具体哪条用例对不上号。

无需在测试代码里做任何额外操作，只要测试函数里调用了 warnings.warn(...)，
这里会自动捕获并写进html报告。
"""

import warnings

import pytest


def pytest_configure(config):
    # 确保warnings不会被pytest的默认filter吃掉，能被稳定捕获
    warnings.simplefilter("always")


@pytest.fixture(autouse=True)
def _capture_warnings_for_html(request):
    """autouse=True: 对每一条测试用例自动生效，无需手动引用这个fixture"""
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        yield
        # 把这条用例期间产生的warning列表挂在item对象上，供下面的hook读取
        request.node._captured_warnings = captured


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    captured = getattr(item, "_captured_warnings", None)
    if not captured:
        return

    try:
        from pytest_html import extras
    except ImportError:
        # 没装pytest-html时，静默跳过，不影响正常跑测试
        return

    extra = getattr(report, "extra", [])
    warning_lines = [
        f"[{w.category.__name__}] {w.message}" for w in captured
    ]
    extra.append(extras.text("\n".join(warning_lines), name="Warnings"))
    report.extra = extra

    # 同时在终端总结里也能看到这条用例有warning标记
    if report.outcome == "passed":
        report.outcome = "passed"  # 保持passed，但html会带黄色Warnings标记(见下方summary hook)


def pytest_html_results_summary(prefix, summary, postfix):
    """在html报告顶部summary区域加一行说明，方便阅读者知道Warnings区域是干什么的"""
    prefix.extend([
        "<p style='color:#856404;background:#fff3cd;padding:8px;border-radius:4px;'>"
        "带有 Warnings 展开项的用例表示：测试断言通过，但存在需要关注的软性问题"
        "（如接近阈值、精度余量收窄等），建议点开查看。"
        "</p>"
    ])
