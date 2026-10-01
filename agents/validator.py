"""
validator.py
Step 5 of the AgentForge pipeline.

Validates generated Python code using only the standard library:
- ast.parse()  : checks for syntax errors
- compile()    : confirms the code can be compiled to bytecode
- Basic checks : empty code, missing return, missing function/class definition
"""

import ast


def validate_code(code_result: dict) -> dict:
    """
    Validate the generated code from code_generator.

    Args:
        code_result: The dict returned by code_generator.generate_code(),
                     expected keys: task_type, language, code.

    Returns:
        A dict with keys:
            valid    (bool)   - True if all checks passed
            checks   (list)   - each check and its pass/fail status
            errors   (list)   - list of error messages (empty if valid)
    """
    code = code_result.get("code", "")
    checks = []
    errors = []

    # --- Check 1: Code is not empty ---
    if not code or not code.strip():
        errors.append("Generated code is empty.")
        checks.append({"check": "non_empty", "passed": False})
        return {"valid": False, "checks": checks, "errors": errors}

    checks.append({"check": "non_empty", "passed": True})

    # --- Check 2: Syntax check via ast.parse ---
    try:
        tree = ast.parse(code)
        checks.append({"check": "syntax", "passed": True})
    except SyntaxError as e:
        errors.append(f"Syntax error: {e.msg} (line {e.lineno})")
        checks.append({"check": "syntax", "passed": False})
        # Cannot continue further checks if syntax is broken
        return {"valid": False, "checks": checks, "errors": errors}

    # --- Check 3: Compile to bytecode ---
    try:
        compile(code, "<generated>", "exec")
        checks.append({"check": "compile", "passed": True})
    except Exception as e:
        errors.append(f"Compile error: {str(e)}")
        checks.append({"check": "compile", "passed": False})
        return {"valid": False, "checks": checks, "errors": errors}

    # --- Check 4: Contains at least one function or class definition ---
    has_def = any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in ast.walk(tree)
    )
    if has_def:
        checks.append({"check": "has_definition", "passed": True})
    else:
        errors.append("No function or class definition found in generated code.")
        checks.append({"check": "has_definition", "passed": False})

    # --- Check 5: At least one return statement inside a function body ---
    has_return = any(
        isinstance(node, ast.Return)
        for node in ast.walk(tree)
    )
    if has_return:
        checks.append({"check": "has_return", "passed": True})
    else:
        checks.append({"check": "has_return", "passed": False})
        # Warning only — does not invalidate the result

    valid = len(errors) == 0
    return {"valid": valid, "checks": checks, "errors": errors}
