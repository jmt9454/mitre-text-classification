import sqlite3
import json
from stix2 import MemoryStore
from stix2 import Filter

# Load the STIX bundle from file
with open("data\\attack-stix-data-master\\enterprise-attack\\enterprise-attack.json", "r") as f:
    stix_bundle = json.load(f)  # This is a dict with "type": "bundle", "objects": [...]

stix_objects = stix_bundle.get('objects', [])

# Wrap bundle in a MemoryStore for easy querying
store = MemoryStore(stix_data = stix_objects)

### CONNECT TO DATABASE
db = sqlite3.connect("data\\sqlite3\\mitre_data.db")
cursor = db.cursor()

### ENSURE mitre_desc TABLE EXISTS
cursor.execute("""
CREATE TABLE IF NOT EXISTS mitre_technique_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT,
    url TEXT,
    attack_pattern TEXT,
    technique_id TEXT
)
""")
db.commit()

# Query for attack patterns and insert into the database
techniques = store.query([ Filter("type", "=", "attack-pattern") ])
for tech in techniques:
    attack_pattern_id = tech['id']
    # Inefficient way to get the technique_id, but it guarantees we have it if it is not the first reference
    technique_id = [ref["external_id"] for ref in tech["external_references"]
                    if ref.get("source_name") == "mitre-attack"][0]
    for ref in tech["external_references"]:
        if ref.get("source_name") != "mitre-attack":
            cursor.execute(
                "INSERT INTO mitre_technique_references (source_name, url, attack_pattern, technique_id) VALUES (?,?,?,?)",
                (ref.get("source_name"), ref.get("url"), attack_pattern_id, technique_id)
            )
    db.commit()
    print(f"Inserted references for {technique_id} ({attack_pattern_id})")
