# import mongodb
import time
import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
from typing import List
from utils import Task, TaskSchema
from langchain_core.prompts import PromptTemplate
from utils import json_task
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
        
        self.prompt_template = PromptTemplate(
            input_variables=["reason", "tasks_json"],
            template="""
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

        **Input Data:**
            {{
                "reason_for_task_creation": "{reason}",
                "existing_tasks": {tasks_json}
            }}
        """)

    async def gemini(self, reason, tasks: List[Task]):
        global load_balancer
        tasks_json = json.dumps([task.model_dump() for task in tasks], ensure_ascii=False, indent=2)
        # json.dumps([task.model_dump_json(indent=2) for task in tasks], indent=2)
        print(f"tasks_json: {tasks_json}\nReason: {reason}")
        print(type(tasks_json))
        attempts = len(self.llms)  # Number of retries = number of available LLMs
        for _ in range(attempts):  
            async with load_balancer_lock:  
                assigned_index = load_balancer  
                load_balancer = (load_balancer + 1) % len(self.llms)  

            try:
                llm_chain = self.prompt_template | self.llms[assigned_index]

                result = llm_chain.invoke(input={"reason": reason, "tasks_json": tasks_json})
                print(f"Result: {result}")
                return result.content.strip()  
            except Exception as e:
                print(f"LLM index {assigned_index} failed: {str(e)}")  

        return "Error: All LLMs failed to process the request."

async def __main__():
    model = Taskbot()
    tasks = [
        json_task("Morning Gratitude", "checkmark", reason="Alice needs to reaffirm their love for themself",difficulty="easy", completed=True),
        json_task("Meditation for 10 minutes", "slider", reason="Alice struggles with overthinking", completed=30, difficulty="easy")
    ]
    result = await model.gemini("To help User get used to rejections and failures.", tasks)
        # model.gemini("To reduce stress and anxiety", []),
        # model.gemini("To help User build a daily mindfulness habit.", []),
        # model.gemini("To help User get used to rejections and failures.", []),
        # model.gemini("To reduce stress and anxiety", []),
        # model.gemini("To help User build a daily mindfulness habit.", []),
        # model.gemini("To help User get used to rejections and failures.", []),
        # model.gemini("To reduce stress and anxiety", []),
        # model.gemini("To help User build a daily mindfulness habit.", [])
    

    # Print results
    print("Result 1:", result)
    # print("Result 2:", result2.strip())
    # print("Result 3:", result3.strip())


if __name__ == "__main__":
    asyncio.run(__main__())
