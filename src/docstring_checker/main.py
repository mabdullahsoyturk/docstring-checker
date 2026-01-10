import ast
import sys
import argparse
from pathlib import Path

REQUIRED_MARKERS = ("Examples", ">>>")


class DocstringExampleChecker(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        self.class_stack = []
        self.total_checked = 0
        self.passed = 0

    def visit_ClassDef(self, node):
        if self._is_public(node.name):
            self._check_docstring(node, kind="class")
            self.class_stack.append(node)
            self.generic_visit(node)
            self.class_stack.pop()
        else:
            # Still visit children so public methods inside private classes
            # are ignored automatically
            pass

    def visit_FunctionDef(self, node):
        self._handle_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._handle_function(node)
        self.generic_visit(node)

    def _handle_function(self, node):
        # Skip private and dunder functions
        if not self._is_public(node.name):
            return

        # Skip property setters
        if self._is_setter(node):
            return

        # Top-level function
        if not self.class_stack:
            self._check_docstring(node, kind="function")
            return

        # Method inside a public class
        parent_class = self.class_stack[-1]
        if self._is_public(parent_class.name):
            self._check_docstring(node, kind="method")

    def _has_noqa_examples(self, node) -> bool:
        if not hasattr(node, "lineno"):
            return False

        try:
            with open(self.filename, encoding="utf-8") as f:
                line = f.readlines()[node.lineno - 1]
        except OSError:
            return False

        return "noqa: examples" in line.lower()

    def _check_docstring(self, node, kind: str):
        # Skip via noqa, decorators
        if self._has_noqa_examples(node):
            return

        self.total_checked += 1

        doc = ast.get_docstring(node)
        if not doc:
            self.errors.append(
                f"{self.filename}:{node.lineno}: "
                f"Public {kind} '{node.name}' is missing a docstring"
            )
            return

        if not any(marker in doc for marker in REQUIRED_MARKERS):
            self.errors.append(
                f"{self.filename}:{node.lineno}: "
                f"Public {kind} '{node.name}' docstring missing examples section"
            )
            return

        self.passed += 1

    @staticmethod
    def _is_public(name: str) -> bool:
        return not name.startswith("_")

    def _is_setter(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        for deco in node.decorator_list:
            # @x.setter
            if isinstance(deco, ast.Attribute) and deco.attr == "setter":
                return True
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check public docstrings for examples section."
    )
    parser.add_argument(
        "filenames", 
        nargs="*", 
        help="List of files to check"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Print summary of checked objects"
    )
    
    args = parser.parse_args()

    total_checked = 0
    total_passed = 0
    exit_code = 0

    # Iterate over the files collected by argparse
    for filename in args.filenames:
        if not filename.endswith(".py"):
            continue

        try:
            tree = ast.parse(Path(filename).read_text(encoding="utf-8"), filename)
        except SyntaxError:
            continue

        checker = DocstringExampleChecker(filename)
        checker.visit(tree)

        # Print per-object errors immediately (always printed on failure)
        for error in checker.errors:
            print(error)

        # Aggregate totals
        total_checked += checker.total_checked
        total_passed += checker.passed

        if checker.errors:
            exit_code = 1

    # Only print the summary table if --verbose is flag is set
    if args.verbose and total_checked:
        print(
            f"\nDocstring examples: "
            f"{total_passed} / {total_checked} public objects passed"
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()