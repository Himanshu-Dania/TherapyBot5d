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
import google.generativeai as genai
import torch


class Chatbot:
    def __init__(self):
        # self.dialo = pickle.load(open(small_model_path, "rb"))
        # self.utility_tokenizer = AutoTokenizer.from_pretrained(
        #     "tiiuae/Falcon3-1B-Instruct"
        # )
        # self.utility_model = AutoModelForCausalLM.from_pretrained(
        #     "tiiuae/Falcon3-1B-Instruct"
        # )
        # self.rag = faiss.read_index(rag_path)
        self.gemini_flash = 1  # initialise api
        self.emotion_model = pipeline(
            "text-classification", model="roberta-base-go_emotions"
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # self.strategy_tokenizer = AutoTokenizer.from_pretrained(
        #     "heegyu/TinyLlama-augesc-context-strategy"
        # )
        # self.strategy_model = (
        #     AutoModelForSequenceClassification.from_pretrained(
        #         "heegyu/TinyLlama-augesc-context-strategy"
        #     )
        #     .eval()
        #     .to(self.device)
        # )
        ESCONV_STRATEGY = [
            "Question",
            "Restatement or Paraphrasing",
            "Reflection of feelings",
            "Self-disclosure",
            "Affirmation and Reassurance",
            "Providing Suggestions",
            "Information",
            "Others",
        ]
        self.strategy_id2label = {i: k for i, k in enumerate(ESCONV_STRATEGY)}
        genai.configure(api_key="AIzaSyCcI71tH5DeRYKfD7D0gDYgPpqfrE_VgS0")
        self.model = genai.GenerativeModel("gemini-1.5-flash-002")
        self.history = []
        print("Initialised\n")

    async def emotion_detection(self, query):
        """
        Detects the emotion in the input query using the 'SamLowe/roberta-base-go_emotions' model.
        """
        print("Emotion\n")
        results = self.emotion_model(query, top_k=3)

        return json.dumps(results)

    async def strategy_detection(self, query):
        prompt = f"""
        You are a compassionate and skilled mental health assistant. Your task is to analyze the user's query and identify the most effective therapy strategy to address their concerns. The therapy strategy should be selected from the following list:

        Therapy Strategies:
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
        
        Instructions:

        Understand the user's query, emotional state, and underlying concerns.
        Select the therapy strategy that would be the most beneficial for the user in this situation.
        Provide a justification for why this strategy is the most suitable based on the query.
        Response Format:
        Provide your output as a structured JSON object with the following keys:

        {{
            "strategy": "Chosen therapy strategy",
            "justification": "Brief explanation of why this strategy is appropriate"
        }}
        
        Example Query and Expected Output:

        Query:
        "I keep blaming myself for things going wrong in my life, and I feel like I'm never good enough."

        Response:

        {{
            "strategy": "Encouraging Self-Compassion",
            "justification": "The user is exhibiting self-blame and low self-esteem. Encouraging self-compassion can help them recognize their inherent worth and be kinder to themselves."
        }}
        
        User Query:
        {query}
        
        Response:
        """
        input_ids = self.utility_tokenizer.encode(prompt, return_tensors="pt")

        # Generate a response
        output = self.utility_model.generate(
            input_ids,
            max_new_tokens=50,
            num_return_sequences=1,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            num_beams=5,
        )
        response = self.utility_tokenizer.decode(output[0], skip_special_tokens=True)
        return response

    # TBD
    async def problem_detection(self, query):
        """
        Detects specific problems in a query using the fine-tuned BERT model.
        """
        print("Problem\n")
        # Encode the input text
        prompt = f"""You are a highly empathetic and knowledgeable mental health assistant. Your task is to analyze the given user query and identify:
        The specific mental health problem or concern the user might be facing (e.g., depression, anxiety, loneliness, self-esteem issues, identity crisis, etc.).
        A confidence level (on a scale of 0 to 1) indicating how certain you are about your analysis.
        Response Format:
        Provide your output as a structured JSON object with the following keys:

        {{
            "problem": "Identified mental health problem (e.g., depression, loneliness)",
            "confidence": 0.0
        }}

        Example Query and Expected Output:

        Query:
        "I feel like I'm constantly under pressure and can't stop worrying about the future."
        Response:
        {{
            "problem": "chronic stress",
            "confidence": 0.92
        }}
        
        Query:
        {query}
        Response:
        """
        input_ids = self.utility_tokenizer.encode(prompt, return_tensors="pt")

        # Generate a response
        output = self.utility_model.generate(
            input_ids,
            max_length=1000,
            num_return_sequences=1,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            num_beams=5,
        )
        response = self.utility_tokenizer.decode(output[0], skip_special_tokens=True)
        return response

    async def rag_similar(self, query, method="cosine", top_k=5):
        """
        Retrieves similar information using FAISS and specified similarity metric.
        """

        pass

    async def get_user_memories(self, query):
        """
        Retrieve relevant user memories for the given query.
        """

        pass

    async def call_dialo(self, query):
        """
        Generate responses using a fine-tuned DialoGPT model.
        """
        pass

    async def gemini(self, query):
        """
        Call Gemini with the constructed prompt and return output with streaming.

        Args:
            self: The class instance (accessing other methods)
            query: The user's input query

        Returns:
            A string representing the Gemini response with simulated streaming.
        """

        # Run all the coroutines concurrently
        emotion_task = self.emotion_detection(query)
        # memories_task = self.get_user_memories(query)
        # problem_task = self.problem_detection(query)
        # strategy_task = self.strategy_detection(query)

        # Await results of all tasks
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
        5. Give brief answers. Donot trouble the user with too much information at the same time.
        6. Explore user's feelings slowly. Let them approach situations at their own pace.
        7. If you're asking questions, keep it to a minimum.
        
        Now, based on the information above, generate a response that fulfills the user's emotional and mental health needs.
        """

        print("Processing with Gemini...")

        # Add the query to chat history
        self.history.append({"role": "user", "parts": {"text": query}})

        try:
            # Start the chat with streaming
            chat = self.model.start_chat(history=self.history)
            response = chat.send_message(prompt)

            # Add the model's response to history
            self.history.append({"role": "model", "parts": {"text": response}})

            return response.text
        except Exception as e:
            return f"Error: {str(e)}"


async def __main__():
    model = Chatbot()
    # print(await model.emotion_detection("I feel so lonely"))
    # print(await model.problem_detection("I feel so lonely"))
    while True:
        query = input(">> User: ")
        if query == "exit":
            break
        print(">> Pet: " + await model.gemini(query))


if __name__ == "__main__":
    asyncio.run(__main__())
