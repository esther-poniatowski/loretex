"""
Command-line entry point for the loretex package.

This entry point loads a YAML specification file and performs Markdown-to-LaTeX conversion for all
listed notes.

Usage
-----
To convert Markdown notes to LaTeX files from a YAML specification file, run:

```sh
python -m loretex path/to/spec.yml
```

Arguments
---------
spec_path : Path
    Path to the YAML specification file that defines the Markdown notes to convert.

See Also
--------
loretex.cli: Command-line interface module for the loretex package.
"""
from loretex.cli import app

if __name__ == "__main__":
    app()
