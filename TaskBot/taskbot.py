# import mongodb
import time
import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
from typing import List
from utils import Task, Journey, JourneySchema, json_task
from langchain_core.prompts import PromptTemplate

global load_balancer
load_balancer = 0
load_balancer_lock = asyncio.Lock()


class Taskbot:
    def __init__(self):
        i = 1
        self.llms = []
        while True:
            key = os.getenv(f"GOOGLE_API_KEY{i}")
            if key is None:
                break
            self.llms.append(
                ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", api_key=key)
            )
            i += 1

        print(f"Initialised Taskbot with {len(self.llms)} LLM(s)\n")

        self.create_task_prompt = PromptTemplate(
            input_variables=["reason", "tasks_json"],
            template="""
You are an intelligent assistant designed to create personalized therapy tasks for users. You receive the following information in JSON format:
```json
{{
    "reason_for_task_creation": "A reason or message explaining why this task is being created.",
    "existing_tasks": [
        {{
            "task_name": "The name of the existing task.",
            "task_type": "The type of the task (e.g., 'discrete', 'slider', 'checkmark').",
            "reason_for_task_creation": "The reason or message explaining why the task was created.",
            "description": "A detailed description of the task.",
            "completed": "The current progress of the task (e.g., 0, 5 for discrete tasks; numeric for slider tasks; true/false for checkmark tasks).",
            "total_count": "Number of counts to be completed to finish the task if it's a discrete task.",
            "difficulty": "The difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
            "recurring": "Number of hours before the task is repeated, e.g., 0 by default."
        }}
    ]
}}
```

Your task is to:
- Create a new task for the user, avoiding redundancy with existing tasks (e.g., tasks with the same name or purpose).
- Gradually increase the difficulty level based on the user's progress and completed tasks.
- Ensure the task is tailored to the reason for task creation and aligns with the user's goals.
- Output the task in JSON format following the updated schema.

The output should be a task or a list of tasks in JSON format.

Here are a few examples of how the output should look:

Example 1:
```json
{{
    "task": [{{
        "task_name": "Talk to 5 people",
        "task_type": "discrete",
        "total_count": 5,
        "completed": 2,
        "difficulty": "medium",
        "recurring": 0,
        "reason_for_task_creation": "Reduce fear of social interactions.",
        "description": "Talk to 5 people to overcome social anxiety."
    }}]
}}
```
Example 2:
```json
{{
    "task": [{{
        "task_name": "Morning Gratitude Check-in",
        "task_type": "checkmark",
        "difficulty": "easy",
        "completed": false,
        "recurring": 0,
        "reason_for_task_creation": "To encourage the user to start the day with positive thoughts.",
        "description": "Mark your morning gratitude as complete."
    }},{{
        "task_name": "Complete a 5-minute mindfulness exercise",
        "task_type": "checkmark",
        "completed": false,
        "difficulty": "easy",
        "recurring": 24,
        "reason_for_task_creation": "To help the user focus and relax through mindfulness.",
        "description": "Do a 5-minute mindfulness exercise."
    }}]
}}
```

Generate tasks based on the inputs provided. Make the tasks engaging, personalized, and aligned with the therapy goals.

**Input Data:**
```json
{{
    "reason_for_task_creation": "{reason}",
    "existing_tasks": {tasks_json}
}}
```
        """,
        )

        self.journey_prompt_template = PromptTemplate(
            input_variables=["new_task", "journeys_json"],
            template="""
You are an intelligent assistant designed to manage and organize therapy journeys.

You will receive:
- A **new task** in JSON format
- A list of **existing journeys**, each containing:
    - `journey_name`
    - `description`
    - `tasks`
    - `difficulty`
    

Your task:
1. **Determine if the new task fits into an existing journey**:
    - Match based on similar themes, difficulty.
    - Avoid overloading a single journey.

2. **If the task does not fit, create a new journey**:
    - Generate a meaningful `journey_name` and `description`.
    - Ensure the difficulty aligns with the task.

**Output either a new journey's name or an already present journey's name.**

Example:
Input:
```json
{{
    "new_task": [{{
        "task_name": "Rejection Exposure",
        "task_type": "checkmark",
        "reason_for_task_creation": "To help get used to rejections and failures.",
        "description": "Every day, ask for a discount at a store.",
        "difficulty": "medium",
        "completed": false,
        "recurring": 24
    }}, 
    {{
        "task_name": "Face Your Fears",
        "task_type": "discrete",
        "reason_for_task_creation": "To help overcome fears.",
        "description": "Face a fear every day.",
        "difficulty": "hard",
        "completed": 0,
        total_count: 2,
        "recurring": 24
    }}],
    "existing_journeys": [{{
        "journey_name": "Mindfulness Journey",
        "description": "A collection of tasks aimed at promoting mindfulness and reducing stress.",
        "tasks": [{{
                "task_name": "Morning Meditation",
                "description": "Meditate for 10 minutes every morning",
            }},
            {{
                "task_name": "Evening Reflection",
                "description": "Reflect on your day for 5 minutes before bed."   
        }}],
        "difficulty": "easy"
    }},
    {{
        "journey_name": "Fitness Journey",
        "description": "Tasks related to physical exercises and improving strength.",
        "tasks": [{{
                "task_name": "Daily Push-ups",
                "description": "Do 20 push-ups daily",
            }},
            {{
                "task_name": "Weekly Jogging",
                "description": "Jog for 30 minutes every weekend."
        }}],
        "difficulty": "medium"
    }}]
}}
```

Output:
Winning against Rejections and Fears
```

**Input Data:**
```json
{{
    "new_task": {new_task},
    "existing_journeys": {journeys_json}
}}
```
Ouput:
""",
        )

        self.task_difficulty_prompt = PromptTemplate(
            input_variables=["task", "reason"],
            template="""
You are an intelligent assistant designed to help curate personalized therapy tasks for users. 
Your task is to change the difficulty of the task according to a user given reason.
You receive the following information in JSON format:
```json
{{
    "reason": "A reason or message explaining why the difficulty of the task should be changed.",
    "task": {{
        "task_name": "The name of the task.",
        "task_type": "The type of the task (e.g., 'discrete', 'slider', 'checkmark').",
        "reason_for_task_creation": "The reason or message explaining why the task was created.",
        "description": "A detailed description of the task.",
        "completed": "The current progress of the task (e.g., 0, 5 for discrete tasks; numeric for slider tasks; true/false for checkmark tasks).",
        "total_count": "Number of counts to be completed to finish the task if it's a discrete task.",
        "difficulty": "The difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
        "recurring": "Number of hours before the task is repeated, e.g., 0 by default."
    }}
}}

Your task is to:
- Change the difficulty of the task based on the reason provided.
- Output the updated task in JSON format.
- You can split the task into multiple tasks if needed. If there, output them in a list.

Input:
```json
{{
    "reason": "{reason}",
    "task": {task}
}}
```

Output:
""",
        )

    async def create_task(self, reason, tasks: List[Task]):
        global load_balancer
        tasks_json = json.dumps(
            [task.model_dump() for task in tasks], ensure_ascii=False, indent=2
        )
        print(f"tasks_json: {tasks_json}\nReason: {reason}")
        attempts = len(self.llms)  # Number of retries = number of available LLMs
        for _ in range(attempts):
            async with load_balancer_lock:
                assigned_index = load_balancer
                load_balancer = (load_balancer + 1) % len(self.llms)

            try:
                llm_chain = self.create_task_prompt | self.llms[assigned_index]
                result = llm_chain.invoke(
                    input={"reason": reason, "tasks_json": tasks_json}
                )
                # print(f"Result: {result}")
                return result.content.strip()
            except Exception as e:
                print(f"LLM index {assigned_index} failed: {str(e)}")

        return "Error: All LLMs failed to process the request."

    async def process_task_into_journey(self, new_task: Task, journeys: List[Journey]):
        global load_balancer
        tasks_json = json.dumps(new_task.model_dump(), ensure_ascii=False, indent=2)
        journeys_json = json.dumps(
            [j.model_dump() for j in journeys], ensure_ascii=False, indent=2
        )

        # print("new task: ")
        # print(new_task)

        # print("journeys: ")
        # print(journeys)

        attempts = len(self.llms)  # Number of retries = number of available LLMs
        for _ in range(attempts):
            async with load_balancer_lock:
                assigned_index = load_balancer
                load_balancer = (load_balancer + 1) % len(self.llms)

            try:
                llm_chain = self.journey_prompt_template | self.llms[assigned_index]
                result = llm_chain.invoke(
                    input={"new_task": tasks_json, "journeys_json": journeys_json}
                )
                return result.content.strip()
            except Exception as e:
                print(f"LLM index {assigned_index} failed: {str(e)}")
        return "Error: Unable to process journey update."

    async def change_task_difficulty(self, reason, task: Task):
        global load_balancer
        task_json = json.dumps(task.model_dump(), ensure_ascii=False, indent=2)
        attempts = len(self.llms)  # Number of retries = number of available LLMs
        for _ in range(attempts):
            async with load_balancer_lock:
                assigned_index = load_balancer
                load_balancer = (load_balancer + 1) % len(self.llms)

            try:
                llm_chain = self.task_difficulty_prompt | self.llms[assigned_index]
                result = llm_chain.invoke(input={"reason": reason, "task": task_json})
                return result.content.strip()
            except Exception as e:
                print(f"LLM index {assigned_index} failed: {str(e)}")
        return "Error: Unable to change task difficulty."


async def __main__():
    model = Taskbot()
    tasks = [
        json_task(
            task_name="Morning Gratitude",
            task_type="checkmark",
            reason="Alice needs to reaffirm their love for themself",
            description="Mark your morning gratitude as complete",
            difficulty="easy",
            completed=True,
        ),
        json_task(
            task_name="Meditation for 10 minutes",
            task_type="slider",
            reason="Alice struggles with overthinking",
            description="Meditate for at least 10 minutes",
            completed=30,
            difficulty="easy",
        ),
    ]
    result = await model.create_task(
        "To help User get used to rejections and failures.", tasks
    )
    print("Result 1:", result)


if __name__ == "__main__":
    asyncio.run(__main__())
