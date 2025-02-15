from typing import List, Dict, Optional, Union


def format_conversation(messages: List[Dict]) -> str:
    """
    Formats a list of conversation messages into a string format required by the Gemini API.

    Example input:
    [
        {
            "role": "sys",
            "detected_strategy": ["Question", "Reflection of feelings"],
            "text": "How are you feeling today?"
        },
        {
            "role": "usr",
            "detected_strategy": None,
            "text": "I'm feeling a bit anxious"
        }
    ]
    """

    # Validate input
    if not messages:
        raise ValueError("Messages list cannot be empty")

    formatted_messages = []

    for msg in messages:
        # Validate required fields
        if "role" not in msg or "text" not in msg:
            raise ValueError("Each message must have 'role' and 'text' fields")

        role = msg["role"]
        text = msg["text"].strip()

        if role not in ["usr", "sys"]:
            raise ValueError(f"Invalid role: {role}. Must be 'usr' or 'sys'")

        # Format system messages with strategy
        if role == "sys":
            strategies = msg.get("detected_strategy", [])
            # Handle both string and list inputs for backward compatibility
            if isinstance(strategies, str):
                strategies = [strategies]
            elif strategies is None:
                strategies = []

            if not strategies:
                # System messages can now have no strategy
                formatted_msg = f"sys: {text}"
            else:
                # Join multiple strategies with comma and space
                strategy_str = ", ".join(strategies)
                formatted_msg = f"sys({strategy_str}): {text}"

        # Format user messages
        else:  # role == 'usr'
            if msg.get("detected_strategy"):
                raise ValueError("User messages should not have a detected_strategy")
            formatted_msg = f"usr: {text}"

        formatted_messages.append(formatted_msg)

    # Join all messages with newlines
    return "\n".join(formatted_messages)


# Example usage:
if __name__ == "__main__":
    example_conversation = [
        {
            "role": "sys",
            "detected_strategy": ["Question", "Reflection of feelings"],
            "text": "How are you feeling today? I can sense that you're dealing with a lot.",
        },
        {"role": "usr", "detected_strategy": None, "text": "I'm feeling a bit anxious"},
        {
            "role": "sys",
            "detected_strategy": None,  # System message with no strategy
            "text": "Tell me more about that",
        },
        {
            "role": "sys",
            "detected_strategy": [
                "Affirmation and Reassurance",
                "Providing Suggestions",
            ],
            "text": "It's completely normal to feel this way. Have you tried any relaxation techniques?",
        },
    ]

    try:
        formatted = format_conversation(example_conversation)
        print("Formatted conversation:")
        print(formatted)

    except ValueError as e:
        print(f"Error formatting conversation: {str(e)}")
