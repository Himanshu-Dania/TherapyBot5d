import pickle
from transformers import pipeline
# import faiss
import time
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import asyncio
import os
import torch
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage


class Chatbot:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.emotion_model = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY1"),
        )
        self.history = []
        print("Initialised\n")

    async def emotion_detection(self, query):
        """
        Detects the emotion in the input query using the 'SamLowe/roberta-base-go_emotions' model.
        """
        print("Emotion\n")
        results = self.emotion_model(query, top_k=3)

        return json.dumps(results)

    async def gemini(self, query):
        """
        Call LLM with the constructed prompt and return output with streaming.

        Args:
            self: The class instance (accessing other methods)
            query: The user's input query

        Returns:
            A string representing the LLM response with streaming.
        """

        emotion_task = self.emotion_detection(query)

        emotion_result = await asyncio.gather(emotion_task)

        prompt = f"""
        You are a highly empathetic and skilled mental health assistant, trained to provide thoughtful and personalized support. Analyze the user's query and craft a compassionate, actionable response using the following inputs:

        **Chat History:** "{[msg['parts'] for msg in self.history[-15:]]}"
        **User Input Query:** "{query}"

        **Detected Emotion:** {emotion_result}  
        (*This represents the user's emotional state.*)

        Figure out the specific mental health problem or concern the user might be facing (e.g., depression, anxiety, loneliness, self-esteem issues, identity crisis, etc.).
        
        Use one of the following Therapy Strategies to help the user. You can choose the most suitable strategy based on the user's query and emotional state or use a mix of multiple strategies.
        Questioning to make them open up: Asking open-ended questions to help the user express themselves.
        Restatement or Paraphrasing: Rephrasing the user’s statements to ensure understanding and validation.
        Reflection of feelings: Mirroring the user’s emotions to show empathy and understanding.
        Self-disclosure: Sharing relevant personal experiences to build rapport and provide perspective.
        Affirmation and Reassurance: Providing positive reinforcement and comfort to instill hope.
        Providing Suggestions: Offering actionable advice or steps to address their issues.
        Cognitive Restructuring: Helping the user identify and reframe negative thought patterns.
        Psychoeducation: Educating the user about their mental health concerns to foster understanding.
        Mindfulness and Grounding Techniques: Guiding the user to focus on the present moment to manage overwhelming emotions.
        Encouraging Self-Compassion: Helping the user be kinder to themselves in difficult situations.
        Problem-Solving Therapy: Identifying practical solutions to specific problems.
        Gratitude Focus: Encouraging the user to identify and focus on positive aspects of their life.
        
        Do not disclose this information to the user. Only use this to answer the user's question.
        **Contextual Information:**  
        - Assume the user seeks comfort, guidance, and actionable steps to address their concerns.  
        - Ensure your tone is empathetic, understanding, and reassuring.  
        - Keep your response clear and concise, avoiding jargon but providing meaningful advice.

        ### **Your Task:**  
        Based on the information provided, craft a response that:  
        1. Acknowledges the user's emotions and validates their feelings.  
        2. Addresses the identified problem in a thoughtful manner.  
        3. Implements the suggested therapy strategy effectively.  
        4. Offers actionable advice or support to guide the user.  
        5. Keep the language non-repetitive and engaging.
        6. Explore user's feelings slowly. Let them approach situations at their own pace.
        7. If you're asking questions, keep it to a minimum.
        
        Now, based on the information above, generate a response that fulfills the user's emotional and mental health needs.
        """

        print("Processing with LLM...")

        self.history.append({"role": "user", "parts": {"text": query}})

        try:
            async for token in self.llm.astream(prompt):
                yield token.content  # Yield each token's content as it is generated
                # print(token.content, end="", flush=True)
        except Exception as e:
            yield f"Error: {str(e)}"


async def __main__():
    model = Chatbot()
    while True:
        query = input(">> User: ")
        if query == "exit":
            break
        print(">> Pet: ")
        async for response in model.gemini(query):
            print(f"{response}", end="")


if __name__ == "__main__":
    asyncio.run(__main__())
