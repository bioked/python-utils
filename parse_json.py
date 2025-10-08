import json
from pathlib import Path

file_path = Path("sample.json")

with file_path.open("r", encoding="utf-8") as f:
	raw_text = f.read()

data = json.loads(raw_text)

print(json.dumps(data, indent=4))
