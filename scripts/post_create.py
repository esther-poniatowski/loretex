"""
Script: `post_create.py`

Conda Environment Post-Creation Setup Script for Loretex Package

Register project-specific directories (e.g., `src/`, `tests/`) into the active Conda environment's
`site-packages` via `.pth` file registration.

Usage
-----
After creating the Conda environment from the `environment.yml` file:

1. Navigate to the project root directory.

2. Activate the Conda environment:

    ```bash
    conda activate loretex
    ```

3. Run the script to register the project directories:

    ```bash
    python scripts/post_create.py
    ```

Requirements
------------
- Must be executed within an active Conda environment created via `environment.yml`.
- Assumes the presence of `src/` and `tests/` in the project root.
- Dependencies: `pyyaml` for YAML parsing (installed in the Conda environment).

"""

import logging
import os
import sys
import site
from pathlib import Path
from typing import Optional

import yaml

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def get_env_name(env_file: Path = Path("environment.yml")) -> str:
    """
    Extract the Conda environment name from the local `environment.yml` file.

    Parameters
    ----------
    env_file : Path, default=Path("environment.yml")
        Path to the environment specification file in the project root.

    Returns
    -------
    str
        Name of the Conda environment associated with the local `environment.yml`.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the file does not contain a `name` field.
    """
    if not env_file.exists():
        raise FileNotFoundError(f"Missing environment file: {env_file}")
    with env_file.open("r") as f:
        env_data = yaml.safe_load(f)
    if not isinstance(env_data, dict) or "name" not in env_data:
        raise ValueError("The environment file does not contain a valid 'name' field.")
    return str(env_data["name"])


def verify_active_conda_environment(expected_env: str) -> None:
    """
    Verifies that the currently active Conda environment matches the expected name.

    Parameters
    ----------
    expected_env : str
        Name of the Conda environment as defined in `environment.yml`.

    Raises
    ------
    EnvironmentError
        If no Conda environment is active, or if the active environment does not match the expected
        one.
    """
    active_env = os.environ.get("CONDA_DEFAULT_ENV")
    if active_env is None:
        raise EnvironmentError(
            "No active Conda environment detected. Activate the environment associated with the project."
        )
    if active_env != expected_env:
        raise EnvironmentError(
            f"Active Conda environment ('{active_env}') does not match expected environment ('{expected_env}')."
        )


def get_site_packages() -> Path:
    """
    Determines the path to the primary site-packages directory.

    Returns
    -------
    Path
        Path to site-packages.

    Raises
    ------
    RuntimeError
        If the site-packages directory cannot be determined.
    """
    paths = site.getsitepackages()
    if not paths:
        raise RuntimeError("Failed to locate site-packages directory.")
    return Path(paths[0])


def register_project_paths(project_root: Path, site_packages: Path, directories: list[str], name: Optional[str] = None) -> None:
    """
    Write a `.pth` file in the site-packages directory pointing to specified project subdirectories.

    Parameters
    ----------
    project_root : Path
        Path to the root directory of the project.
    site_packages : Path
        Path to the environment's site-packages directory.
    directories : list of str
        List of subdirectory names (relative to project_root) to be registered.
    name : str, default=None
        Optional override for `.pth` filename. Defaults to the project directory name.

    Raises
    ------
    FileNotFoundError
        If any of the specified directories does not exist.
    """
    project_name = name or project_root.name
    pth_path = site_packages / f"{project_name}.pth"

    resolved_paths = []
    for subdir in directories:
        abs_path = project_root / subdir
        if not abs_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {abs_path}")
        resolved_paths.append(str(abs_path.resolve()))

    pth_path.write_text("\n".join(resolved_paths) + "\n")

    logging.info(f"Created .pth file: {pth_path}")
    for entry in resolved_paths:
        logging.info(f"  -> {entry}")


def main() -> None:
    """
    Main entry point for the script.
    Verifies that the active Conda environment matches the one defined in `environment.yml`,
    and registers project directories via a `.pth` file.
    """
    try:
        expected_env = get_env_name()
        verify_active_conda_environment(expected_env)
        site_packages = get_site_packages()
        project_root = Path(__file__).resolve().parent
        directories_to_register = ["src", "tests"]
        register_project_paths(project_root, site_packages, directories=directories_to_register)
    except Exception as e:
        logging.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
