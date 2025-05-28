import yaml
from pathlib import Path

def load_yaml_spec(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_output_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)
