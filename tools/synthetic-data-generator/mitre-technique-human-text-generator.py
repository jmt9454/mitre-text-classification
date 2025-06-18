import sqlite3
import openai
import os
from dotenv import load_dotenv
import time
import argparse # Import the argparse module

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
DATABASE_FILE = 'data\\sqlite3\\mitre_data.db'  # Replace with your SQLite database file name
TABLE_NAME = 'mitre_technique_descriptions'
OUTPUT_FILE = 'synthetic_data.txt'
DEFAULT_NUM_SYNTHETIC = 1 # Default if not specified via command line
OPENAI_MODEL = "gpt-3.5-turbo" # Or "gpt-4" if you have access and prefer higher quality
REQUEST_DELAY = 0.1 # Delay in seconds between OpenAI API calls to avoid rate limits

# Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it.")

# --- Database Interaction ---
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

# --- OpenAI Interaction ---
def generate_synthetic_text(technique_name, technique_description, num_samples=1):
    """
    Generates synthetic text based on the technique name and description using OpenAI.
    """
    prompt = (
        f"Generate a distinct and realistic text block resembling a very technical news article "
        f"that describe a hypothetical, realistic scenario where the MITRE ATT&CK technique '{technique_name}' is present. "
        f"The description of the technique '{technique_name}' is: \n\n"
        f"'{technique_description}'\n\n"
        f"Do not reference MITRE ATT&CK or any specific cybersecurity terms directly. "
        f"Do not include the fact that the text is hypothetical or fictional. "
    )

    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in cybersecurity and MITRE ATT&CK techniques."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.2, # Adjust for creativity; lower values are more deterministic
            max_tokens=2000, # Adjust as needed
            n=1, # Request one completion that contains all samples
            stop=["---END_GENERATION---"] # Optional: to ensure the model stops
        )
        generated_content = response.choices[0].message.content.strip()
        # Split by the delimiter and filter out any empty strings
        synthetic_texts = [text.strip() for text in generated_content.split('---NEW_TEXT_BLOCK---') if text.strip()]
        return synthetic_texts[:num_samples] # Ensure we return exactly num_samples if the model generates more
    except openai.APIError as e:
        print(f"OpenAI API error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred with OpenAI: {e}")
        return []

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic text for MITRE ATT&CK techniques using OpenAI."
    )
    parser.add_argument(
        '-t', '--technique', type=str,
        help="Optional: Specify a specific technique name (or partial name) to process."
    )
    parser.add_argument(
        '-n', '--num', type=int, default=DEFAULT_NUM_SYNTHETIC,
        help=f"Optional: Number of synthetic text blocks to generate per technique (default: {DEFAULT_NUM_SYNTHETIC})."
    )

    args = parser.parse_args()

    # Determine which techniques to process
    techniques_to_process = get_technique_data(DATABASE_FILE, TABLE_NAME, args.technique)

    if not techniques_to_process:
        if args.technique:
            print(f"No technique found matching '{args.technique}' or an error occurred. Please check the technique name.")
        else:
            print("No data found in the table or an error occurred. Exiting.")
        return

    print(f"Found {len(techniques_to_process)} technique(s) to process.")
    print(f"Generating {args.num} synthetic text blocks for each selected technique.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        for i, (technique_id, name, description) in enumerate(techniques_to_process):
            print(f"Processing technique {i+1}/{len(techniques_to_process)}: {name}")
            
            synthetic_texts = generate_synthetic_text(name, description, args.num)
            
            if synthetic_texts:
                for j, s_text in enumerate(synthetic_texts):
                    f_out.write(f"--- MITRE Technique: {technique_id} - {name} ---\n")
                    f_out.write(f"{s_text}\n\n")
            else:
                print(f"Could not generate synthetic text for '{name}'.")
            
            # Add a small delay to avoid hitting API rate limits
            time.sleep(REQUEST_DELAY)

    print(f"\nSynthetic text generation complete. Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()