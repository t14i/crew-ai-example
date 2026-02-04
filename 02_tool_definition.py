"""
02_tool_definition.py - Tool定義方法の比較

目的: CrewAIでのTool定義方法を検証
- @tool デコレータ（シンプル）
- @tool with type hints
- BaseTool クラス継承（Pydantic args_schema使用可能）

LangGraph比較:
- @tool decorator → ほぼ同等
- Pydantic連携 → BaseToolで利用可能
"""

from typing import Type

from crewai import Agent, Task, Crew
from crewai.tools import tool, BaseTool
from pydantic import BaseModel, Field


# =============================================================================
# 方法1: @tool デコレータ（最もシンプル）
# =============================================================================
@tool("Simple Calculator")
def simple_calculator(operation: str, a: float, b: float) -> str:
    """
    Perform basic arithmetic operations.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number
    """
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero",
    }
    result = operations.get(operation, "Unknown operation")
    return f"Result of {operation}({a}, {b}) = {result}"


# =============================================================================
# 方法2: @tool with type hints (CrewAIではargs_schemaは非サポート)
# =============================================================================
@tool("Weather Lookup")
def weather_lookup(city: str, unit: str = "celsius") -> str:
    """
    Get current weather for a city.

    This is a mock implementation for demonstration.
    """
    # Mock weather data
    mock_weather = {
        "Tokyo": {"temp_c": 22, "condition": "Sunny"},
        "New York": {"temp_c": 18, "condition": "Cloudy"},
        "London": {"temp_c": 15, "condition": "Rainy"},
    }

    weather = mock_weather.get(city, {"temp_c": 20, "condition": "Unknown"})
    temp = weather["temp_c"]

    if unit == "fahrenheit":
        temp = temp * 9 / 5 + 32
        unit_symbol = "°F"
    else:
        unit_symbol = "°C"

    return f"Weather in {city}: {temp}{unit_symbol}, {weather['condition']}"


# =============================================================================
# 方法3: BaseTool クラス継承（最も柔軟）
# =============================================================================
class DatabaseQueryInput(BaseModel):
    """Input schema for database query tool."""

    table: str = Field(..., description="Table name to query")
    columns: str = Field(default="*", description="Columns to select (comma-separated)")
    limit: int = Field(default=10, description="Maximum number of rows to return")


class DatabaseQueryTool(BaseTool):
    """Tool for querying a mock database."""

    name: str = "Database Query"
    description: str = "Query data from a mock database. Use this to retrieve structured data."
    args_schema: Type[BaseModel] = DatabaseQueryInput

    def _run(self, table: str, columns: str = "*", limit: int = 10) -> str:
        """Execute the database query."""
        # Mock database
        mock_data = {
            "users": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
            ],
            "products": [
                {"id": 1, "name": "Widget", "price": 9.99},
                {"id": 2, "name": "Gadget", "price": 19.99},
            ],
        }

        if table not in mock_data:
            return f"Error: Table '{table}' not found"

        data = mock_data[table][:limit]

        if columns != "*":
            col_list = [c.strip() for c in columns.split(",")]
            data = [{k: v for k, v in row.items() if k in col_list} for row in data]

        return f"Query result from {table}:\n{data}"


def main():
    # 全ツールをインスタンス化
    tools = [
        simple_calculator,
        weather_lookup,
        DatabaseQueryTool(),
    ]

    # ツール情報を表示
    print("=" * 60)
    print("Tool Definition Comparison")
    print("=" * 60)

    for t in tools:
        print(f"\nTool: {t.name}")
        print(f"  Description: {t.description[:80]}...")
        print(f"  Type: {type(t).__name__}")
        if hasattr(t, "args_schema") and t.args_schema:
            print(f"  Args Schema: {t.args_schema.model_json_schema()}")

    # Agent with tools
    analyst = Agent(
        role="Data Analyst",
        goal="Analyze data using available tools",
        backstory="You are a skilled analyst who uses tools efficiently.",
        tools=tools,
        verbose=True,
    )

    # Task that requires tool usage
    analysis_task = Task(
        description="""Perform the following analysis:
        1. Calculate 15 * 7 using the calculator
        2. Get the weather in Tokyo
        3. Query the users table from the database

        Summarize all results.""",
        expected_output="A summary of all tool results",
        agent=analyst,
    )

    crew = Crew(
        agents=[analyst],
        tasks=[analysis_task],
        verbose=True,
    )

    print("\n" + "=" * 60)
    print("Executing Crew with Tools")
    print("=" * 60)

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
