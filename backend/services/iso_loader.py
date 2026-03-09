import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RULES_PATH = os.path.join(BASE_DIR, "clause_rules", "iso9001.json")

with open(RULES_PATH, "r", encoding="utf-8") as f:
    ISO9001_RULES = json.load(f)
