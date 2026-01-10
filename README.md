# Docstring Example Checker

A Python pre-commit hook that enforces the presence of an "Examples" section in the docstrings of public classes and functions.

This tool helps maintain high-quality documentation by ensuring that all public APIs include usage examples or doctests.

## Features

* **Public API Focus:** Automatically checks public classes, functions, and methods (skips names starting with `_`).
* **Smart Filtering:** Automatically ignores property setters and dunder methods.
* **Validation:** looks for the keyword `Examples` or Python doctest chevrons (`>>>`) in the docstring.
* **Manual Exclusions:** Supports `# noqa: examples` to skip specific objects.
* **Zero Dependencies:** Built using Python's standard library (`ast`), making it lightweight and fast.

## Installation & Usage

### As a Pre-commit Hook (Recommended)

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: [https://github.com/mabdullahsoyturk/docstring-checker](https://github.com/mabdullahsoyturk/docstring-checker)
    rev: v0.1.0  # Use the latest release tag
    hooks:
      - id: check-docstring-examples
```

### Configuration

You can pass arguments to the hook in your pre-commit config. For example, to enable verbose mode (which prints a summary table of passed/checked objects):

```yaml
    hooks:
      - id: check-docstring-examples
        args: ["--verbose"]
```

### Manual Usage

You can also install and run the tool manually via pip if you have the package installed:

```bash
uv pip install git+[https://github.com/mabdullahsoyturk/docstring-checker.git](https://github.com/mabdullahsoyturk/docstring-checker.git)

# Run on specific files
check-docstring-examples src/my_project/main.py

# Run with verbose summary
check-docstring-examples src/ -v
```

## Rules & Logic
The checker enforces the following rules:

1. **Public Objects Only**: It only checks objects that do not start with an underscore (_).
    - ``def my_func():`` -> Checked
    - ``def _internal():`` -> Ignored
2. **Required Markers**: The docstring must contain either:
    - The word ``Examples``
    - The Python console marker ``>>>``
3. **Property Setters**: Decorators matching ``@*.setter`` are automatically ignored.

### Ignoring Specific Functions
If you have a public function that truly does not need an example, you can skip it by 
adding # noqa: examples on the line where the function is defined:

```Python
def simple_helper():  # noqa: examples
    """This docstring does not need an example section."""
    return True
```

## Development

This project uses uv for dependency management.

### Setup
```bash
git clone [https://github.com/mabdullahsoyturk/docstring-checker.git](https://github.com/mabdullahsoyturk/docstring-checker.git)
cd docstring-checker
uv sync
```

### Running Tests
This project uses pytest for testing.

```bash
uv run pytest
```
