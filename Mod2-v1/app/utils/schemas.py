import json
from pathlib import Path
from jsonschema import Draft7Validator

BASE = Path(__file__).resolve().parents[2]  # до корня репо (/app)
CHUNK_SCHEMA_PATH = BASE / "contracts" / "chunk.json"
FINAL_SCHEMA_PATH = BASE / "contracts" / "final.json"

with open(CHUNK_SCHEMA_PATH, "r", encoding="utf-8") as f:
    CHUNK_SCHEMA = json.load(f)

with open(FINAL_SCHEMA_PATH, "r", encoding="utf-8") as f:
    FINAL_SCHEMA = json.load(f)

chunk_validator = Draft7Validator(CHUNK_SCHEMA)
final_validator = Draft7Validator(FINAL_SCHEMA)
