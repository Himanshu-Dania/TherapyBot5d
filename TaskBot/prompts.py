from langchain_core.prompts import PromptTemplate


create_task_prompt = PromptTemplate(
    input_variables=["reason", "tasks_json"],
    template="""
You are an intelligent assistant designed to create personalized therapy tasks for users. You receive the following information in JSON format:
```json
{{
    "reason_for_task_creation": "A reason or message explaining why this task is being created.",
    "existing_tasks": [
        {{
            "task_name": "The name of the existing task.",
            "task_type": "The type of the task (e.g., 'discrete', 'slider', 'checkmark').",
            "reason_for_task_creation": "The reason or message explaining why the task was created.",
            "description": "A detailed description of the task.",
            "completed": "The current progress of the task (e.g., 0, 5 for discrete tasks; numeric(0.0 t0 100.0) for slider tasks; true/false for checkmark and notebook tasks).",
            "total_count": "Number of counts to be completed to finish the task, only present if it's a discrete task.",
            "difficulty": "The difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
            "recurring": "Number of hours before the task is repeated, e.g., 0 by default."
        }}
    ]
}}
```

Your task is to:
- Create a new task for the user, avoiding redundancy with existing tasks (e.g., tasks with the same name or purpose).
- Gradually increase the difficulty level based on the user's progress and completed tasks.
- Ensure the task is tailored to the reason for task creation and aligns with the user's goals.
- Make sure the tasks are framed in a positive tone.
- Output the task in JSON format following the updated schema.

The output should be a task or a list of tasks in JSON format.

Here are a few examples of how the output should look:

Example 1:
```json
{{
    "task": {{
        "task_name": "Emotion Regulation Skill Training",
        "task_type": "notebook",
        "reason_for_task_creation": "Enhance the user's ability to manage emotional responses.",
        "description": "Identify emotional triggers and apply coping strategies in stressful situations.",
        "completed": False,
        "difficulty": "hard",
        "recurring": 24
    }}
}}
```
Example 2:
```json
{{
    "task": [{{
        "task_name": "Morning Gratitude Check-in",
        "task_type": "checkmark",
        "difficulty": "easy",
        "completed": false,
        "recurring": 0,
        "reason_for_task_creation": "To encourage the user to start the day with positive thoughts.",
        "description": "Mark your morning gratitude as complete."
    }},{{
        "task_name": "Write few positive thoughts",
        "task_type": "checkmark",
        "completed": false,
        "difficulty": "easy",
        "recurring": 24,
        "reason_for_task_creation": "To help the user focus and relax through mindfulness.",
        "description": "Write few lines of positive thoughts about oneself to reinforce self-esteem."
    }}]
}}
```

Example 3:
```json
{{
    "task": {{
        "task_name": "Social Exposure Challenge",
        "task_type": "discrete",
        "reason_for_task_creation": "Encourage gradual exposure to social situations.",
        "description": "Initiate a conversation with a stranger in a controlled environment.",
        "completed": 0,
        "total_count": 5,
        "difficulty": "hard",
        "recurring": 72
    }}
}}
```

Generate tasks based on the inputs provided. Make the tasks engaging, personalized, and aligned with the therapy goals.

**Input Data:**
```json
{{
    "reason_for_task_creation": "{reason}",
    "existing_tasks": {tasks_json}
}}
```
        """,
)


journey_prompt_template = PromptTemplate(
    input_variables=["new_task", "journeys_json"],
    template="""
You are an intelligent assistant designed to manage and organize therapy journeys.

You will receive:
- A **new task** in JSON format
- A list of **existing journeys**, each containing:
    - `journey_name`
    - `description`
    - `tasks`
    - `difficulty`
    

Your task:
1. **Determine if the new task fits into an existing journey**:
    - Match based on similar themes, difficulty.
    - Avoid overloading a single journey.

2. **If the task does not fit, create a new journey**:
    - Generate a meaningful `journey_name` and `description`.
    - Ensure the difficulty aligns with the task.

**Output either a new journey's name or an already present journey's name.**

Example:
Input:
```json
{{
    "new_task": [{{
        "task_name": "Rejection Exposure",
        "task_type": "checkmark",
        "reason_for_task_creation": "To help get used to rejections and failures.",
        "description": "Every day, ask for a discount at a store.",
        "difficulty": "medium",
        "completed": false,
        "recurring": 24
    }}, 
    {{
        "task_name": "Face Your Fears",
        "task_type": "discrete",
        "reason_for_task_creation": "To help overcome fears.",
        "description": "Face a fear every day.",
        "difficulty": "hard",
        "completed": 0,
        total_count: 2,
        "recurring": 24
    }}],
    "existing_journeys": [{{
        "journey_name": "Mindfulness Journey",
        "description": "A collection of tasks aimed at promoting mindfulness and reducing stress.",
        "tasks": [{{
                "task_name": "Morning Meditation",
                "description": "Meditate for 10 minutes every morning",
            }},
            {{
                "task_name": "Evening Reflection",
                "description": "Reflect on your day for 5 minutes before bed."   
        }}],
        "difficulty": "easy"
    }},
    {{
        "journey_name": "Fitness Journey",
        "description": "Tasks related to physical exercises and improving strength.",
        "tasks": [{{
                "task_name": "Daily Push-ups",
                "description": "Do 20 push-ups daily",
            }},
            {{
                "task_name": "Weekly Jogging",
                "description": "Jog for 30 minutes every weekend."
        }}],
        "difficulty": "medium"
    }}]
}}
```

Output:
Winning against Rejections and Fears
```

**Input Data:**
```json
{{
    "new_task": {new_task},
    "existing_journeys": {journeys_json}
}}
```
Ouput:
""",
)

task_difficulty_prompt = PromptTemplate(
    input_variables=["task", "reason"],
    template="""
You are an intelligent assistant designed to help curate personalized therapy tasks for users. 
Your task is to change the difficulty of the task according to a user given reason.
You receive the following information in JSON format:
```json
{{
    "reason": "A reason or message explaining why the difficulty of the task should be changed.",
    "task": {{
        "task_name": "The name of the task.",
        "task_type": "The type of the task (e.g., 'discrete', 'slider', 'checkmark').",
        "reason_for_task_creation": "The reason or message explaining why the task was created.",
        "description": "A detailed description of the task.",
        "completed": "The current progress of the task (e.g., 0, 5 for discrete tasks; numeric for slider tasks; true/false for checkmark tasks).",
        "total_count": "Number of counts to be completed to finish the task if it's a discrete task.",
        "difficulty": "The difficulty level of the task (e.g., 'easy', 'medium', 'hard').",
        "recurring": "Number of hours before the task is repeated, e.g., 0 by default."
    }}
}}

Your task is to:
- Change the difficulty of the task based on the reason provided.
- Output the updated task in JSON format.
- You can split the task into multiple tasks if needed. If there, output them in a list.
- Make sure to only give out the new task in json and no other information except it.
Example:
```json
Input:
{{
    "reason": "I am having alot of negative self-talk and difficulty challenging my automatic thoughts. I need a more advanced exercise to help myself",
    "task": {{
        "task_name": "Cognitive Restructuring Exercise",
        "task_type": "discrete",
        "reason_for_task_creation": "Help the user identify and challenge negative thoughts.",
        "description": "Identify a negative thought, evaluate a plan to fix it.",
        "completed": 0,
        "total_count": 1,
        "difficulty": "easy",
        "recurring": 24
    }}
}}
Output:
{{
    "task": {{
        "task_name": "Cognitive Restructuring Exercise",
        "task_type": "discrete",
        "reason_for_task_creation": "Help the user identify and challenge negative thoughts.",
        "description": "Identify a negative thought, critically evaluate the evidence supporting and contradicting it, and generate alternative, balanced thoughts. Reflect on cognitive distortions and document insights for future review.",
        "completed": 0,
        "total_count": 3,
        "difficulty": "hard",
        "recurring": 24
    }}
}}

Input:
```json
{{
    "reason": "{reason}",
    "task": {task}
}}
```

Output:
""",
)
