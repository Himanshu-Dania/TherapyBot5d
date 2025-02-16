from transformers import pipeline
import asyncio
import json

emotion_model = pipeline(
    task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None
)


async def emotion_detection(query):
    """
    Detects the emotion in the input query using the 'SamLowe/roberta-base-go_emotions' model.
    """
    results = emotion_model(query, top_k=3)

    return results


async def __main__():
    query = "I am feeling very sad today. My dog passed away and I am devastated."
    emotion_result = await emotion_detection(query)
    print(json.dumps(emotion_result, indent=2))


if __name__ == "__main__":
    asyncio.run(__main__())
