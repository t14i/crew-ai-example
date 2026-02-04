"""
01_quickstart.py - CrewAI Quick Start

目的: CrewAI基本構造の理解
- Agent 1体 + Task 1つ + Crew の最小構成
- role/goal/backstory の効果確認
- Python方式での定義

LangGraph比較:
- CrewAI: Agent/Task/Crew の宣言的な定義
- LangGraph: StateGraph/Node/Edge の明示的な接続
"""

from crewai import Agent, Task, Crew


def main():
    # Agent定義
    # role: エージェントの役割（LLMへのシステムプロンプトに含まれる）
    # goal: エージェントの目標（タスク遂行の指針）
    # backstory: 背景設定（より詳細なコンテキスト）
    researcher = Agent(
        role="Research Analyst",
        goal="Provide accurate and insightful analysis on given topics",
        backstory="""You are an experienced research analyst with a keen eye
        for detail. You excel at gathering information and presenting it
        in a clear, structured manner.""",
        verbose=True,  # 実行過程を表示
    )

    # Task定義
    # description: タスクの詳細な説明
    # expected_output: 期待される出力形式
    # agent: タスクを実行するエージェント
    research_task = Task(
        description="""Research the current state of AI agent frameworks.
        Focus on:
        1. Main frameworks available
        2. Key differences between them
        3. Typical use cases""",
        expected_output="""A structured report containing:
        - List of major AI agent frameworks
        - Comparison table of features
        - Recommendations for different use cases""",
        agent=researcher,
    )

    # Crew定義
    # agents: 参加するエージェントのリスト
    # tasks: 実行するタスクのリスト
    crew = Crew(
        agents=[researcher],
        tasks=[research_task],
        verbose=True,  # 詳細なログ出力
    )

    # 実行
    print("=" * 60)
    print("CrewAI Quick Start - Minimal Configuration")
    print("=" * 60)

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)
    print(result)

    # CrewOutput の属性確認
    print("\n" + "=" * 60)
    print("CrewOutput attributes:")
    print("=" * 60)
    print(f"Type: {type(result)}")
    print(f"Raw output: {result.raw[:200]}..." if len(result.raw) > 200 else f"Raw output: {result.raw}")

    if result.tasks_output:
        print(f"\nTasks output count: {len(result.tasks_output)}")
        for i, task_output in enumerate(result.tasks_output):
            print(f"  Task {i+1}: {type(task_output)}")

    # Token使用量（利用可能な場合）
    if hasattr(result, "token_usage"):
        print(f"\nToken usage: {result.token_usage}")


if __name__ == "__main__":
    main()
