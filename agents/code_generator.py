"""
code_generator.py
Step 4 of the AgentForge pipeline.

Generates Python code based on the task type and keywords.
No LLM or external API is used — this is a rule-based generator.
"""

import keyword


def _safe_identifier(raw: str, fallback: str) -> str:
    """
    Return raw if it is a valid Python identifier and not a keyword.
    Otherwise return fallback.
    """
    if raw and raw.isidentifier() and not keyword.iskeyword(raw):
        return raw

    return fallback


def _build_calculator_template() -> str:
    """
    Generate a complete calculator application with unit tests.
    """

    return '''\
def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def subtract(a, b):
    """Return the difference between two numbers."""
    return a - b


def multiply(a, b):
    """Return the product of two numbers."""
    return a * b


def divide(a, b):
    """Return the quotient of two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")

    return a / b


def calculate(a, b, operation):
    """
    Perform a calculator operation.

    Supported operations:
        add
        subtract
        multiply
        divide
    """

    if operation == "add":
        return add(a, b)

    if operation == "subtract":
        return subtract(a, b)

    if operation == "multiply":
        return multiply(a, b)

    if operation == "divide":
        return divide(a, b)

    raise ValueError("Unsupported operation.")


def run_tests():
    """Run basic unit tests for the calculator."""

    assert add(2, 3) == 5
    assert subtract(5, 3) == 2
    assert multiply(4, 3) == 12
    assert divide(10, 2) == 5

    try:
        divide(10, 0)
        raise AssertionError("Division by zero should raise ValueError.")
    except ValueError:
        pass

    assert calculate(2, 3, "add") == 5
    assert calculate(5, 3, "subtract") == 2
    assert calculate(4, 3, "multiply") == 12
    assert calculate(10, 2, "divide") == 5

    print("All calculator tests passed.")


if __name__ == "__main__":
    print("2 + 3 =", add(2, 3))
    print("5 - 3 =", subtract(5, 3))
    print("4 * 3 =", multiply(4, 3))
    print("10 / 2 =", divide(10, 2))

    run_tests()
'''


def _build_function_template(keywords: list) -> str:
    """Generate a Python function template."""

    raw = str(keywords[0]).replace("-", "_") if keywords else ""
    func_name = _safe_identifier(raw, "solution")

    return f'''\
def {func_name}(value):
    """
    Process the supplied value.

    Args:
        value: The input to process.

    Returns:
        The processed result.
    """

    if value is None:
        raise ValueError("Input cannot be None.")

    result = value

    return result


if __name__ == "__main__":
    output = {func_name}("example_input")
    print("Output:", output)
'''


def _build_class_template(keywords: list) -> str:
    """Generate a Python class template."""

    raw = keywords[0].capitalize().replace("-", "") if keywords else ""
    class_name = _safe_identifier(raw, "Solution")

    return f'''\
class {class_name}:
    """
    Generated solution class.
    """

    def __init__(self, name: str):
        """Initialize the object."""
        self.name = name

    def process(self):
        """
        Process the stored name.

        Returns:
            A result string.
        """
        return f"Processing: {{self.name}}"

    def __str__(self):
        return f"{class_name}(name={{self.name!r}})"


if __name__ == "__main__":
    obj = {class_name}("example")
    print(obj.process())
'''


def _build_script_template(keywords: list) -> str:
    """Generate a Python script template."""

    return '''\
import sys


def main():
    """Main entry point for the generated script."""

    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = "default_input"

    result = process(input_data)

    print("Result:", result)


def process(data: str) -> str:
    """
    Process input data.

    Args:
        data: Input string.

    Returns:
        Processed string.
    """

    if not isinstance(data, str):
        raise ValueError("data must be a string")

    return data.strip().upper()


if __name__ == "__main__":
    main()
'''


def _build_general_template() -> str:
    """Generate a fallback template for unknown task types."""

    return '''\
def solution(input_data):
    """
    General solution function.

    Args:
        input_data: Input to the solution.

    Returns:
        Result of the solution.
    """

    if input_data is None:
        raise ValueError("input_data cannot be None")

    result = input_data

    return result


if __name__ == "__main__":
    print(solution("test"))
'''


# Map task types to their builder functions.
TEMPLATE_BUILDERS = {
    "calculator": lambda keywords: _build_calculator_template(),
    "function": _build_function_template,
    "class": _build_class_template,
    "script": _build_script_template,
}


def generate_code(analyzed_task: dict) -> dict:
    """
    Generate Python code based on the analyzed task.

    Args:
        analyzed_task:
            Dictionary returned by analyze_task().

    Returns:
        Dictionary containing task_type, language, code, and keywords.
    """

    if not isinstance(analyzed_task, dict):
        raise TypeError("analyzed_task must be a dictionary")

    task_type = analyzed_task.get("task_type", "general")
    keywords = analyzed_task.get("keywords", [])

    if not isinstance(keywords, list):
        keywords = list(keywords) if keywords else []

    builder = TEMPLATE_BUILDERS.get(task_type)

    if builder is not None:
        code = builder(keywords)
    else:
        code = _build_general_template()

    return {
        "task_type": task_type,
        "language": "python",
        "code": code,
        "keywords": keywords,
    }