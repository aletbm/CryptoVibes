import json
import toml
from pathlib import Path

json_path = Path("credentials.json")

toml_path = Path("credentials.toml")

with open(json_path, "r", encoding="utf-8") as f:
    credentials = json.load(f)

with open(toml_path, "w", encoding="utf-8") as f:
    toml.dump({"gcp_service_account": credentials}, f)

print(f"TOML file generated in: {toml_path}")
