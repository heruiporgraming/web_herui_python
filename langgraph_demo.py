"""
LangGraph Demo — 智能任务路由器
=================================
根据任务类型自动分发到不同的处理器，最后汇总输出。

图结构:
  classifier (分类) → 条件路由 → math_handler / text_handler / general_handler
                                      ↘          ↓          ↙
                                          finalizer (汇总)

无需 API Key，纯 Python 逻辑即可运行。
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# ── 1. 定义 State ─────────────────────────────────────────────
# State 是流经图中所有节点的共享数据结构


class TaskState(TypedDict):
    task: str          # 输入任务文本
    category: str      # 分类结果: "math" / "text" / "general"
    output: str        # 处理结果
    node_log: list[str]  # 记录经过的节点（调试用）


# ── 2. 节点函数 (node) ────────────────────────────────────────
# 每个节点接收 state，返回更新后的 state dict


def classifier(state: TaskState) -> dict:
    """分析任务文本，决定属于哪个类别。"""
    task = state["task"].lower()

    math_keywords = ["计算", "算", "加", "减", "乘", "除", "math",
                     "+", "-", "*", "数字", "数值", "求和", "平方"]
    text_keywords = ["翻译", "翻译成", "translate", "润色", "改写",
                     "总结", "摘要", "总结一下", "文本"]

    if any(kw in task for kw in math_keywords):
        category = "math"
    elif any(kw in task for kw in text_keywords):
        category = "text"
    else:
        category = "general"

    print(f"  [classifier] 任务: '{task[:30]}...' → 分类为: {category}")
    return {
        "category": category,
        "node_log": state.get("node_log", []) + [f"classifier → {category}"]
    }


def math_handler(state: TaskState) -> dict:
    """处理数学类任务：从文本中提取数字并计算。"""
    import re
    task = state["task"]

    # 尝试抽取数字并求和
    numbers = [float(n) for n in re.findall(r'\d+\.?\d*', task)]
    if numbers:
        result = f"抽取到的数字: {numbers}\n求和: {sum(numbers)}\n平均值: {sum(numbers)/len(numbers):.2f}"
    else:
        result = "未在任务中找到数字，无法执行数学计算。"

    print(f"  [math_handler] 处理完成，共 {len(numbers)} 个数字")
    return {
        "output": result,
        "node_log": state["node_log"] + ["math_handler ✓"]
    }


def text_handler(state: TaskState) -> dict:
    """处理文本类任务：模拟文本变换。"""
    task = state["task"]

    # 简单模拟：把文本反转作为"处理结果"
    if "翻译" in task:
        result = f"[模拟翻译] 原文: {task}\n英文模拟: This is a simulated translation of the input text."
    elif "润色" in task:
        result = f"[模拟润色] 原文: {task}\n润色后: (经过优化后的文本版本)"
    elif "总结" in task:
        result = f"[模拟总结] 原文: {task}\n摘要: 这是对输入内容的简要概括。"
    else:
        result = f"[文本处理] 对输入 '{task[:40]}...' 进行了文本处理"

    print(f"  [text_handler] 文本处理完成")
    return {
        "output": result,
        "node_log": state["node_log"] + ["text_handler ✓"]
    }


def general_handler(state: TaskState) -> dict:
    """处理通用任务：直接回显任务内容。"""
    result = f"[通用处理] 收到任务: {state['task']}\n未匹配到特定处理器，执行默认逻辑。"

    print(f"  [general_handler] 通用处理完成")
    return {
        "output": result,
        "node_log": state["node_log"] + ["general_handler ✓"]
    }


def finalizer(state: TaskState) -> dict:
    """汇总输出，打印最终结果。"""
    print(f"\n{'='*50}")
    print(f"  最终结果")
    print(f"{'='*50}")
    print(f"  原始任务: {state['task'][:60]}")
    print(f"  分类结果: {state['category']}")
    print(f"  处理结果:\n{state['output']}")
    print(f"  经过节点: {' → '.join(state['node_log'])}")
    print(f"{'='*50}\n")
    return state


# ── 3. 条件路由函数 ─────────────────────────────────────────


def route_by_category(state: TaskState) -> Literal["math_handler", "text_handler", "general_handler"]:
    """根据 classifier 的分类结果决定下一个节点。"""
    category = state["category"]
    if category == "math":
        return "math_handler"
    elif category == "text":
        return "text_handler"
    else:
        return "general_handler"


# ── 4. 构建图 (Graph) ────────────────────────────────────────


def build_graph() -> StateGraph:
    """组装 LangGraph 状态图。"""
    graph = StateGraph(TaskState)

    # 添加节点
    graph.add_node("classifier", classifier)
    graph.add_node("math_handler", math_handler)
    graph.add_node("text_handler", text_handler)
    graph.add_node("general_handler", general_handler)
    graph.add_node("finalizer", finalizer)

    # 设置入口
    graph.set_entry_point("classifier")

    # 条件路由：classifier → 三种 handler 之一
    graph.add_conditional_edges(
        "classifier",
        route_by_category,
        {
            "math_handler": "math_handler",
            "text_handler": "text_handler",
            "general_handler": "general_handler",
        }
    )

    # 三种 handler 都汇聚到 finalizer
    graph.add_edge("math_handler", "finalizer")
    graph.add_edge("text_handler", "finalizer")
    graph.add_edge("general_handler", "finalizer")

    # finalizer 是终点
    graph.add_edge("finalizer", END)

    return graph


# ── 5. 运行 Demo ─────────────────────────────────────────────


def main():
    print("=" * 50)
    print("  LangGraph Demo — 智能任务路由器")
    print("=" * 50)
    print()

    # 编译图
    graph = build_graph()
    app = graph.compile()

    # 测试用例
    test_tasks = [
        "请帮我计算 3.14 + 2.86 并求和得出结果",
        "把这段话翻译成英文：今天的天气真好",
        "帮我查一下北京时间现在是几点",
        "计算这些数字的平均值: 10, 20, 30, 50, 100",
        "帮我润色一下这段文字，让它更专业",
        "随便说点什么吧",
    ]

    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'─'*50}")
        print(f"  测试 #{i}")
        print(f"{'─'*50}")

        initial_state: TaskState = {
            "task": task,
            "category": "",
            "output": "",
            "node_log": [],
        }

        # 执行图
        final_state = app.invoke(initial_state)

    print("\n所有测试完成！")


if __name__ == "__main__":
    main()
