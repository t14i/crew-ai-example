"""
04_tool_error_handling.py - Tool Error Handling

Purpose: Verify error handling during tool execution
- Behavior when exceptions occur inside tools
- Whether agent retries
- Error message propagation

LangGraph Comparison:
- LangGraph: handle_tool_errors=True returns errors as results
- CrewAI: Errors are automatically propagated to the agent
"""

from typing import Type

from crewai import Agent, Task, Crew
from crewai.tools import tool, BaseTool
from pydantic import BaseModel, Field


# =============================================================================
# Tool that throws exceptions
# =============================================================================
@tool("Failing Tool")
def failing_tool(should_fail: bool = True) -> str:
    """
    A tool that fails on purpose for testing error handling.

    Args:
        should_fail: If True, raises an exception
    """
    if should_fail:
        raise ValueError("Intentional failure for testing!")
    return "Success! Tool executed without errors."


# =============================================================================
# Tool that conditionally fails (for retry testing)
# =============================================================================
call_counter = {"count": 0}


@tool("Flaky Tool")
def flaky_tool(operation: str) -> str:
    """
    A tool that fails on first call but succeeds on subsequent calls.
    Useful for testing retry behavior.

    Args:
        operation: The operation to perform
    """
    call_counter["count"] += 1
    print(f"  [Flaky Tool] Call #{call_counter['count']} for operation: {operation}")

    if call_counter["count"] == 1:
        raise ConnectionError("Simulated network error on first attempt!")

    return f"Operation '{operation}' completed successfully on attempt #{call_counter['count']}"


# =============================================================================
# Tool that returns errors (error message instead of exception)
# =============================================================================
class DivisionInput(BaseModel):
    """Input for division tool."""

    dividend: float = Field(..., description="Number to be divided")
    divisor: float = Field(..., description="Number to divide by")


class SafeDivisionTool(BaseTool):
    """A division tool that returns error messages instead of raising exceptions."""

    name: str = "Safe Division"
    description: str = "Divide two numbers safely, returning error message for invalid operations."
    args_schema: Type[BaseModel] = DivisionInput

    def _run(self, dividend: float, divisor: float) -> str:
        print(f"  [Safe Division] {dividend} / {divisor}")

        if divisor == 0:
            return "Error: Division by zero is not allowed. Please provide a non-zero divisor."

        result = dividend / divisor
        return f"{dividend} / {divisor} = {result}"


# =============================================================================
# Tool that causes input validation errors
# =============================================================================
class StrictInput(BaseModel):
    """Strict input validation."""

    value: int = Field(..., ge=0, le=100, description="A value between 0 and 100")


class StrictValidationTool(BaseTool):
    """Tool with strict input validation."""

    name: str = "Strict Validator"
    description: str = "A tool that only accepts values between 0 and 100."
    args_schema: Type[BaseModel] = StrictInput

    def _run(self, value: int) -> str:
        return f"Validated value: {value}"


def main():
    print("=" * 60)
    print("Tool Error Handling Test")
    print("=" * 60)

    # Reset counter
    call_counter["count"] = 0

    tools = [
        failing_tool,
        flaky_tool,
        SafeDivisionTool(),
        StrictValidationTool(),
    ]

    # Error handling specialist agent
    error_handler = Agent(
        role="Error Handling Specialist",
        goal="Test various error scenarios and observe how errors are handled",
        backstory="""You are an expert at testing error handling.
        You intentionally trigger errors to verify system robustness.
        When a tool fails, you analyze the error and try alternative approaches.""",
        tools=tools,
        verbose=True,
        max_retry_limit=3,  # Allow retries on failure
    )

    # Task designed to trigger various error conditions
    error_test_task = Task(
        description="""Test error handling by:
        1. Use the Safe Division tool to divide 10 by 0 (should return error message)
        2. Use the Safe Division tool to divide 10 by 2 (should succeed)
        3. Use the Flaky Tool with operation "test" (may fail first, retry should succeed)
        4. Try the Failing Tool with should_fail=True, then with should_fail=False

        Report what errors occurred and how they were handled.""",
        expected_output="""A report containing:
        - Each error encountered
        - How the agent recovered or handled the error
        - Final successful results where applicable""",
        agent=error_handler,
    )

    crew = Crew(
        agents=[error_handler],
        tasks=[error_test_task],
        verbose=True,
    )

    print("\n" + "=" * 60)
    print("Executing Error Handling Test")
    print("=" * 60)

    try:
        result = crew.kickoff()

        print("\n" + "=" * 60)
        print("Result:")
        print("=" * 60)
        print(result)

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"Crew execution failed with error: {type(e).__name__}")
        print("=" * 60)
        print(f"Error message: {e}")

    print(f"\n[Debug] Flaky tool was called {call_counter['count']} times")


if __name__ == "__main__":
    main()
