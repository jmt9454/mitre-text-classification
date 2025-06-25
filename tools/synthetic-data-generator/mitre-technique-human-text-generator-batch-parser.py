import json
import sqlite3 # Import sqlite3 for database operations
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
                    technique_id = custom_id.split('_')[0] if custom_id else None
                    technique_name = custom_id.split('_')[1] if custom_id and len(custom_id.split('_')) > 1 else None
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
                                            print(f"  Custom ID: {custom_id}")
                                            print(f"  Message Content: {message_content}\n")
                                            add_synthetic_text_to_db('data\\sqlite3\\mitre_data.db', technique_id, technique_name, message_content)
                                            break

                except json.JSONDecodeError as e:
                    print(f"  Error decoding JSON on line {line_num} of {file_path}: {e}")
                    print(f"  Problematic line content: '{line.strip()}'")
                except Exception as e:
                    print(f"  An unexpected error occurred on line {line_num}: {e}")
                    print(f"  Problematic line content: '{line.strip()}'")

    except Exception as e:
        print(f"An error occurred while opening or processing {file_path}: {e}")


def add_synthetic_text_to_db(db_file, technique_id, name, synthetic_text):
    """
    Connects to the SQLite database and adds synthetic text for a given technique.
    """
    db = None
    try:
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS synthetic_texts_test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            technique_id TEXT,
            name TEXT,
            text TEXT
        )
        """)
        cursor.execute("INSERT INTO synthetic_texts_test (technique_id, name, text) VALUES (?, ?, ?)", (technique_id, name, synthetic_text))
        db.commit()
    except sqlite3.Error as e:
        print(f"Database error while inserting synthetic text: {e}")
    finally:
        if db:
            db.close()

def main():
    jsonl_file_path = r"data\\openai_batches\\batch_6859b0f79a9c8190bdf0d62ff7903192_output.jsonl"
    process_jsonl_file(jsonl_file_path)

if __name__ == "__main__":
    main()