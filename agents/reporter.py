"""
reporter.py
Step 6 of the AgentForge pipeline.

Assembles all pipeline outputs into a structured final report.
Produces both a JSON-serializable dict and a human-readable plain-text summary.
No external dependencies — uses only the standard library.
"""

import json
from datetime import datetime

# Increment this when the pipeline behavior changes significantly
PIPELINE_VERSION = "1.0.0"


def generate_report(
    analyzed_task: dict,
    plan: dict,
    code_result: dict,
    validation: dict,
) -> dict:
    """
    Assemble the final report from all pipeline stages.

    Args:
        analyzed_task : output of task_analyzer.analyze_task()
        plan          : output of plan_generator.generate_plan()
        code_result   : output of code_generator.generate_code()
        validation    : output of validator.validate_code()

    Returns:
        A dict with keys:
            timestamp      (str)  - ISO format timestamp
            task           (str)  - original task text
            task_type      (str)  - detected task type
            complexity     (str)  - low / medium / high
            keywords       (list) - extracted keywords
            plan_steps     (list) - numbered implementation steps
            generated_code (str)  - the code template
            language       (str)  - programming language
            validation     (dict) - validation result summary
            status         (str)  - "success" or "failed"
            summary        (str)  - human-readable one-liner
    """
    status = "success" if validation.get("valid") else "failed"

    if status == "success":
        summary = (
            f"Task '{analyzed_task.get('task_text', '')}' completed successfully. "
            f"A {analyzed_task.get('complexity', 'low')}-complexity "
            f"{analyzed_task.get('task_type', 'general')} template was generated "
            f"and passed all validation checks."
        )
    else:
        error_list = ", ".join(validation.get("errors", ["unknown error"]))
        summary = (
            f"Task '{analyzed_task.get('task_text', '')}' completed with issues. "
            f"Validation errors: {error_list}"
        )

    report = {
        "pipeline_version": PIPELINE_VERSION,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "task": analyzed_task.get("task_text", ""),
        "task_type": analyzed_task.get("task_type", "general"),
        "complexity": analyzed_task.get("complexity", "low"),
        "keywords": analyzed_task.get("keywords", []),
        "plan_steps": plan.get("steps", []),
        "generated_code": code_result.get("code", ""),
        "language": code_result.get("language", "python"),
        "validation": {
            "valid": validation.get("valid", False),
            "checks": validation.get("checks", []),
            "errors": validation.get("errors", []),
        },
        "status": status,
        "summary": summary,
    }

    return report


def format_report(report: dict) -> str:
    """
    Format the report as a human-readable plain-text string.

    Args:
        report: The dict returned by generate_report().

    Returns:
        A multi-line string suitable for printing to the terminal.
    """
    sep = "=" * 60
    thin = "-" * 60

    lines = [
        sep,
        "  AGENTFORGE — PIPELINE REPORT",
        sep,
        f"  Timestamp  : {report['timestamp']}",
        f"  Status     : {report['status'].upper()}",
        f"  Task       : {report['task']}",
        f"  Type       : {report['task_type']}",
        f"  Complexity : {report['complexity']}",
        f"  Keywords   : {', '.join(report['keywords']) or 'none'}",
        thin,
        "  IMPLEMENTATION PLAN",
        thin,
    ]

    for step in report["plan_steps"]:
        lines.append(f"  {step}")

    lines += [
        thin,
        "  GENERATED CODE",
        thin,
    ]

    for code_line in report["generated_code"].splitlines():
        lines.append(f"  {code_line}")

    lines += [
        thin,
        "  VALIDATION",
        thin,
    ]

    for check in report["validation"]["checks"]:
        # Checks that are informational warnings — a failure does not block the pipeline
        WARNING_CHECKS = {"has_return"}

        if check["passed"]:
            icon = "PASS"
        elif check["check"] in WARNING_CHECKS:
            icon = "WARN"
        else:
            icon = "FAIL"
        lines.append(f"  [{icon}] {check['check']}")

    if report["validation"]["errors"]:
        lines.append("")
        lines.append("  Errors:")
        for err in report["validation"]["errors"]:
            lines.append(f"    - {err}")

    lines += [
        thin,
        f"  SUMMARY: {report['summary']}",
        sep,
    ]

    return "\n".join(lines)


def save_report(report: dict, filepath: str) -> None:
    """
    Save the report as a JSON file.

    Args:
        report   : The dict returned by generate_report().
        filepath : Destination file path (e.g. 'report.json').
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def save_report_to_s3(report: dict, bucket: str, s3_key: str) -> bool:
    """
    Save the report as a JSON object in an S3 bucket.

    boto3 is imported inside this function so that the rest of reporter.py
    works locally without boto3 installed. This function is additive —
    save_report() is completely unchanged.

    Args:
        report  : The dict returned by generate_report().
        bucket  : S3 bucket name (e.g. 'agentforge-reports').
        s3_key  : Object key (e.g. 'reports/2026-09-28/function/abc123.json').

    Returns:
        True if the upload succeeded, False if it failed.
    """
    try:
        import boto3  # noqa: PLC0415 — intentional late import; boto3 is
                      # available in the Lambda runtime and documented in requirements.txt for local development
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json.dumps(report, indent=2),
            ContentType="application/json",
        )
        return True
    except Exception as e:
        # Log the error without crashing the pipeline
        print(f"[reporter] S3 upload failed: {e}")
        return False
