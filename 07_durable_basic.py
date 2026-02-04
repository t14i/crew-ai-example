"""
07_durable_basic.py - Durable Execution 基本

目的: CrewAI Flow での状態管理の検証
- Flow の基本的な使い方
- @start, @listen によるステップ連携
- 状態管理

LangGraph比較:
- LangGraph: Checkpointer (Memory/SQLite/Postgres) を明示的に設定
- CrewAI: Flow + Pydantic state で状態管理
"""

from datetime import datetime
from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel


# 永続化用のDB設定
DB_PATH = Path("./db")
DB_PATH.mkdir(exist_ok=True)


class WorkflowState(BaseModel):
    """State for the workflow."""

    workflow_id: str = ""
    current_step: str = "init"
    data: dict = {}
    history: list = []
    created_at: str = ""
    updated_at: str = ""


class SimpleWorkflow(Flow[WorkflowState]):
    """
    A simple workflow demonstrating CrewAI Flow.

    Flow steps are connected via @start and @listen decorators.
    @listen uses method name (not return value) to chain steps.
    """

    @start()
    def step1_initialize(self):
        """Initialize the workflow."""
        print("\n[Step 1] Initializing workflow...")

        self.state.workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.state.current_step = "initialized"
        self.state.created_at = datetime.now().isoformat()
        self.state.updated_at = datetime.now().isoformat()
        self.state.history.append({
            "step": "initialize",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })

        print(f"[Step 1] Workflow ID: {self.state.workflow_id}")

    @listen(step1_initialize)
    def step2_gather_data(self):
        """Gather data step."""
        print("\n[Step 2] Gathering data...")

        # Simulate data gathering
        self.state.data = {
            "source": "api",
            "records": 100,
            "quality_score": 0.95
        }
        self.state.current_step = "data_gathered"
        self.state.updated_at = datetime.now().isoformat()
        self.state.history.append({
            "step": "gather_data",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "records": 100
        })

        print(f"[Step 2] Gathered {self.state.data['records']} records")

    @listen(step2_gather_data)
    def step3_process_data(self):
        """Process the gathered data."""
        print("\n[Step 3] Processing data...")

        # Simulate processing
        self.state.data["processed"] = True
        self.state.data["analysis"] = {
            "mean": 42.5,
            "median": 40.0,
            "std_dev": 5.2
        }
        self.state.current_step = "data_processed"
        self.state.updated_at = datetime.now().isoformat()
        self.state.history.append({
            "step": "process_data",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })

        print(f"[Step 3] Processing complete. Analysis: {self.state.data['analysis']}")

    @listen(step3_process_data)
    def step4_generate_report(self):
        """Generate final report."""
        print("\n[Step 4] Generating report...")

        self.state.current_step = "completed"
        self.state.updated_at = datetime.now().isoformat()
        self.state.history.append({
            "step": "generate_report",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })

        report = f"""
Workflow Report
===============
ID: {self.state.workflow_id}
Created: {self.state.created_at}
Completed: {self.state.updated_at}

Data Summary:
- Records: {self.state.data.get('records', 'N/A')}
- Quality Score: {self.state.data.get('quality_score', 'N/A')}

Analysis Results:
- Mean: {self.state.data.get('analysis', {}).get('mean', 'N/A')}
- Median: {self.state.data.get('analysis', {}).get('median', 'N/A')}
- Std Dev: {self.state.data.get('analysis', {}).get('std_dev', 'N/A')}

Execution History:
{chr(10).join([f"  - {h['step']}: {h['status']} at {h['timestamp']}" for h in self.state.history])}
"""
        print(report)
        return report


def main():
    print("=" * 60)
    print("Durable Execution: Basic Flow Test")
    print("=" * 60)
    print("""
This example demonstrates CrewAI Flow for workflow management.

Key Points:
- @start() marks the entry point
- @listen(method) chains to previous method
- State is managed via Pydantic model

LangGraph Comparison:
- CrewAI Flow: Decorator-based, implicit connections
- LangGraph: Explicit add_edge(), more control
""")

    # Run the workflow
    print("\n" + "=" * 60)
    print("Executing Workflow")
    print("=" * 60)

    flow = SimpleWorkflow()
    result = flow.kickoff()

    print("\n" + "=" * 60)
    print("Workflow Result:")
    print("=" * 60)
    print(result)

    # Display final state
    print("\n" + "=" * 60)
    print("Final State Object:")
    print("=" * 60)
    print(f"Workflow ID: {flow.state.workflow_id}")
    print(f"Current Step: {flow.state.current_step}")
    print(f"History Length: {len(flow.state.history)}")
    print(f"Data: {flow.state.data}")


if __name__ == "__main__":
    main()
