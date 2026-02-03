"""
Module: `loretex.utils.io`

Utility functions for file and I/O operations.

Functions
---------
load_yaml_spec(path: str) -> dict
    Load a YAML specification file and return its contents as a dictionary.
ensure_output_dir(path: Path)
    Ensure that the specified output directory exists, creating it if necessary.
"""
from pathlib import Path

import yaml


def load_yaml_spec(path: str | Path) -> dict:
    """
    Load and formats YAML specification file as a dictionary.

    Arguments
    ---------
    path : str
        Path to the YAML file.
    Returns
    -------
    dict
        Contents of the YAML file as a dictionary.
    """
    with open(Path(path), "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_output_dir(path: Path):
    """
    Ensure that the specified output directory exists, creating it if necessary.

    Arguments
    ---------
    path : Path
        Path to the output directory.
    """
    path.mkdir(parents=True, exist_ok=True)
