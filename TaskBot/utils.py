from pydantic import BaseModel, Field
import json
from typing import List, Union


class Task(BaseModel):
    task_name: str = Field(
        ..., description="A short and descriptive name for the task."
    )
    task_type: str = Field(
        ..., description="Type of task: 'discrete', 'slider', or 'checkmark'."
    )
    reason_for_task_creation: str = Field(
        ...,
        description="A reason or message explaining why this task is being created.",
    )
    description: str = Field(..., description="A detailed description of the task.")
    difficulty: str = Field(
        "easy",
        description="Difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
    )
    recurring: int = Field(
        0, description="Number of hours before the task is repeated."
    )


class DiscreteTask(Task):
    task_type: str = "discrete"
    total_count: int = Field(
        ..., description="Total number of times the task should be completed."
    )
    completed: int = Field(
        0, description="Number of times the task has been completed."
    )


class SliderTask(Task):
    task_type: str = "slider"
    completed: float = Field(
        0.0, description="Number of times the task has been completed."
    )


class CheckmarkTask(Task):
    task_type: str = "checkmark"
    completed: bool = Field(False, description="Whether the task has been completed.")


class Journey(BaseModel):
    journey_name: str = Field(
        ..., description="A short and descriptive name for the journey."
    )
    description: str = Field(..., description="A detailed description of the journey.")
    task: List[Union[CheckmarkTask, SliderTask, DiscreteTask]] = Field(
        ..., description="A list of tasks to be completed."
    )
    difficulty: str = Field(
        ...,
        description="Difficulty level of the journey (e.g., 'easy', 'medium', 'hard').",
    )


class JourneySchema(BaseModel):
    journeys: List[Journey] = Field(
        ..., description="A list of journeys to be completed."
    )


def json_task(
    task_name,
    task_type,
    reason,
    description=None,  # Added description parameter
    difficulty="easy",
    completed=None,
    recurring=0,
    total_count=None,
):
    if description is None:
        # Defaulting description to a combination of task_name and reason
        description = f"Task '{task_name}' - {reason}"
    if completed is None:
        completed = 0 if task_type != "checkmark" else False
    if task_type == "checkmark":
        return CheckmarkTask(
            task_name=task_name,
            task_type=task_type,
            reason_for_task_creation=reason,
            description=description,
            completed=completed,
            difficulty=difficulty,
            recurring=recurring,
        )
    if task_type == "discrete":
        return DiscreteTask(
            task_name=task_name,
            task_type=task_type,
            reason_for_task_creation=reason,
            description=description,
            completed=completed,
            total_count=total_count,
            difficulty=difficulty,
            recurring=recurring,
        )
    if task_type == "slider":
        return SliderTask(
            task_name=task_name,
            task_type=task_type,
            reason_for_task_creation=reason,
            description=description,
            completed=completed,
            difficulty=difficulty,
            recurring=recurring,
        )


if __name__ == "__main__":
    checkmark_task = json_task(
        task_name="Morning Gratitude",
        task_type="checkmark",
        reason="To express gratitude each morning",
        description="Mark your morning gratitude as complete",
        completed=True,
        difficulty="easy",
        recurring=0,
    )

    count_task = json_task(
        task_name="Exercise Routine",
        task_type="discrete",
        reason="Daily exercise to maintain health",
        description="Complete the exercise routine a total of 10 times",
        completed=3,
        total_count=10,
        difficulty="medium",
        recurring=24,
    )

    slider_task = json_task(
        task_name="Meditation for 10 minutes",
        task_type="slider",
        reason="Alice struggles with overthinking",
        description="Meditate for at least 10 minutes",
        completed=30,
        difficulty="easy",
    )
    print(
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
    )
    # Create a journey with the tasks
    journey = Journey(
        journey_name="Daily Routines for mental health and well-being improvement",
        description="A journey to improve mental health and well-being through daily routines.",
        task=[checkmark_task, count_task, slider_task],
        difficulty="medium",
    )

    journey2 = Journey(
        journey_name="YZ",
        description="A journey to improve mental health and well-being through daily routines.",
        task=[checkmark_task],
        difficulty="easy",
    )

    journey_schema = JourneySchema(journeys=[journey2, journey])
    # Print the TaskSchema to check its structure
    print(journey_schema.model_dump_json(indent=2))
