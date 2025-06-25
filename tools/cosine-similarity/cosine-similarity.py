import sqlite3
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

DB_FILE = 'data\\sqlite3\\mitre_data.db'

def load_mitre_techniques(db_file):
    """
    Connects to the SQLite database and retrieves MITRE techniques.
    Returns a DataFrame with technique_id, name, and description.
    """
    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute('SELECT technique_id, name, description FROM mitre_desc')
    data = cursor.fetchall()
    db.close()
    return pd.DataFrame(data, columns=['technique_id', 'name', 'description'])

def load_synthetic_texts(db_file):
    """
    Connects to the SQLite database and retrieves synthetic texts.
    Returns a DataFrame with technique_id, name, and text.
    """
    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute('SELECT technique_id, name, text FROM synthetic_texts_test')
    data = cursor.fetchall()
    db.close()
    return pd.DataFrame(data, columns=['technique_id', 'name', 'text'])

def load_model():
    """
    Loads the SentenceTransformer model for embedding generation.
    """
    return SentenceTransformer('all-MiniLM-L6-v2')

def encode_texts(model, texts, save_to_file=None, load_from_file=None):
    """
    Encodes a list of texts into embeddings using the provided model.
    Returns a NumPy array of embeddings.
    """
    if load_from_file:
        try:
            return np.load(load_from_file)
        except Exception as e:
            print(f"Error loading embeddings from file: {e}")
    else:
        embeddings = model.encode(texts, convert_to_tensor=True)
        if save_to_file:
            try:
                np.save(save_to_file, embeddings.cpu().numpy())
            except Exception as e:
                print(f"Error saving embeddings to file: {e}")
        return embeddings
    
def calculate_cosine_similarity(embeddings1, embeddings2):
    """
    Calculates cosine similarity between two sets of embeddings.
    Returns a DataFrame with cosine similarity scores.
    """
    if embeddings1.shape[0] == 0 or embeddings2.shape[0] == 0:
        return pd.DataFrame(columns=['technique_id', 'name', 'similarity'])
    
    similarities = cosine_similarity(embeddings1, embeddings2)
    return pd.DataFrame(similarities, columns=embeddings2.index, index=embeddings1.index)

def main():
    # Load data
    techniques_df = load_mitre_techniques(DB_FILE)
    synthetic_texts_df = load_synthetic_texts(DB_FILE)

    # Load model
    model = load_model()

    # Encode techniques and synthetic texts
    # Remove save_to_file parameter and replace with load_from_file if you've already saved embeddings
    technique_embeddings = encode_texts(model, techniques_df['description'].tolist(), save_to_file='technique_embeddings.npy')
    synthetic_embeddings = encode_texts(model, synthetic_texts_df['text'].tolist(), save_to_file='synthetic_embeddings.npy')

    # Calculate cosine similarity
    similarity_df = calculate_cosine_similarity(technique_embeddings, synthetic_embeddings)

    # Print results
    print(similarity_df)

if __name__ == "__main__":
    main()
