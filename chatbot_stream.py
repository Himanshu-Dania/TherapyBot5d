import os
import asyncio

from langchain.prompts.prompt import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from TherapyBot.prompts import system_prompt, user_prompt, pet_prompt
from EmotionBot.bot import emotion_detection
from StrategyBot.bot import predict_therapy_strategy
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from RAG.retreive_books import query_retriever


class Chatbot:
    def __init__(self):
        # Store the API keys in a list and set the starting index.
        self.api_keys = [
            os.getenv("GOOGLE_API_KEY1"),
            os.getenv("GOOGLE_API_KEY2"),
            os.getenv("GOOGLE_API_KEY3"),
        ]
        self.api_key_index = 0

        # Set up prompt templates.
        self.system_prompt_template = SystemMessagePromptTemplate(prompt=system_prompt)
        self.user_prompt_template = HumanMessagePromptTemplate(prompt=user_prompt)
        pet_prompt_template = AIMessagePromptTemplate(prompt=pet_prompt)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                self.system_prompt_template,
                MessagesPlaceholder(variable_name="history"),
                (
                    "user",
                    """These are some books excerpts that may be relevant to answering user's question.
{context}


{input}
**Detected Emotions with their probabilities:** {emotion_result}
(*This represents the user's emotional state.*)
The following Therapy Strategy has been predicted to help the user. Use it to help the user.
**Reasoning for strategy to be used:** {reasoning_for_strategy}
**Detected Strategy:** {strategy_result}""",
                ),
            ]
        )

        # Build LLM instances and corresponding chains.
        self.llm = []
        self.chain = []
        for key in self.api_keys:
            if key is None:
                raise ValueError("API key not found in environment variables.")
            llm_instance = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=key)
            self.llm.append(llm_instance)
            # Create a new chain by piping the prompt with the LLM.
            self.chain.append(self.prompt | llm_instance)

        # Initialize chat history and add the system prompt.
        self.chat_history = ChatMessageHistory()
        self.chat_history.add_message(system_prompt)

        # Initialize ConversationSummaryBufferMemory with the chat history.
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm[0],
            max_token_limit=1000,
            chat_memory=self.chat_history,
        )
        self.store = {}
        print("Chatbot initialised.\n")

    def get_message_history(self, session_id: str, user_id: int) -> ChatMessageHistory:
        if user_id not in self.store:
            self.store[user_id] = {}  # Initialize user dictionary if not present
        if session_id not in self.store[user_id]:
            self.store[user_id][
                session_id
            ] = ChatMessageHistory()  # Initialize session chat history

        return self.store[user_id][session_id]

    async def chat(self, query: str, session_id: str, user_id: int):
        message_history = self.get_message_history(session_id, user_id)

        # Retrieve relevant documents from the RAG database asynchronously.
        rag_docs_task = asyncio.create_task(asyncio.to_thread(query_retriever, query))

        # Run emotion detection and therapy strategy prediction concurrently.
        emotion_result_task = asyncio.create_task(emotion_detection(query))
        recent_msgs = message_history.messages[-8:]
        recent_msgs.append(HumanMessage(content=f"{query}"))
        strategy_result_task = asyncio.create_task(
            predict_therapy_strategy(recent_msgs)
        )

        # Await all concurrently.
        emotion_result, strategy_result, rag_docs = await asyncio.gather(
            emotion_result_task, strategy_result_task, rag_docs_task
        )
        reasoning, strategy_list = strategy_result

        # Extract and combine the content from each retrieved document.
        extracted_contents = [doc.page_content for doc in rag_docs]
        combined_context = "\n\n".join(extracted_contents)

        response = ""

        # --- Round Robin with fallback attempts ---
        attempts = 0
        max_attempts = len(self.chain)
        successful = False

        # Start with the current API key index.
        start_index = self.api_key_index

        while attempts < max_attempts and not successful:
            current_index = (start_index + attempts) % len(self.chain)
            try:
                async for token in self.chain[current_index].astream(
                    {
                        "input": query,
                        "history": message_history.messages,
                        "emotion_result": emotion_result,
                        "reasoning_for_strategy": reasoning,
                        "strategy_result": strategy_list,
                        "context": combined_context,
                    },
                    config={
                        "configurable": {"session_id": session_id, "user_id": user_id}
                    },
                ):
                    yield token.content  # Yield each token's content as it is generated.
                    response += token.content
                successful = True
                # Update to the next API key for subsequent queries.
                self.api_key_index = (current_index + 1) % len(self.chain)
            except Exception as e:
                print(f"Error with API key at index {current_index}: {e}")
                attempts += 1
                if attempts >= max_attempts:
                    raise Exception("All API keys failed.") from e

        # Update chat history with the user input and AI response.
        self.store[user_id][session_id].add_user_message(
            f"""{query}
Relevant context from retrieved documents:
{rag_docs}
**Detected Emotions with their probabilities:** {emotion_result}
(*This represents the user's emotional state.*)
The following Therapy Strategy has been predicted to help the user. Use it to help the user.
**Reasoning for strategy to be used:** {reasoning}
**Detected Strategy:** {strategy_list}"""
        )
        self.store[user_id][session_id].add_ai_message(response)


# Test code in main
if __name__ == "__main__":

    async def main():
        model = Chatbot()
        while True:
            query = input("\n>> User: ")
            if query.lower() == "exit":
                print(model.store.get("bh", 123))
                break
            print(">> Pet: ")
            async for response in model.chat(query, "bh", 123):
                print(f"{response}", end="")

    asyncio.run(main())
