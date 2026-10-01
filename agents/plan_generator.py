"""
plan_generator.py
Step 3 of the AgentForge pipeline.

Takes the analyzed task (output of task_analyzer) and produces
a numbered implementation plan as a list of steps.
"""


# Base steps that apply to every task
BASE_STEPS = [
    "Understand and restate the problem clearly.",
    "Identify inputs and expected outputs.",
    "Write the core logic.",
    "Handle edge cases and invalid inputs.",
    "Test the solution with sample data.",
]

# Extra steps added based on task type
EXTRA_STEPS_BY_TYPE = {
    "function": [
        "Define the function signature with clear parameter names.",
        "Add a docstring explaining what the function does.",
        "Return the result explicitly.",
    ],
    "class": [
        "Define the class with an __init__ method.",
        "Add relevant attributes and methods.",
        "Consider using __str__ for readable output.",
    ],
    "script": [
        "Define the script entry point using if __name__ == '__main__'.",
        "Read any required inputs (file, arguments, or user input).",
        "Write the output to the console or a file.",
    ],
    "api": [
        "Define the API endpoint and HTTP method.",
        "Validate incoming request data.",
        "Return a structured JSON response.",
    ],
    "test": [
        "Import the module or function being tested.",
        "Write at least one test for expected (happy path) behavior.",
        "Write at least one test for edge cases or error conditions.",
    ],
    "general": [],
}

# Extra steps for higher complexity
COMPLEXITY_STEPS = {
    "medium": ["Break the problem into smaller helper functions."],
    "high": [
        "Break the problem into smaller helper functions.",
        "Consider performance — avoid unnecessary loops or repeated work.",
        "Add logging or print statements for debugging.",
    ],
}


def generate_plan(analyzed_task: dict) -> dict:
    """
    Generate an implementation plan from an analyzed task.

    Args:
        analyzed_task: The dict returned by task_analyzer.analyze_task().

    Returns:
        A dict with keys: task_type, complexity, steps (list of strings).
    """
    task_type = analyzed_task.get("task_type", "general")
    complexity = analyzed_task.get("complexity", "low")

    # Build the step list
    steps = []
    steps.extend(EXTRA_STEPS_BY_TYPE.get(task_type, []))
    steps.extend(BASE_STEPS)
    steps.extend(COMPLEXITY_STEPS.get(complexity, []))

    # Number the steps (1-indexed)
    numbered_steps = [f"Step {i + 1}: {step}" for i, step in enumerate(steps)]

    return {
        "task_type": task_type,
        "complexity": complexity,
        "steps": numbered_steps,
    }
