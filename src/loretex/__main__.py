"""
Entry point for the `loretex` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m loretex


See Also
--------
loretex.cli: Module implementing the application's command-line interface.
"""
from .cli import app

app()
