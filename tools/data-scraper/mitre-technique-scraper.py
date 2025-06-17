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
CREATE TABLE IF NOT EXISTS mitre_technique_descriptions (
    attack_pattern TEXT PRIMARY KEY,
    technique_id TEXT,
    name TEXT,
    description TEXT
)
""")
db.commit()

# Query for attack patterns and insert into the database
techniques = store.query([ Filter("type", "=", "attack-pattern") ])
for tech in techniques:
    attack_pattern_id = tech['id']
    technique_id = [ref["external_id"] for ref in tech["external_references"]
                    if ref.get("source_name") == "mitre-attack"][0]
    technique_name = tech['name']
    technique_desc = tech['description']
    cursor.execute("INSERT INTO mitre_technique_descriptions (attack_pattern, technique_id, name, description) VALUES (?,?,?,?)",(attack_pattern_id,technique_id,technique_name,technique_desc))
    db.commit()