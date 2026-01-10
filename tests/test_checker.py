import ast
from docstring_checker.main import DocstringExampleChecker


def run_checker(content: str, tmp_path) -> DocstringExampleChecker:
    """Helper to write content to a temp file and run the checker."""
    f = tmp_path / "example.py"
    f.write_text(content, encoding="utf-8")

    tree = ast.parse(content)
    checker = DocstringExampleChecker(str(f))
    checker.visit(tree)
    return checker


def test_public_function_pass(tmp_path):
    code = """
def my_func():
    '''
    Docs.
    Examples:
        >>> run()
    '''
    pass
"""
    checker = run_checker(code, tmp_path)
    assert not checker.errors
    assert checker.passed == 1


def test_public_function_fail(tmp_path):
    code = """
def my_func():
    '''Docs without examples.'''
    pass
"""
    checker = run_checker(code, tmp_path)
    assert len(checker.errors) == 1
    assert "missing examples section" in checker.errors[0]


def test_private_function_ignored(tmp_path):
    code = """
def _internal():
    '''No examples needed.'''
    pass
"""
    checker = run_checker(code, tmp_path)
    assert not checker.errors
    assert checker.total_checked == 0


def test_class_methods(tmp_path):
    code = """
class MyClass:
    '''
    Examples:
        >>> MyClass()
    '''
    def public_method(self):
        '''
        Examples:
            >>> 1 + 1
        '''
        pass

    def _private_method(self):
        pass
"""
    checker = run_checker(code, tmp_path)
    assert not checker.errors
    assert checker.passed == 2  # 1 class + 1 public method


def test_noqa_skip(tmp_path):
    code = """
def tricky_func():  # noqa: examples
    '''Docs without examples.'''
    pass
"""
    checker = run_checker(code, tmp_path)
    assert not checker.errors
    # It should count as skipped, so passed/checked shouldn't increment
    assert checker.total_checked == 0


def test_setter_ignored(tmp_path):
    code = """
class Data:
    '''
    Examples:
        >>> d = Data()
    '''
    @property
    def x(self):
        '''
        Examples:
             >>> d.x
        '''
        return 1

    @x.setter
    def x(self, val):
        '''Setter docs, no example needed.'''
        pass
"""
    checker = run_checker(code, tmp_path)
    
    # Assert is 2 because:
    # 1. Class 'Data' is checked
    # 2. Method 'x' (getter) is checked
    # The setter is correctly ignored (otherwise it would be 3).
    assert checker.total_checked == 2
    
    # Both the Class and the getter have valid examples, so both pass
    assert checker.passed == 2
    assert not checker.errors


def test_missing_docstring(tmp_path):
    code = """
def my_func():
    pass
"""
    checker = run_checker(code, tmp_path)
    assert len(checker.errors) == 1
    assert "missing a docstring" in checker.errors[0]
