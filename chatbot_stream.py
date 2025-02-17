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

# from langchain.agents import Tool
# from TaskBot.bot import Taskbot


class Chatbot:
    def __init__(self):
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            api_key=os.getenv("GOOGLE_API_KEY1"),
        )

        # Initialize chat history and add the system prompt
        self.chat_history = ChatMessageHistory()
        self.chat_history.add_message(system_prompt)

        # Initialize ConversationSummaryBufferMemory with the chat history
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm, max_token_limit=500, chat_memory=self.chat_history
        )
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
        # Create the conversation chain
        self.chain = self.prompt | self.llm
        self.store = {}
        print("Chatbot initialised.\n")

        self.chain_with_history = RunnableWithMessageHistory(
            runnable=self.chain,
            get_session_history=self.get_message_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_message_history(self, session_id: str, user_id: int) -> ChatMessageHistory:
        if user_id not in self.store:
            self.store[user_id] = {}  # Initialize user dictionary if not present
        if session_id not in self.store[user_id]:
            self.store[user_id][
                session_id
            ] = ChatMessageHistory()  # Initialize session chat history

        return self.store[user_id][session_id]

    async def chat(self, query: str, session_id: str, user_id):
        message_history = self.get_message_history(session_id, user_id)

        # Retrieve relevant documents from the RAG database asynchronously.
        # The query_retriever is assumed to be a synchronous function.
        rag_docs = asyncio.create_task(asyncio.to_thread(query_retriever, query))
        # Augment the query with the retrieved document content.

        # Run emotion detection and therapy strategy prediction concurrently.
        emotion_result_task = asyncio.create_task(emotion_detection(query))
        # Retrieve recent messages for strategy prediction.
        recent_msgs = message_history.messages[-8:]
        recent_msgs.append(HumanMessage(content=f"{query}"))
        strategy_result_task = asyncio.create_task(
            predict_therapy_strategy(recent_msgs)
        )

        # Await both concurrently.
        emotion_result, strategy_result, rag_docs = await asyncio.gather(
            emotion_result_task, strategy_result_task, rag_docs
        )
        reasoning, strategy_list = strategy_result

        # Step 1: Extract content from each Document object
        extracted_contents = [doc.page_content for doc in rag_docs]

        # Step 2: Combine the extracted content into a single string
        # Using two newlines as a separator between documents for readability
        combined_context = "\n\n".join(extracted_contents)
        # context_message = SystemMessage(content=combined_context)
        response = ""
        # Generate response using the augmented query.
        async for token in self.chain.astream(
            {
                "input": query,
                "history": message_history.messages,
                "emotion_result": emotion_result,
                "reasoning_for_strategy": reasoning,
                "strategy_result": strategy_list,
                "context": combined_context,
            },
            config={"configurable": {"session_id": session_id, "user_id": user_id}},
        ):
            yield token.content  # Yield each token's content as it is generated.
            response += token.content

        # Update chat history with the user input and AI response.
        self.store[user_id][session_id].add_user_message(
            f"""{query}\nRelevant context from retrieved documents:\n{rag_docs}\n
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
            if query == "exit":
                print(model.store.get("bh", 123))
                break
            print(">> Pet: ")
            async for response in model.chat(query, "bh", 123):
                print(f"{response}", end="")

    asyncio.run(main())
