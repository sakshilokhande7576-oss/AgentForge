"""
lambda_function.py
AWS Lambda handler for AgentForge.

Wraps the existing local pipeline (main.py:run_pipeline) in a
Lambda-compatible handler. This file is the only AWS-specific code
in the project — all pipeline logic stays in the agents/ package.

Triggered by: API Gateway POST /tasks
Expected event body: { "task": "Write a function to reverse a string" }

Response format (API Gateway Lambda proxy integration):
{
    "statusCode": 200,
    "headers": { "Content-Type": "application/json" },
    "body": "<JSON string>"
}

S3 report upload is implemented through the reporter module.
boto3 is available in Lambda's runtime by default (no extra dependency).
"""

import json
import uuid

from main import run_pipeline
from agents.reporter import save_report_to_s3


def lambda_handler(event, context):
    """
    AWS Lambda entry point.

    Args:
        event   : dict — the API Gateway proxy event
        context : LambdaContext — runtime info (not used here)

    Returns:
        dict — API Gateway proxy response
    """
    # --- Parse input ---
    try:
        body = event.get("body", "")
        if isinstance(body, str):
            body = json.loads(body) if body else {}
        task_text = body.get("task", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return _error_response(400, "Invalid request body. Expected JSON with 'task' field.")

    if not task_text:
        return _error_response(400, "Missing required field: 'task'.")

    # --- Run the pipeline ---
    try:
        report = run_pipeline(task_text)
    except ValueError as e:
        return _error_response(400, str(e))
    except Exception as e:
        return _error_response(500, f"Pipeline error: {str(e)}")

    # --- Save report to S3 (Phase 2) ---
    ts = report.get("timestamp", "unknown").replace(":", "-")
    task_type = report.get("task_type", "general")
    task_id = uuid.uuid4().hex[:8]
    s3_key = f"reports/{ts}/{task_type}/{task_id}.json"

    s3_saved = save_report_to_s3(report, bucket="agentforge-reports", s3_key=s3_key)

    # --- Return success response ---
    response_body = {
        "pipeline_version": report.get("pipeline_version"),
        "status": report.get("status"),
        "task_type": report.get("task_type"),
        "complexity": report.get("complexity"),
        "summary": report.get("summary"),
        "timestamp": report.get("timestamp"),
        "report_s3_key": s3_key if s3_saved else None,
        "s3_upload": "success" if s3_saved else "failed",
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body),
    }


def _error_response(status_code: int, message: str) -> dict:
    """
    Build a structured error response for API Gateway.

    Args:
        status_code : HTTP status code (400, 500, etc.)
        message     : Human-readable error message.

    Returns:
        API Gateway proxy response dict.
    """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message}),
    }
