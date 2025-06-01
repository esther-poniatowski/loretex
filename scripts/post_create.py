"""
Script: `post_create.py`

Conda environment post-creation setup for Loretex package.

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

3. Register the default project directories (`src/`, `tests/`) into the environment:

    ```bash
    python scripts/post_create.py
    ```

   Register custom directories by providing them as arguments:

    ```bash
    python scripts/post_create.py custom_dir1 custom_dir2
    ```

Arguments
---------
- [positional] (optional)
    List of subdirectory paths to register, relative to the current working directory (default:
    `['src', 'tests']`).
- `--env-file` (optional)
    Path to the Conda environment specification file (default: `environment.yml`).
- `--name-pth` (optional)
    Optional name for the `.pth` file (default: project root directory name).

Requirements
------------
- Must be executed within an active Conda environment created via `environment.yml`.
- Dependencies: `pyyaml` for YAML parsing (installed in the Conda environment).

"""

import logging
import os
import site
from pathlib import Path
from typing import Optional
from collections.abc import Sequence

import typer
import yaml

app = typer.Typer(help="Register developing packages into the Conda environment in editable mode.")



# --- Exception Classes ----------------------------------------------------------------------------

class EnvironmentFileNotFoundError(FileNotFoundError):
    def __init__(self, path: Path) -> None:
        self.path = path


class InvalidEnvironmentFileError(ValueError):
    def __init__(self, path: Path) -> None:
        self.path = path


class CondaEnvironmentMismatchError(EnvironmentError):
    def __init__(self, expected: str, actual: Optional[str]) -> None:
        self.expected = expected
        self.actual = actual


class SitePackagesNotFoundError(RuntimeError):
    pass


class DirectoryToRegisterMissingError(FileNotFoundError):
    def __init__(self, path: Path) -> None:
        self.path = path


# --- CLI Configuration ----------------------------------------------------------------------------

@app.callback()
def setup_logging() -> None:
    """
    Configure basic logging for the script.
    Sets the logging level to INFO and formats the output.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# --- Core Logic Functions -------------------------------------------------------------------------


def get_env_name(env_file: Path) -> str:
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
    EnvironmentFileNotFoundError
        If the file does not exist.
    InvalidEnvironmentFileError
        If the file does not contain a `name` field.
    """
    if not env_file.exists():
        raise EnvironmentFileNotFoundError(env_file)
    with env_file.open("r") as f:
        env_data = yaml.safe_load(f)
    if not isinstance(env_data, dict) or "name" not in env_data:
        raise InvalidEnvironmentFileError(env_file)
    return str(env_data["name"])


def verify_active_conda_environment(expected_env: str) -> str:
    """
    Verifies that the currently active Conda environment matches the expected name.

    Parameters
    ----------
    expected_env : str
        Name of the Conda environment as defined in `environment.yml`.

    Raises
    ------
    CondaEnvironmentMismatchError
        If the active environment does not match the expected one.
    """
    active_env = os.environ.get("CONDA_DEFAULT_ENV")
    if active_env != expected_env:
        raise CondaEnvironmentMismatchError(expected_env, active_env)
    return active_env

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
        raise SitePackagesNotFoundError()
    return Path(paths[0])


def register_project_paths(
    project_root: Path,
    site_packages: Path,
    directories: Sequence[str],
    name_pth: Optional[str] = None
) -> tuple[Path, list[Path]]:
    """
    Write a `.pth` file in the site-packages directory pointing to specified project subdirectories.

    Arguments
    ---------
    project_root : Path
        Absolute path to the root directory of the project.
    site_packages : Path
        Path to the environment's site-packages directory.
    directories : Sequence[str]
        List of subdirectory paths to register, **relative to `project_root`**.
    name_pth : str, optional
        Optional override for `.pth` filename. Defaults to the project directory name.

    Returns
    -------
    pth_path: Path
        Path to the created `.pth` file and a list of resolved paths.
    resolved_paths: list[Path]
        Absolute paths to the directories registered in the `.pth` file.

    Raises
    ------
    DirectoryToRegisterMissingError
        If any of the specified directories to register do not exist.
    """
    project_name = name_pth or project_root.name
    pth_path = site_packages / f"{project_name}.pth"
    resolved_paths = []
    for rel_path in directories:
        abs_path = (project_root / rel_path).resolve()
        if not abs_path.exists():
            raise DirectoryToRegisterMissingError(abs_path)
        resolved_paths.append(abs_path)
    pth_path.write_text("\n".join(str(p) for p in resolved_paths) + "\n")
    return pth_path, resolved_paths


# --- CLI Command ----------------------------------------------------------------------------------

@app.command()
def register(
    directories: list[str] = typer.Argument(
        default=["src", "tests"],
        help="Paths to project directories to register, relative to the current working directory (defaults: ['src', 'tests'])."
    ),
    env_file: Path = typer.Option(
        default=Path("environment.yml"),
        exists=False,  # defer existence check to logic layer
        resolve_path=True,
        help="Path to the Conda environment file (default: `environment.yml`)."
    ),
    name_pth: Optional[str] = typer.Option(
        None,
        "--name-pth",
        help="Optional name for the .pth file (default: project root directory name)."
    )
) -> None:
    """
    Register project directories in the active Conda environment's site-packages.

    - Verifies that the active environment matches the one specified in the environment file.
    - Writes a `.pth` file pointing to the specified directories.

    Arguments
    ---------
    directories : list[str], default=['src', 'tests']
        List of subdirectory paths to register, relative to the current working directory.
    env_file : Path, default=Path("environment.yml")
        Path to the Conda environment specification file.
    name_pth : Optional[str], default=None
        Optional name for the `.pth` file. If not provided, defaults to the project root directory
        name.

    Raises
    ------
    EnvironmentFileNotFoundError
        If the specified environment file does not exist.
    InvalidEnvironmentFileError
        If the environment file does not contain a `name` field.
    CondaEnvironmentMismatchError
        If the active Conda environment does not match the expected one from the environment file.
    SitePackagesNotFoundError
        If the site-packages directory cannot be determined.
    DirectoryToRegisterMissingError
        If any of the specified directories to register do not exist.
    """
    project_root = Path.cwd()

    try:
        env_name = get_env_name(env_file)
        active_env = verify_active_conda_environment(env_name)
        logging.info(f"Verified Conda environment: '{active_env}'")
        site_packages = get_site_packages()
        pth_file, paths = register_project_paths(project_root, site_packages, directories=directories, name=name_pth)
        logging.info(f"Registered .pth file: {pth_file}")
        for path in paths:
            logging.info(f"  -> {path}")

    except EnvironmentFileNotFoundError as exc:
        logging.error(f"Environment file not found: {exc.path}")
        raise typer.Exit(code=1)

    except InvalidEnvironmentFileError as exc:
        logging.error(f"Missing 'name' field in environment file: {exc.path}")
        raise typer.Exit(code=1)

    except CondaEnvironmentMismatchError as exc:
        if exc.actual is None:
            logging.error("No active Conda environment detected.")
        else:
            logging.error(f"Active environment '{exc.actual}' does not match expected '{exc.expected}'")
        raise typer.Exit(code=1)

    except SitePackagesNotFoundError:
        logging.error("Failed to locate the site-packages directory for the current environment.")
        raise typer.Exit(code=1)

    except DirectoryToRegisterMissingError as exc:
        logging.error(f"Project directory not found: {exc.path}")
        raise typer.Exit(code=1)

    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        raise typer.Exit(code=1)


# --- Main Entry Point -----------------------------------------------------------------------------

if __name__ == "__main__":
    app()
