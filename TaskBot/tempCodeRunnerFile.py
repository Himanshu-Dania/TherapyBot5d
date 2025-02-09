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
    assert "hard" in response

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
