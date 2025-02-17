from typing import List, Dict, Optional, Union


def format_conversation(messages: List[Dict]) -> str:
    """
    Formats a list of conversation messages into a string format required by the Gemini API.

    Example input:
    [
        {
            "role": "sys",
            "strategy": ["Question", "Reflection of feelings"],
            "content": "How are you feeling today?"
        },
        {
            "role": "usr",
            "strategy": None,
            "content": "I'm feeling a bit anxious"
        }
    ]
    """

    # Validate input
    if not messages:
        raise ValueError("Messages list cannot be empty")

    formatted_messages = []

    for msg in messages:
        # Validate required fields
        if "role" not in msg or "content" not in msg:
            raise ValueError("Each message must have 'role' and 'content' fields")

        role = msg["role"]
        content = msg["content"].strip()

        if role not in ["usr", "sys"]:
            raise ValueError(f"Invalid role: {role}. Must be 'usr' or 'sys'")

        # Format system messages with strategy
        if role == "sys":
            strategies = msg.get("strategy", [])
            # Handle both string and list inputs for backward compatibility
            if isinstance(strategies, str):
                strategies = [strategies]
            elif strategies is None:
                strategies = []

            if not strategies:
                # System messages can now have no strategy
                formatted_msg = f"sys: {content}"
            else:
                # Join multiple strategies with comma and space
                strategy_str = ", ".join(strategies)
                formatted_msg = f"sys({strategy_str}): {content}"

        # Format user messages
        else:  # role == 'usr'
            if msg.get("strategy"):
                raise ValueError("User messages should not have a strategy")
            formatted_msg = f"usr: {content}"

        formatted_messages.append(formatted_msg)

    # Join all messages with newlines
    return "\n".join(formatted_messages)


# Example usage:
if __name__ == "__main__":
    example_conversation = [
        {
            "role": "sys",
            "strategy": ["Question", "Reflection of feelings"],
            "content": "How are you feeling today? I can sense that you're dealing with a lot.",
        },
        {"role": "usr", "content": "I'm feeling a bit anxious"},
        {
            "role": "sys",
            "strategy": ["Others"],  # System message with no strategy
            "content": "Tell me more about that",
        },
        {
            "role": "usr",
            "content": "It's completely normal to feel this way. Have you tried any relaxation techniques?",
        },
    ]

    try:
        formatted = format_conversation(example_conversation)
        print("Formatted conversation:")
        print(formatted)

    except ValueError as e:
        print(f"Error formatting conversation: {str(e)}")
