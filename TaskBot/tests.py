import pytest_asyncio
import pytest
import asyncio
from typing import List
# from taskbot import Task
from utils import json_task
from taskbot import Taskbot

model = Taskbot()

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
    
    
@pytest.mark.asyncio
async def test_empty_existing_tasks():
    reason = "To help Alice focus and relax through mindfulness."
    tasks = []  

    response=await model.gemini(reason, tasks)
    print(response)
    # return response
    assert "task_name" in response
    assert "task_type" in response
    assert "difficulty" in response
    assert "completed" in response

@pytest.mark.asyncio
async def test_existing_tasks_increasing_difficulty():
    reason = "To help Alice build a daily mindfulness habit."
    tasks = [
        json_task("Morning Gratitude", "checkmark", reason="Alice needs to reaffirm their love for themself",difficulty="easy", completed=True),
        json_task("Meditation for 10 minutes", "slider", reason="Alice struggles with overthinking", completed=30, difficulty="easy")
    ]
    response=await model.gemini(reason, tasks)
    print(response)
    assert "difficulty" in response
    assert "medium" in response

@pytest.mark.asyncio
async def test_task_avoidance_of_duplicates():
    reason = "To promote relaxation and reduce stress."
    tasks = [
        json_task("Breathing Exercise", "slider", reason="To reduce stress", difficulty="medium", completed=50),
        json_task("Breathing Exercise", "slider", reason="To reduce stress", difficulty="medium", completed=50)
    ]

    response = await model.gemini(reason, tasks)
    
    assert "task_name" in response
    assert "Breathing Exercise" not in response

@pytest.mark.asyncio
async def test_task_with_custom_reason():
    reason = "To encourage Alice to connect with nature."
    tasks = []

    response=await model.gemini(reason, tasks)
    print(response)
    assert "task_name" in response
    assert "nature" in response.lower()
    
    
@pytest.mark.asyncio
async def test_multiple_tasks_with_progress():
    reason = "To support Alice in achieving her fitness goals."
    tasks = [
        json_task("Morning Prayer", "slider", reason="", difficulty="easy", completed=30),
        json_task("Evening Yoga", "slider", reason="", difficulty="medium", completed=60)
    ]

    response=await model.gemini(reason, tasks)
    print(response)
    assert "task_name" in response
    assert "fitness" in response.lower()
