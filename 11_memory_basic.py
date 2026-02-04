"""
11_memory_basic.py - Basic Memory Functionality

Purpose: Verify CrewAI's memory feature
- What gets saved with memory=True
- Behavior of short-term memory
- Memory within the same session

LangGraph Comparison:
- LangGraph: Explicit memory management in State
- CrewAI: Automatic memory enablement with memory=True
"""

from crewai import Agent, Task, Crew


def main():
    print("=" * 60)
    print("Memory: Basic Memory Test")
    print("=" * 60)
    print("""
This example demonstrates CrewAI's memory feature.
When memory=True, agents can remember information across tasks.

Memory Types in CrewAI:
1. Short-term Memory: Within the same crew execution
2. Long-term Memory: Persists across executions
3. Entity Memory: Remembers information about entities

LangGraph Comparison:
- CrewAI: memory=True (automatic)
- LangGraph: Explicit state management in graph
""")

    # ==========================================================================
    # Agent with memory enabled
    # ==========================================================================
    assistant = Agent(
        role="Research Assistant",
        goal="Help users by researching and remembering information",
        backstory="""You are a helpful research assistant with excellent
        memory. You remember details from previous interactions and use
        them to provide better assistance.""",
        verbose=True,
        memory=True,  # Enable agent-level memory
    )

    # ==========================================================================
    # Tasks that build on each other
    # ==========================================================================

    # Task 1: Learn information
    learn_task = Task(
        description="""Learn and memorize the following information about Project Alpha:
        - Project Code: ALPHA-2024
        - Budget: $2.5 million
        - Team Lead: Dr. Sarah Chen
        - Start Date: January 2024
        - Primary Goal: Develop an AI-powered analytics platform

        Confirm that you have memorized this information.""",
        expected_output="Confirmation that the information has been memorized",
        agent=assistant,
    )

    # Task 2: Recall information (tests short-term memory)
    recall_task = Task(
        description="""Without being given the information again, answer
        these questions about Project Alpha:
        1. What is the project code?
        2. Who is the team lead?
        3. What is the budget?

        This tests your short-term memory from the previous task.""",
        expected_output="Answers to all three questions from memory",
        agent=assistant,
    )

    # Task 3: Apply remembered information
    apply_task = Task(
        description="""Using your memory of Project Alpha, create a brief
        project summary email that could be sent to stakeholders.
        Include all the key details you remember.""",
        expected_output="A professional email summarizing Project Alpha",
        agent=assistant,
    )

    # ==========================================================================
    # Crew with memory enabled
    # ==========================================================================
    crew = Crew(
        agents=[assistant],
        tasks=[learn_task, recall_task, apply_task],
        verbose=True,
        memory=True,  # Enable crew-level memory
        # embedder configuration can be customized:
        # embedder={
        #     "provider": "openai",
        #     "config": {"model": "text-embedding-3-small"}
        # }
    )

    print("\n" + "=" * 60)
    print("Executing Memory Test (3 Tasks)")
    print("=" * 60)
    print("""
Task Flow:
1. Learn: Agent memorizes project information
2. Recall: Agent answers questions from memory
3. Apply: Agent uses memory to create a document

Watch for memory usage in the agent's reasoning.
""")

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("Result:")
    print("=" * 60)
    print(result)

    # Show task outputs for detailed analysis
    if result.tasks_output:
        print("\n" + "=" * 60)
        print("Individual Task Outputs:")
        print("=" * 60)
        for i, task_output in enumerate(result.tasks_output):
            print(f"\nTask {i+1}:")
            print("-" * 40)
            print(task_output.raw[:500] if len(task_output.raw) > 500 else task_output.raw)


def test_multi_agent_memory():
    """Test memory sharing between multiple agents."""
    print("\n" + "=" * 60)
    print("Multi-Agent Memory Test")
    print("=" * 60)

    # Two agents that should share memory
    agent_a = Agent(
        role="Information Gatherer",
        goal="Gather and store information",
        backstory="You collect information and pass it to colleagues.",
        verbose=True,
        memory=True,
    )

    agent_b = Agent(
        role="Information Processor",
        goal="Process information gathered by others",
        backstory="You work with information collected by your colleagues.",
        verbose=True,
        memory=True,
    )

    task_gather = Task(
        description="""Record the following facts:
        - The secret code is 'OMEGA-777'
        - The meeting is at 3 PM
        - The contact person is John""",
        expected_output="Confirmation of recorded facts",
        agent=agent_a,
    )

    task_process = Task(
        description="""Based on the information gathered by your colleague,
        what is the secret code and when is the meeting?
        (Note: This tests if memory is shared between agents)""",
        expected_output="The secret code and meeting time",
        agent=agent_b,
    )

    crew = Crew(
        agents=[agent_a, agent_b],
        tasks=[task_gather, task_process],
        verbose=True,
        memory=True,
    )

    result = crew.kickoff()
    print("\nMulti-Agent Memory Result:")
    print(result)


if __name__ == "__main__":
    main()
    # Uncomment to test multi-agent memory:
    # test_multi_agent_memory()
