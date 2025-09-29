import json
from pathlib import Path

# Point to your JSON file
file_path = Path("sample.json")

# Read it as plain text
with file_path.open("r", encoding="utf-8") as f:
	raw_text = f.read()

# Parse the JSON string into Python objects
data = json.loads(raw_text)

#Pretty-print the data as JSON again 
print(json.dumps(data, indent=4))
