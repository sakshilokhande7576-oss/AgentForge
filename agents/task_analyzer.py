"""
task_analyzer.py
Step 2 of the AgentForge pipeline.

Analyzes a raw task string and extracts:
- task_type : what kind of task it is (e.g. "function", "class", "script")
- keywords  : important words found in the task
- complexity : simple estimate — "low", "medium", or "high"
"""


# Words that hint at what kind of code the user wants
TASK_TYPE_HINTS = {
    "function": ["function", "def", "method", "compute", "calculate", "return"],
    "class": ["class", "object", "oop", "model", "entity"],
    "script": ["script", "automate", "run", "process", "parse", "read", "write", "file"],
    "api": ["api", "endpoint", "request", "response", "rest", "http", "url"],
    "test": ["test", "unit test", "assert", "verify", "check"],
}

# Words that raise complexity from low → medium or medium → high
COMPLEXITY_KEYWORDS = {
    "medium": ["loop", "list", "dict", "file", "input", "output", "multiple", "several"],
    "high": ["database", "api", "async", "class", "inherit", "recursive", "algorithm", "sort", "search"],
}

# Meta-words describing the task type itself — not useful as code identifiers
META_WORDS = {"function", "class", "script", "api", "test", "method", "object",
              "endpoint", "assert", "verify", "def"}


def analyze_task(task_text: str) -> dict:
    """
    Analyze the task text and return a structured dictionary.

    Args:
        task_text: The raw task description provided by the user.

    Returns:
        A dict with keys: task_text, task_type, keywords, complexity.
    """
    if not task_text or not task_text.strip():
        raise ValueError("Task text cannot be empty.")

    lower_text = task_text.lower()
    # Strip punctuation from each token so "string," and "return." are treated
    # the same as "string" and "return"
    words = [w.strip(".,!?;:\"'()[]{}") for w in lower_text.split()]

    # --- Detect task type ---
    detected_type = "general"  # default
    for task_type, hints in TASK_TYPE_HINTS.items():
        for hint in hints:
            if hint in lower_text:
                detected_type = task_type
                break
        if detected_type != "general":
            break

    # --- Extract keywords (words longer than 3 chars, skip common filler) ---
    stop_words = {"the", "a", "an", "is", "in", "on", "at", "to", "for",
                  "and", "or", "of", "that", "with", "this", "it", "be",
                  "should", "will", "can", "which", "from", "by", "write",
                  "create", "make", "build", "using", "use", "please"}
    keywords = [w for w in words if len(w) > 3 and w not in stop_words and w not in META_WORDS]
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    # --- Estimate complexity ---
    complexity = "low"
    for level in ("high", "medium"):
        for kw in COMPLEXITY_KEYWORDS[level]:
            if kw in lower_text:
                complexity = level
                break
        if complexity == level:
            break

    return {
        "task_text": task_text.strip(),
        "task_type": detected_type,
        "keywords": unique_keywords,
        "complexity": complexity,
    }
