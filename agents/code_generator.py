"""
code_generator.py
Step 4 of the AgentForge pipeline.

Generates a Python code template based on the task type and keywords.
No LLM or external API is used — this is a rule-based template generator.
In a future phase, this will be replaced by an Amazon Bedrock call.
"""

import keyword


def _safe_identifier(raw: str, fallback: str) -> str:
    """
    Return `raw` if it is a valid Python identifier and not a reserved keyword.
    Otherwise return `fallback`.

    Args:
        raw:      Candidate identifier string.
        fallback: Safe name to use when raw is invalid.

    Returns:
        A safe Python identifier string.
    """
    if raw and raw.isidentifier() and not keyword.iskeyword(raw):
        return raw
    return fallback


def _build_function_template(keywords: list) -> str:
    """Generate a Python function template."""
    raw = keywords[0].replace("-", "_") if keywords else ""
    func_name = _safe_identifier(raw, "solution")

    return f'''\
def {func_name}(value):
    """
    TODO: Implement the logic for '{func_name}'.

    Args:
        value: The input to process.

    Returns:
        The computed result.
    """
    # Step 1: Validate input
    if value is None:
        raise ValueError("Input cannot be None.")

    # Step 2: Core logic (replace this with your implementation)
    result = value  # placeholder

    return result


if __name__ == "__main__":
    # Quick smoke test
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
    TODO: Implement the {class_name} class.
    """

    def __init__(self, name: str):
        """Initialize with a name."""
        self.name = name

    def process(self):
        """
        TODO: Add the core processing logic here.

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
    """
    TODO: Implement the main script logic here.
    """
    # Step 1: Read input (from args or a file)
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = "default_input"

    # Step 2: Process the input
    result = process(input_data)

    # Step 3: Output the result
    print("Result:", result)


def process(data: str) -> str:
    """
    TODO: Replace with actual processing logic.

    Args:
        data: Input string to process.

    Returns:
        Processed result as a string.
    """
    return data.strip().upper()  # placeholder transformation


if __name__ == "__main__":
    main()
'''


def _build_general_template() -> str:
    """Fallback template for unrecognized task types."""
    return '''\
def solution(input_data):
    """
    TODO: Implement your solution here.

    Args:
        input_data: The input to your solution.

    Returns:
        The output of your solution.
    """
    # Write your logic here
    result = None  # placeholder

    return result


if __name__ == "__main__":
    print(solution("test"))
'''


# Map task types to their builder functions
TEMPLATE_BUILDERS = {
    "function": _build_function_template,
    "class": _build_class_template,
    "script": _build_script_template,
}


def generate_code(analyzed_task: dict) -> dict:
    """
    Generate a Python code template based on the analyzed task.

    Args:
        analyzed_task: The dict returned by task_analyzer.analyze_task().

    Returns:
        A dict with keys: task_type, code (string), language.
    """
    task_type = analyzed_task.get("task_type", "general")
    keywords = analyzed_task.get("keywords", [])

    builder = TEMPLATE_BUILDERS.get(task_type)

    if builder:
        # class template doesn't need keywords the same way, but we pass them anyway
        code = builder(keywords)
    else:
        code = _build_general_template()

    return {
        "task_type": task_type,
        "language": "python",
        "code": code,
    }
