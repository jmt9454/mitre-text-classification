import openai
from dotenv import load_dotenv
import os
import sqlite3

# Load environment variables from .env file
load_dotenv()
# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it.")

client = openai.OpenAI()

DATABASE_FILE = 'data\\sqlite3\\mitre_data.db'  # Replace with your SQLite database file name
TABLE_NAME = 'mitre_technique_descriptions'
SYSTEM_MESSAGE = "You are a synthetic data generator that creates realistic news articles based on cybersecurity techniques. Your task is to generate a news article that describes a scenario related to a specific MITRE ATT&CK technique. The article should be informative, engaging, and relevant to the technique's context. You use non-technical language to ensure the article is accessible to a general audience. The sample should be realistic and relevant to the technique. Do not highlight that this is a synthetic data sample or that the scenario is hypothetical. Do not reference MITRE ATT&CK or any specific cybersecurity terms directly."

def get_technique_data(db_file, table_name, technique_name=None):
    """
    Connects to the SQLite database and retrieves technique name and description.
    If technique_name is provided, it fetches data only for that specific technique.
    """
    db = None
    try:
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        if technique_name:
            # Use LIKE for partial matches and parameter binding for safety
            cursor.execute(f"SELECT technique_id, name, description FROM {table_name} WHERE technique_id LIKE ?", ('%' + technique_name + '%',))
        else:
            cursor.execute(f"SELECT technique_id, name, description FROM {table_name}")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if db:
            db.close()

def generate_prompt(technique_id, name, desc):
    return f"Generate a synthetic data news article paragraph about a scenario pertaining to the MITRE ATT&CK technique with ID {repr(technique_id).replace("\\","\\\\").replace('"','\\\"')}, named '{repr(name).replace("\\","\\\\").replace('"','\\\"')}', which is described as: {repr(desc).replace("\\","\\\\").replace('"','\\\"')}. Use non-technical language The sample should be realistic and relevant to the technique. Do not highlight that this is a synthetic data sample or that the scenario is hypothetical. Do not reference MITRE ATT&CK or any specific cybersecurity terms directly."

def generate_batch_input(technique_id, name, desc, system_message, iteration=1):
    return '{"custom_id": "'+technique_id+'_iteration_'+str(iteration)+'", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-4.1-nano", "messages": [{"role": "system", "content": "'+system_message+'"},{"role": "user", "content": "'+generate_prompt(technique_id, name, desc)+'"}],"max_tokens": 128, "temperature": 1.2}}'

def main():
    techniques_to_process = get_technique_data(DATABASE_FILE, TABLE_NAME) 
    with open('batchinput.jsonl', 'w', encoding='utf-8') as f_out:
            for i, (technique_id, name, description) in enumerate(techniques_to_process):
                f_out.write(generate_batch_input(technique_id, name, description, SYSTEM_MESSAGE, i))
                f_out.write('\n')

    batch_input_file = client.files.create(
        file=open("batchinput.jsonl", "rb"),
        purpose="batch"
    )

    batch_input_file_id = batch_input_file.id
    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "test"
        }
    )

if __name__ == "__main__":
    main()