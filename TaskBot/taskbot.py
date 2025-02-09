# import mongodb
import time
import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
from typing import List
from utils import Task, TaskSchema

global load_balancer
load_balancer = 0
load_balancer_lock = asyncio.Lock()

class Taskbot:
    def __init__(self):
        i=1
        self.llms=[]
        while True:
            key=os.getenv(f"GOOGLE_API_KEY{i}")
            if key is None:
                break
            self.llms.append(ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-8b",
                api_key=key
            ))
            i+=1
        
        print(f"Initialised Taskbot with {i}\n")

    async def gemini(self, reason, tasks: List[Task]):
        global load_balancer
        query = json.dumps(f"""
            "reason_for_task_creation": {reason},
            "existing_tasks": {tasks}
        """)

        prompt = f"""
        You are an intelligent assistant designed to create personalized therapy tasks for users. You receive the following information in JSON format:

        {{
            "reason_for_task_creation": "A reason or message explaining why this task is being created.",
            "existing_tasks": [[
                {{
                    "task_name": "The name of the existing task.",
                    "task_type": "The type of the task (e.g., 'discrete', 'slider', 'checkmark').",
                    "completed": "The current progress of the task (e.g., 0, 5 for discrete tasks and 23, 50, 100 for slider tasks and true, false for checkmark tasks)."
                    "total_count": "Number of counts to be completed to finish the task if it's a discrete task.",
                    "difficulty": "The difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
                    "recurring": "Number of hours before the task is repeated. e.g. 0 by default."
                }}
            ]]
        }}

        Your task is to:
        - Create a new task for the user, avoiding redundancy with existing tasks (e.g., tasks with the same name or purpose).
        - Gradually increase the difficulty level based on the user's progress and completed tasks (e.g., if the user has completed several tasks successfully, increase the challenge).
        - Ensure the task is tailored to the reason for task creation and aligns with the user's goals.
        - Output the task in JSON format following the updated schema.

        The output should be a task or a list of tasks in JSON format.
        Here are a few examples of how the output should look:

        Example 1:
        "task": [{{
            "task_name": "Talk to 5 people",
            "task_type": "discrete",
            "total_count": 5,
            difficulty: "medium",
            "completed": 2,
            "task_reason": "Reduce fear of social interactions."
        }}]
        
        Example 2:
        "task": [{{
            "task_name": "Morning Gratitude Check-in",
            "task_type": "checkmark",
            "difficulty": "easy",
            "completed": false,
            "task_reason": "To encourage the user to start the day with positive thoughts."
        }},
        {{
            "task_name": "Complete a 5-minute mindfulness exercise",
            "task_type": "checkmark",
            "completed": false,
            "difficulty": "easy",
            "recurring": 24,
            "task_reason": "To help the user focus and relax through mindfulness."
        }}]


        Generate tasks based on the inputs provided. Make the tasks engaging, personalized, and aligned with the therapy goals.

        Input Query:
        {query}
        """
        
        print("Processing with LLM...")
        attempts = len(self.llms)  # Max retries = number of available LLMs
        for _ in range(attempts):  # Try each LLM once
            async with load_balancer_lock:  # Lock to prevent race conditions
                assigned_index = load_balancer  # Assign current LLM index
                load_balancer = (load_balancer + 1) % len(self.llms)  # Move to next LLM

            print(f"Trying LLM index: {assigned_index}")
            try:
                result = await self.llms[assigned_index].ainvoke(prompt)  # Call LLM
                return result.content  # If success, return response
            except Exception as e:
                print(f"LLM index {assigned_index} failed with error: {str(e)}")  # Log error and retry

        return "Error: All LLMs failed to process the request."  # If all fail, return an error message


async def __main__():
    model = Taskbot()
    result, result2, result3 = await asyncio.gather(
        model.gemini("To help User get used to rejections and failures.", []),
        model.gemini("To reduce stress and anxiety", []),
        model.gemini("To help User build a daily mindfulness habit.", []),
        # model.gemini("To help User get used to rejections and failures.", []),
        # model.gemini("To reduce stress and anxiety", []),
        # model.gemini("To help User build a daily mindfulness habit.", []),
        # model.gemini("To help User get used to rejections and failures.", []),
        # model.gemini("To reduce stress and anxiety", []),
        # model.gemini("To help User build a daily mindfulness habit.", [])
    )

    # Print results
    print("Result 1:", result.strip())
    print("Result 2:", result2.strip())
    print("Result 3:", result3.strip())


if __name__ == "__main__":
    asyncio.run(__main__())
