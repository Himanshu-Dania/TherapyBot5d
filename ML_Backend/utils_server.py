from flask import Flask, request, jsonify
from TaskBot.utils import (
    DiscreteTask,
    SliderTask,
    CheckmarkTask,
    NotebookTask,
    json_task,
)
from langchain_core.prompts import PromptTemplate
from TaskBot.bot import Taskbot
from utils import extract_json_from_string, format_task
from RAG.create_user_embeds import upload_interests_to_rag

app = Flask(__name__)

taskbot = Taskbot()


@app.route("/api/load_task_into_session", methods=["POST"])
async def load_task_into_session():
    if not request.is_json:
        return jsonify({"error": "Request content-type must be application/json"}), 400
    req = request.get_json()
    task = req["task"]
    times_missed = req["times_missed"]
    try:
        task = format_task(task)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    message = PromptTemplate(
        input_variables=["task", "times_missed"],
        template="""
The user has missed the follwoing tasks {times_missed} times. Please guide the user in an empathic and supportive manner. Ask them why they are unable to complete the task and provide them with the necessary support.
This is the follwoing task that they have missed
{task}""",
    )

    # Create a session id and send back here... so they can ask to retreive it

    print(message.format(task=task, times_missed=times_missed))
    return jsonify({"message": "Task loaded into memory"}), 200


@app.route("/api/change_task_difficulty", methods=["POST"])
async def change_task_difficulty():
    if not request.is_json:
        return jsonify({"error": "Request content-type must be application/json"}), 400

    # Parse the JSON data from the request
    data = request.get_json()
    user_id = data["user_id"]
    task = data["task"]
    reason = data["reason"]
    try:
        task = format_task(task)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    new_task = await taskbot.change_task_difficulty(reason=reason, task=task)

    return extract_json_from_string(new_task), 200


@app.route("/api/create_task", methods=["POST"])
async def create_task():
    if not request.is_json:
        return jsonify({"error": "Request content-type must be application/json"}), 400

    # Parse the JSON data from the request
    data = request.get_json()
    user_id = data["user_id"]
    tasks = data["tasks"]
    reason = data["reason"]
    try:
        tasks_processed = [format_task(task) for task in tasks]
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    new_tasks = await taskbot.create_task(reason=reason, tasks=tasks_processed)
    print(new_tasks)
    return extract_json_from_string(new_tasks), 200


@app.route("/api/create_user_embedding", methods=["POST"])
async def create_user_embedding():
    if not request.is_json:
        return jsonify({"error": "Request content-type must be application/json"}), 400

    # Parse the JSON data from the request
    data = request.get_json()
    user_id = data["user_id"]
    interests = data["interests"]
    interests_str = " ".join(interests)
    await upload_interests_to_rag(user_id=user_id, user_interests=interests_str)

    return jsonify({"message": "User embedding created"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8500, debug=True)
