"""
08_durable_resume.py - Durable Execution 再開テスト

目的: 中断したワークフローの再開機能を検証
- プロセス再起動後の復旧
- 中断ポイントからの再開
- 状態の整合性

LangGraph比較:
- LangGraph: thread_id でチェックポイントを特定
- CrewAI: Flow state ID / method_name で再開

使い方:
1. 最初に実行: python 08_durable_resume.py --start
2. 中断後に再開: python 08_durable_resume.py --resume <flow_id>
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel


# ステート保存用のファイルパス（シンプルな永続化のデモ用）
STATE_FILE = Path("./db/resume_state.json")
STATE_FILE.parent.mkdir(exist_ok=True)


class LongRunningState(BaseModel):
    """State for a long-running workflow that may need to be resumed."""

    flow_id: str = ""
    current_phase: int = 0
    total_phases: int = 5
    results: list = []
    is_complete: bool = False
    started_at: str = ""
    last_checkpoint: str = ""
    interrupted: bool = False


class ResumableWorkflow(Flow[LongRunningState]):
    """
    A workflow designed to demonstrate resumption after interruption.

    This workflow has multiple phases and can be interrupted and resumed.
    Each phase simulates long-running work.
    """

    def save_checkpoint(self):
        """Manually save checkpoint to file for demonstration."""
        self.state.last_checkpoint = datetime.now().isoformat()
        checkpoint = {
            "flow_id": self.state.flow_id,
            "state": self.state.model_dump()
        }
        with open(STATE_FILE, "w") as f:
            json.dump(checkpoint, f, indent=2)
        print(f"[Checkpoint] Saved to {STATE_FILE}")

    @start()
    def phase_0_initialize(self):
        """Initialize the long-running workflow."""
        print("\n[Phase 0] Initializing long-running workflow...")

        if not self.state.flow_id:
            self.state.flow_id = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.state.started_at = datetime.now().isoformat()
            self.state.current_phase = 0

        self.state.results.append({
            "phase": 0,
            "action": "initialize",
            "timestamp": datetime.now().isoformat()
        })

        self.save_checkpoint()
        print(f"[Phase 0] Initialized workflow: {self.state.flow_id}")

    @listen(phase_0_initialize)
    def phase_1_data_collection(self):
        """Phase 1: Data collection (simulated)."""
        print("\n[Phase 1] Starting data collection...")

        self.state.current_phase = 1
        print("[Phase 1] Simulating data collection (1 second)...")
        time.sleep(1)

        self.state.results.append({
            "phase": 1,
            "action": "data_collection",
            "records_collected": 500,
            "timestamp": datetime.now().isoformat()
        })

        self.save_checkpoint()
        print("[Phase 1] Data collection complete.")

    @listen(phase_1_data_collection)
    def phase_2_validation(self):
        """Phase 2: Data validation."""
        print("\n[Phase 2] Starting data validation...")

        self.state.current_phase = 2
        print("[Phase 2] Simulating validation (1 second)...")
        time.sleep(1)

        self.state.results.append({
            "phase": 2,
            "action": "validation",
            "valid_records": 485,
            "invalid_records": 15,
            "timestamp": datetime.now().isoformat()
        })

        self.save_checkpoint()
        print("[Phase 2] Validation complete.")

    @listen(phase_2_validation)
    def phase_3_processing(self):
        """Phase 3: Data processing (long-running, interruptible)."""
        print("\n[Phase 3] Starting data processing...")
        print("[Phase 3] This phase is INTERRUPTIBLE. Press Ctrl+C to simulate interruption.")

        self.state.current_phase = 3

        try:
            for i in range(3):
                print(f"[Phase 3] Processing batch {i+1}/3...")
                time.sleep(1)
                self.save_checkpoint()  # Frequent checkpoints

        except KeyboardInterrupt:
            print("\n[Phase 3] INTERRUPTED! State has been saved.")
            self.state.interrupted = True
            self.save_checkpoint()
            raise

        self.state.results.append({
            "phase": 3,
            "action": "processing",
            "batches_processed": 3,
            "timestamp": datetime.now().isoformat()
        })

        print("[Phase 3] Processing complete.")

    @listen(phase_3_processing)
    def phase_4_aggregation(self):
        """Phase 4: Result aggregation."""
        print("\n[Phase 4] Starting aggregation...")

        self.state.current_phase = 4
        time.sleep(1)

        self.state.results.append({
            "phase": 4,
            "action": "aggregation",
            "aggregated_results": {"mean": 42.0, "count": 485},
            "timestamp": datetime.now().isoformat()
        })

        self.save_checkpoint()
        print("[Phase 4] Aggregation complete.")

    @listen(phase_4_aggregation)
    def phase_5_finalize(self):
        """Phase 5: Finalization."""
        print("\n[Phase 5] Finalizing workflow...")

        self.state.current_phase = 5
        self.state.is_complete = True

        self.state.results.append({
            "phase": 5,
            "action": "finalize",
            "timestamp": datetime.now().isoformat()
        })

        self.save_checkpoint()
        print("[Phase 5] Workflow complete!")

        return self.generate_final_report()

    def generate_final_report(self):
        """Generate the final report."""
        return f"""
Long-Running Workflow Report
============================
Flow ID: {self.state.flow_id}
Started: {self.state.started_at}
Completed: {datetime.now().isoformat()}

Phases Completed: {self.state.current_phase}/{self.state.total_phases}

Phase Results:
{chr(10).join([f"  - Phase {r['phase']}: {r['action']}" for r in self.state.results])}

Status: {'COMPLETE' if self.state.is_complete else 'INCOMPLETE'}
"""


def load_checkpoint():
    """Load the last checkpoint from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None


def main():
    parser = argparse.ArgumentParser(description="Resumable Workflow Demo")
    parser.add_argument("--start", action="store_true", help="Start a new workflow")
    parser.add_argument("--resume", type=str, help="Resume workflow with given flow_id")
    parser.add_argument("--status", action="store_true", help="Check current checkpoint status")
    args = parser.parse_args()

    print("=" * 60)
    print("Durable Execution: Resume Test")
    print("=" * 60)

    if args.status:
        checkpoint = load_checkpoint()
        if checkpoint:
            print("\nCurrent Checkpoint:")
            print(json.dumps(checkpoint, indent=2))
        else:
            print("\nNo checkpoint found.")
        return

    if args.resume:
        # Resume from checkpoint
        checkpoint = load_checkpoint()
        if not checkpoint:
            print("Error: No checkpoint found to resume from.")
            sys.exit(1)

        if checkpoint["flow_id"] != args.resume:
            print(f"Error: Checkpoint flow_id ({checkpoint['flow_id']}) doesn't match requested ({args.resume})")
            sys.exit(1)

        print(f"\nResuming workflow: {args.resume}")
        print(f"Last checkpoint: {checkpoint['state']['last_checkpoint']}")
        print(f"Current phase: {checkpoint['state']['current_phase']}")

        # Restore state
        flow = ResumableWorkflow()
        flow.state = LongRunningState(**checkpoint["state"])
        flow.state.interrupted = False

        print(f"\n[Resume] Continuing from phase {flow.state.current_phase}...")
        # Note: Full resume would require CrewAI's internal @persist mechanism
        result = flow.kickoff()

    elif args.start:
        # Start new workflow
        print("\nStarting new workflow...")
        print("Note: Press Ctrl+C during Phase 3 to test interruption recovery.\n")

        flow = ResumableWorkflow()
        try:
            result = flow.kickoff()
            print("\n" + "=" * 60)
            print("Result:")
            print("=" * 60)
            print(result)
        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("Workflow Interrupted!")
            print("=" * 60)
            print(f"Flow ID: {flow.state.flow_id}")
            print(f"To resume, run: python 08_durable_resume.py --resume {flow.state.flow_id}")
            sys.exit(0)

    else:
        # Default: show usage
        print("""
Usage:
  python 08_durable_resume.py --start    Start a new workflow
  python 08_durable_resume.py --resume <flow_id>   Resume an interrupted workflow
  python 08_durable_resume.py --status   Check current checkpoint

LangGraph Comparison:
- CrewAI: Flow state + manual checkpointing
- LangGraph: Checkpointer + thread_id

To test interruption and resume:
1. Run: python 08_durable_resume.py --start
2. Press Ctrl+C during Phase 3
3. Run: python 08_durable_resume.py --resume <flow_id>
""")


if __name__ == "__main__":
    main()
