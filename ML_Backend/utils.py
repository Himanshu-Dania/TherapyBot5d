import json
import re
from TaskBot.utils import Task, CheckmarkTask, DiscreteTask, SliderTask, NotebookTask


def extract_json_from_string(input_string):
    # Use regex to extract the JSON part
    match = re.search(r"```json(.*?)```", input_string, re.DOTALL)

    if match:
        json_str = match.group(1).strip()  # Extract JSON content and strip whitespace

        try:
            # Fix potential formatting issues before loading JSON
            json_str = json_str.replace("\n", "").replace("\t", "")
            return json.loads(json_str)  # Convert JSON string to Python dict
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format: {str(e)}"}
    else:
        return {"error": "No valid JSON found in the string"}


def format_task(task):
    task_type = task["task_type"]
    if task_type == "checkmark":
        task = CheckmarkTask(**task)
    elif task_type == "discrete":
        task = DiscreteTask(**task)
    elif task_type == "slider":
        task = SliderTask(**task)
    elif task_type == "notebook":
        task = NotebookTask(**task)
    else:
        raise ValueError("Invalid task type")
    return task


if __name__ == "__main__":
    # Example usage
    input_string = """```json
    {
        "task": {
        "task_name": "Emotion Regulation Skill Training","task_type": "notebook","reason_for_task_creation": "Enhance the user's ability to manage emotional responses.","description": "Identify emotional triggers, analyze the intensity and duration of emotional responses, and apply a range of coping strategies (e.g., deep breathing, mindfulness, grounding techniques) in progressively more challenging situations.  Record your experiences, including the specific strategies utilized and their effectiveness.","difficulty": "medium","recurring": 24,
        "note_content": "",
        "completed": false
        }
    }
    ```"""

    parsed_json = extract_json_from_string(input_string)
    print(parsed_json)
