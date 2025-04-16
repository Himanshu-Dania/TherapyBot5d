import pickle
from transformers import pipeline

# import faiss
import time
import numpy as np

# from transformers import AutoTokenizer, AutoModelForCausalLM
import json

# from transformers import AutoTokenizer, AutoModelForSequenceClassification
import asyncio
import torch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain_core.prompts import PromptTemplate
import sys
import os

# Points to the parent directory containing EmotionBot, StrategyBot, TherapyBot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Now you can import directly
from TherapyBot.prompts import chat_prompt
from EmotionBot.bot import emotion_detection
from StrategyBot.bot import predict_therapy_strategy


class Chatbot:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY1"),
        )
        self.prompt = chat_prompt
        self.chain = self.prompt | self.llm
        self.history = []

        print("Initialised\n")

    async def gemini(self, query):
        """
        Call LLM with the constructed prompt and return output with streaming.

        Args:
            self: The class instance (accessing other methods)
            query: The user's input query

        Returns:
            A string representing the LLM response with streaming.
        """

        emotion_result = emotion_detection(query)

        self.history.append({"role": "usr", "content": query})
        strategy_result = predict_therapy_strategy(self.history[-8:])
        emotion_result, strategy_result = await asyncio.gather(
            emotion_result, strategy_result
        )

        (reasoning, strategy_list) = strategy_result

        print("Processing with LLM...")

        history_summary = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in self.history[-8:]]
        )

        print(
            f"Emotion: {emotion_result}\n\nStrategy: {reasoning}\n\n{strategy_list}\n\n"
        )
        # print("History Summary: ", self.history[-8:])
        response_text = ""
        try:
            async for token in self.chain.astream(
                {
                    "query": query,
                    "emotion_result": emotion_result,
                    "history": history_summary,
                    "reasoning_for_strategy": reasoning,
                    "strategy_result": strategy_list,
                }
            ):  # Stream the response tokens
                yield token.content  # Yield each token's content as it is generated
                response_text += token.content

            self.history[-1].update({"emotion": emotion_result})
            self.history.append(
                {
                    "role": "sys",
                    "strategy": strategy_list,
                    "content": response_text,
                }
            )  # Store chatbot response
            # print(self.history)
        except Exception as e:
            yield f"Error: {str(e)}"


async def __main__():
    model = Chatbot()
    while True:
        query = input("\n>> User: ")
        if query == "exit":
            break
        print(">> Pet: ")
        async for response in model.gemini(query):
            print(f"{response}", end="")


if __name__ == "__main__":
    asyncio.run(__main__())
