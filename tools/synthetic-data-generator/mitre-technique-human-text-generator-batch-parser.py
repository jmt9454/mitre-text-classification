import json
import os # Import os module for path manipulation

def process_jsonl_file(file_path):
    """
    Loads a JSON Lines (JSONL) file, extracts custom_id and message content
    from each line, and prints them.

    Args:
        file_path (str): The path to the JSONL file.
    """
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return

        print(f"Processing file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1): # Enumerate to get line numbers for better error reporting
                # Skip empty lines
                if not line.strip():
                    continue

                try:
                    # Each line is a separate JSON object
                    data = json.loads(line.strip()) # .strip() removes leading/trailing whitespace and newlines

                    custom_id = data.get("custom_id")
                    message_content = None

                    response = data.get("response")
                    if response:
                        body = response.get("body")
                        if body:
                            choices = body.get("choices")
                            if choices and isinstance(choices, list):
                                for choice in choices:
                                    message = choice.get("message")
                                    if message:
                                        content = message.get("content")
                                        if content:
                                            message_content = content
                                            break # Assuming we only need the first message content

                    print(f"  Custom ID: {custom_id}")
                    print(f"  Message Content: {message_content}\n")

                except json.JSONDecodeError as e:
                    print(f"  Error decoding JSON on line {line_num} of {file_path}: {e}")
                    print(f"  Problematic line content: '{line.strip()}'")
                except Exception as e:
                    print(f"  An unexpected error occurred on line {line_num}: {e}")
                    print(f"  Problematic line content: '{line.strip()}'")

    except Exception as e:
        print(f"An error occurred while opening or processing {file_path}: {e}")

# Example usage with your file path:
jsonl_file_path = r"data\\openai_batches\\batch_685554a5dbb8819092c4732a9dd5ac5b_output.jsonl"
process_jsonl_file(jsonl_file_path)

# If you have multiple .jsonl files in a directory, you can loop through them:
# import glob
#
# directory_path = "data/openai_batches/"
# for jsonl_file in glob.glob(os.path.join(directory_path, "*.jsonl")):
#     process_jsonl_file(jsonl_file)