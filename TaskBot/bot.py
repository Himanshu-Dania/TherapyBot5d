# import mongodb
import time
import asyncio
import sys
import os

# Points to the parent directory containing EmotionBot, StrategyBot, TherapyBot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
from typing import List
from TaskBot.utils import Task, Journey, JourneySchema, json_task
from langchain_core.prompts import PromptTemplate
from TaskBot.prompts import (
    create_task_prompt,
    journey_prompt_template,
    task_difficulty_prompt,
)

global load_balancer
load_balancer = 0
load_balancer_lock = asyncio.Lock()


class Taskbot:
    def __init__(self):

        self.create_task_prompt = create_task_prompt
        self.journey_prompt_template = journey_prompt_template
        self.task_difficulty_prompt = task_difficulty_prompt

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

    async def create_task(self, reason, tasks: List[Task]):
        global load_balancer
        tasks_json = json.dumps(
            [task.model_dump() for task in tasks], ensure_ascii=False, indent=2
        )
        # print(f"tasks_json: {tasks_json}\nReason: {reason}")
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
