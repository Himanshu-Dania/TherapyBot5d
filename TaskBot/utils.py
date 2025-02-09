from pydantic import BaseModel, Field
import json
from typing import List, Union

class Task(BaseModel):
    task_name: str = Field(..., description="A short and descriptive name for the task.")
    task_type: str = Field(..., description="Type of task: 'discrete', 'slider', or 'checkmark'.")
    reason_for_task_creation: str = Field(..., description="A reason or message explaining why this task is being created.")
    description: str = Field(..., description="A detailed description of the task.")
    completed: Union[int, float, bool] = Field(
        ...,
        description="Indicates the completed status of the task (e.g., '0', '50', '100' for percentage, or 'True/False')."
    )
    total_count: Union[int, None] = Field(
        None, 
        description="Number of times to be completed (e.g., 0 out of 5) if task is of discrete type."
    )
    difficulty: str = Field(..., description="Difficulty level of the task (e.g., 'easy', 'medium', 'hard')."),
    recurring: int = Field(0, description="Number of hours before the task is repeated.")

class TaskSchema(BaseModel):
    task: List[Task] = Field(..., description="A list of tasks to be completed.")
    
def json_task(task_name, task_type, reason, difficulty="easy", completed=None, recurring=0, total_count=None):
    if completed is None:
        completed = 0 if task_type != "checkmark"  else False
    
    return Task(
        task_name=task_name, 
        task_type=task_type, 
        reason_for_task_creation=reason,
        completed=completed,
        total_count=total_count,
        difficulty=difficulty, 
        recurring=0
    )

if __name__=="__main__":
    checkmark_task = json_task(
        task_name="Morning Gratitude", 
        task_type="checkmark", 
        reason="To express gratitude each morning", 
        completed=True, 
        difficulty="easy", 
        recurring=0
    )

    count_task = json_task(
        task_name="Exercise Routine", 
        task_type="discrete", 
        reason="Daily exercise to maintain health", 
        completed=3, 
        total_count=10, 
        difficulty="medium", 
        recurring=24
    )

    # Create a TaskSchema with the tasks
    task_schema = TaskSchema(
        user_name="John Doe",
        description="Daily tasks for John",
        task=[checkmark_task, count_task]
    )

    # Print the TaskSchema to check its structure
    print(task_schema.model_dump_json(indent=2))