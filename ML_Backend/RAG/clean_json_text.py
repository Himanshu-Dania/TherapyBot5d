import os
import sys
import json
import re
import argparse


def remove_control_characters(text: str) -> str:
    """
    Removes ASCII control characters (0x00–0x1F, 0x7F–0x9F).
    Keeps standard printable characters, newlines, tabs, etc.
    Adjust the regex as needed to remove or keep certain chars.
    """
    # This pattern allows:
    #   - \x09 (tab), \x0A (line feed), \x0D (carriage return)
    #   - \x20-\x7E (basic ASCII printable range)
    # Everything else is replaced with ''.
    cleaned = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]+", "", text)
    return cleaned


def clean_json_file(input_json: str, output_json: str) -> None:
    """
    Loads a JSON file, removes control characters from each value,
    and saves the cleaned data to a new JSON file.
    """
    if not os.path.isfile(input_json):
        print(f"[ERROR] Input file '{input_json}' does not exist.")
        sys.exit(1)

    # Load the existing JSON
    with open(input_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSONDecodeError: {e}")
            sys.exit(1)

    # Clean each value (assuming data is a dict {filename: text})
    cleaned_data = {}
    for key, value in data.items():
        if not isinstance(value, str):
            # If some entries aren't strings, skip or convert them
            cleaned_data[key] = value
            continue

        original_text = value
        cleaned_text = remove_control_characters(original_text)
        cleaned_data[key] = cleaned_text

        # Debug info
        if original_text != cleaned_text:
            print(f"[INFO] Cleaned '{key}': removed control chars.")

    # Write the cleaned data to the new JSON file
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    print(f"[INFO] Successfully wrote cleaned data to '{output_json}'.")


def main():
    parser = argparse.ArgumentParser(
        description="Remove unwanted control characters from a JSON file of extracted text."
    )
    parser.add_argument("input_json", help="Path to the input JSON file.")
    parser.add_argument("output_json", help="Path to save the cleaned JSON file.")
    args = parser.parse_args()

    clean_json_file(args.input_json, args.output_json)


if __name__ == "__main__":
    main()
