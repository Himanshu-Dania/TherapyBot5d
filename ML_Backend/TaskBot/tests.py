import asyncio
import json
import sys
import os

# Points to the parent directory containing EmotionBot, StrategyBot, TherapyBot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from TaskBot.utils import json_task, Task, Journey
from TaskBot.bot import Taskbot


async def test_create_task():
    print("\n===== Testing Task Creation =====")

    taskbot = Taskbot()

    # Scenario 1: No existing tasks
    print("\n--- Test: No Existing Tasks ---")
    reason_1 = "To reduce negative thoughts about self"
    tasks_1 = []
    result_1 = await taskbot.create_task(reason_1, tasks_1)
    print("Result:", result_1)

    # Scenario 2: Existing tasks already present
    print("\n--- Test: Some Existing Tasks ---")
    reason_2 = "User struggles with negative thoughts about their physical health"
    tasks_2 = [
        json_task(
            "Daily Gratitude",
            "checkmark",
            reason_2,
            "Write 3 things you’re grateful for",
            "easy",
            completed=False,
        ),
        json_task(
            "Morning Walk",
            "discrete",
            reason_2,
            "Walk for 30 minutes every morning",
            "medium",
            completed=2,
            total_count=10,
        ),
    ]
    result_2 = await taskbot.create_task(reason_2, tasks_2)
    print("Result:", result_2)


async def test_process_task_into_journey():
    print("\n===== Testing Journey Processing =====")

    journey_bot = Taskbot()

    # Scenario 1: New task should fit into an existing journey
    print("\n--- Test: Task Fits Into Existing Journey ---")
    new_task_1 = json_task(
        "Deep Breathing",
        "checkmark",
        "To reduce stress",
        "Breathe deeply for 5 minutes",
        "easy",
        completed=False,
    )
    existing_journeys_1 = [
        Journey(
            journey_name="Mindfulness Journey",
            description="Tasks for mental calmness",
            task=[
                json_task(
                    "Morning Meditation",
                    "slider",
                    "To develop mindfulness",
                    "Meditate for 10 minutes",
                    "easy",
                    completed=10,
                )
            ],
            difficulty="easy",
        )
    ]
    result_1 = await journey_bot.process_task_into_journey(
        new_task_1, existing_journeys_1
    )
    print("Result:", result_1)

    # Scenario 2: Task does not match any existing journey, so a new journey should be created
    print("\n--- Test: Task Requires a New Journey ---")

    new_task_2 = json_task(
        "Weight Lifting",
        "slider",
        "To build muscle",
        "Lift weights for 30 minutes",
        "hard",
        completed=0,
    )
    existing_journeys_2 = [
        Journey(
            journey_name="Mindfulness Journey",
            description="Tasks for mental calmness",
            task=[
                json_task(
                    "Morning Meditation",
                    "slider",
                    "To develop mindfulness",
                    "Meditate for 10 minutes",
                    "easy",
                    completed=10,
                )
            ],
            difficulty="easy",
        )
    ]
    result_2 = await journey_bot.process_task_into_journey(
        new_task_2, existing_journeys_2
    )
    print("Result:", result_2)


async def test_change_task_difficulty():
    print("\n===== Testing Task Difficulty Change =====")

    journey_bot = Taskbot()

    # Scenario 1: Change the difficulty of an existing task
    print("\n--- Test: Change Task Difficulty ---")
    task_1 = json_task(
        "Morning Walk",
        "discrete",
        "User struggles with negative thoughts about their physical health",
        "Walk for 30 minutes every morning",
        "medium",
        completed=2,
        total_count=10,
    )
    print(task_1)
    reason = " It isn't really helping me. The lonelier I am, the more it sucks"
    result_1 = await journey_bot.change_task_difficulty(reason, task_1)
    print("Result:", result_1)

    # Scenario 2: Too difficult to complete, change to an easier difficulty
    print("\n--- Test: Task is Too Difficult ---")
    task_2 = json_task(
        "Face rejections",
        "discrete",
        "To build resilience",
        "Face rejections 5 times",
        "hard",
        completed=2,
        total_count=5,
    )
    reason = "It's too hard for me to face rejections"
    result_2 = await journey_bot.change_task_difficulty(reason, task_2)
    print("Result:", result_2)


async def run_tests():
    # await test_create_task()
    # await test_process_task_into_journey()
    await test_change_task_difficulty()


if __name__ == "__main__":
    asyncio.run(run_tests())
