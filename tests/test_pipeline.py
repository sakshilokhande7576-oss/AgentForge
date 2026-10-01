"""
test_pipeline.py
Unit tests for the AgentForge pipeline agents.

Run with:
  "C:\Program Files\Python310\python.exe" -m unittest tests/test_pipeline.py -v
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from agents.task_analyzer import analyze_task
from agents.plan_generator import generate_plan
from agents.code_generator import generate_code
from agents.validator import validate_code
from agents.reporter import generate_report, format_report


# ---------------------------------------------------------------------------
# task_analyzer tests
# ---------------------------------------------------------------------------

class TestTaskAnalyzer(unittest.TestCase):

    def test_returns_dict_with_required_keys(self):
        result = analyze_task("Write a function to add two numbers")
        self.assertIn("task_text", result)
        self.assertIn("task_type", result)
        self.assertIn("keywords", result)
        self.assertIn("complexity", result)

    def test_detects_function_type(self):
        result = analyze_task("Write a function to calculate the sum")
        self.assertEqual(result["task_type"], "function")

    def test_detects_class_type(self):
        result = analyze_task("Create a class to model a user object")
        self.assertEqual(result["task_type"], "class")

    def test_detects_script_type(self):
        result = analyze_task("Write a script to parse a CSV file")
        self.assertEqual(result["task_type"], "script")

    def test_complexity_low_by_default(self):
        result = analyze_task("Write a function to say hello")
        self.assertEqual(result["complexity"], "low")

    def test_complexity_high_for_algorithm(self):
        result = analyze_task("Implement a recursive sorting algorithm")
        self.assertEqual(result["complexity"], "high")

    def test_empty_task_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_task("")

    def test_whitespace_only_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_task("   ")

    def test_keywords_are_list(self):
        result = analyze_task("Write a function to reverse a string")
        self.assertIsInstance(result["keywords"], list)

    def test_keywords_no_duplicates(self):
        result = analyze_task("function function function")
        self.assertEqual(len(result["keywords"]), len(set(result["keywords"])))

    def test_meta_words_excluded_from_keywords(self):
        result = analyze_task("Write a function to reverse a string")
        self.assertNotIn("function", result["keywords"])
        self.assertIn("reverse", result["keywords"])

    def test_punctuation_stripped_from_keywords(self):
        result = analyze_task("Write a function to reverse a string, and return it.")
        # "string," should be cleaned to "string", not appear with punctuation
        self.assertNotIn("string,", result["keywords"])
        self.assertIn("string", result["keywords"])


# ---------------------------------------------------------------------------
# plan_generator tests
# ---------------------------------------------------------------------------

class TestPlanGenerator(unittest.TestCase):

    def _make_analyzed(self, task_type="function", complexity="low"):
        return {
            "task_text": "Write a function",
            "task_type": task_type,
            "keywords": ["calculate"],
            "complexity": complexity,
        }

    def test_returns_dict_with_required_keys(self):
        result = generate_plan(self._make_analyzed())
        self.assertIn("task_type", result)
        self.assertIn("complexity", result)
        self.assertIn("steps", result)

    def test_steps_is_non_empty_list(self):
        result = generate_plan(self._make_analyzed())
        self.assertIsInstance(result["steps"], list)
        self.assertGreater(len(result["steps"]), 0)

    def test_steps_are_numbered(self):
        result = generate_plan(self._make_analyzed())
        self.assertTrue(result["steps"][0].startswith("Step 1:"))

    def test_high_complexity_adds_extra_steps(self):
        low_result = generate_plan(self._make_analyzed(complexity="low"))
        high_result = generate_plan(self._make_analyzed(complexity="high"))
        self.assertGreater(len(high_result["steps"]), len(low_result["steps"]))


# ---------------------------------------------------------------------------
# code_generator tests
# ---------------------------------------------------------------------------

class TestCodeGenerator(unittest.TestCase):

    def _make_analyzed(self, task_type="function", keywords=None):
        return {
            "task_text": "Write a function",
            "task_type": task_type,
            "keywords": keywords if keywords is not None else ["calculate"],
            "complexity": "low",
        }

    def test_returns_dict_with_required_keys(self):
        result = generate_code(self._make_analyzed())
        self.assertIn("task_type", result)
        self.assertIn("language", result)
        self.assertIn("code", result)

    def test_language_is_python(self):
        result = generate_code(self._make_analyzed())
        self.assertEqual(result["language"], "python")

    def test_code_is_non_empty_string(self):
        result = generate_code(self._make_analyzed())
        self.assertIsInstance(result["code"], str)
        self.assertTrue(result["code"].strip())

    def test_function_template_uses_keyword_as_name(self):
        result = generate_code(self._make_analyzed(task_type="function", keywords=["compute"]))
        self.assertIn("def compute", result["code"])

    def test_reserved_keyword_falls_back_to_solution(self):
        result = generate_code(self._make_analyzed(task_type="function", keywords=["return"]))
        self.assertIn("def solution", result["code"])

    def test_invalid_identifier_falls_back_to_solution(self):
        result = generate_code(self._make_analyzed(task_type="function", keywords=["123bad"]))
        self.assertIn("def solution", result["code"])

    def test_class_normal_keyword_produces_capitalized_name(self):
        # "user".capitalize().replace("-", "") → "User" — valid identifier
        result = generate_code(self._make_analyzed(task_type="class", keywords=["user"]))
        self.assertIn("class User", result["code"])

    def test_class_invalid_identifier_falls_back_to_Solution(self):
        # "123abc".capitalize().replace("-", "") → "123abc" — not a valid identifier
        result = generate_code(self._make_analyzed(task_type="class", keywords=["123abc"]))
        self.assertIn("class Solution", result["code"])

    def test_general_type_produces_code(self):
        result = generate_code(self._make_analyzed(task_type="general"))
        self.assertIn("def solution", result["code"])


# ---------------------------------------------------------------------------
# validator tests
# ---------------------------------------------------------------------------

class TestValidator(unittest.TestCase):

    def _make_code_result(self, code):
        return {"task_type": "function", "language": "python", "code": code}

    def test_valid_code_passes(self):
        code = "def hello():\n    return 'hello'\n"
        result = validate_code(self._make_code_result(code))
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])

    def test_empty_code_fails(self):
        result = validate_code(self._make_code_result(""))
        self.assertFalse(result["valid"])
        self.assertTrue(len(result["errors"]) > 0)

    def test_syntax_error_fails(self):
        code = "def broken(\n    return 1\n"
        result = validate_code(self._make_code_result(code))
        self.assertFalse(result["valid"])
        self.assertTrue(any("yntax" in e for e in result["errors"]))

    def test_no_definition_fails(self):
        code = "x = 1\ny = 2\n"
        result = validate_code(self._make_code_result(code))
        self.assertFalse(result["valid"])

    def test_checks_list_is_returned(self):
        code = "def ok():\n    pass\n"
        result = validate_code(self._make_code_result(code))
        self.assertIsInstance(result["checks"], list)
        self.assertGreater(len(result["checks"]), 0)

    def test_function_with_return_passes_has_return(self):
        code = "def greet(name):\n    return 'Hello ' + name\n"
        result = validate_code(self._make_code_result(code))
        return_check = next(c for c in result["checks"] if c["check"] == "has_return")
        self.assertTrue(return_check["passed"])

    def test_function_without_return_fails_has_return(self):
        code = "def greet(name):\n    print('Hello')\n"
        result = validate_code(self._make_code_result(code))
        return_check = next(c for c in result["checks"] if c["check"] == "has_return")
        self.assertFalse(return_check["passed"])
        # valid should still be True — has_return is a warning, not a hard failure
        self.assertTrue(result["valid"])


# ---------------------------------------------------------------------------
# reporter tests
# ---------------------------------------------------------------------------

class TestReporter(unittest.TestCase):

    def _build_inputs(self):
        analyzed = {
            "task_text": "Write a function to add numbers",
            "task_type": "function",
            "keywords": ["numbers"],
            "complexity": "low",
        }
        plan = {"task_type": "function", "complexity": "low", "steps": ["Step 1: Do something"]}
        code_result = {"task_type": "function", "language": "python", "code": "def numbers(v):\n    return v\n"}
        validation = {"valid": True, "checks": [{"check": "syntax", "passed": True}], "errors": []}
        return analyzed, plan, code_result, validation

    def test_report_has_required_keys(self):
        report = generate_report(*self._build_inputs())
        for key in ("pipeline_version", "timestamp", "task", "task_type",
                    "complexity", "plan_steps", "generated_code", "language",
                    "validation", "status", "summary"):
            self.assertIn(key, report)

    def test_report_pipeline_version_is_string(self):
        report = generate_report(*self._build_inputs())
        self.assertIsInstance(report["pipeline_version"], str)
        self.assertTrue(len(report["pipeline_version"]) > 0)

    def test_status_is_success_when_valid(self):
        report = generate_report(*self._build_inputs())
        self.assertEqual(report["status"], "success")

    def test_status_is_failed_when_invalid(self):
        analyzed, plan, code_result, validation = self._build_inputs()
        validation["valid"] = False
        validation["errors"] = ["Syntax error"]
        report = generate_report(analyzed, plan, code_result, validation)
        self.assertEqual(report["status"], "failed")

    def test_format_report_returns_string(self):
        report = generate_report(*self._build_inputs())
        formatted = format_report(report)
        self.assertIsInstance(formatted, str)
        self.assertIn("AGENTFORGE", formatted)

    def test_format_report_shows_warn_for_has_return_failure(self):
        # has_return failed but valid is True — should render [WARN]
        analyzed, plan, code_result, validation = self._build_inputs()
        validation["checks"] = [
            {"check": "non_empty",      "passed": True},
            {"check": "syntax",         "passed": True},
            {"check": "compile",        "passed": True},
            {"check": "has_definition", "passed": True},
            {"check": "has_return",     "passed": False},
        ]
        report = generate_report(analyzed, plan, code_result, validation)
        formatted = format_report(report)
        self.assertIn("[WARN] has_return", formatted)
        self.assertNotIn("[FAIL] has_return", formatted)

    def test_format_report_shows_fail_for_hard_failure(self):
        # syntax failed — should render [FAIL], not [WARN]
        analyzed, plan, code_result, validation = self._build_inputs()
        validation["checks"] = [
            {"check": "non_empty", "passed": True},
            {"check": "syntax",    "passed": False},
        ]
        report = generate_report(analyzed, plan, code_result, validation)
        formatted = format_report(report)
        self.assertIn("[FAIL] syntax", formatted)
        self.assertNotIn("[WARN] syntax", formatted)


# ---------------------------------------------------------------------------
# lambda_handler tests
# All tests mock save_report_to_s3 — zero real AWS calls are made.
# ---------------------------------------------------------------------------

from lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    def test_valid_task_returns_200(self):
        event = {"body": json.dumps({"task": "Write a function to reverse a string"})}
        with patch("lambda_function.save_report_to_s3", return_value=True):
            response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body["status"], "success")

    def test_missing_task_returns_400(self):
        event = {"body": json.dumps({})}
        # No S3 call expected on a 400 — no mock needed, but safe to include
        with patch("lambda_function.save_report_to_s3", return_value=True):
            response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)

    def test_empty_body_returns_400(self):
        event = {"body": ""}
        with patch("lambda_function.save_report_to_s3", return_value=True):
            response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)

    def test_response_contains_required_fields(self):
        event = {"body": json.dumps({"task": "Write a script to parse a file"})}
        with patch("lambda_function.save_report_to_s3", return_value=True):
            response = lambda_handler(event, None)
        body = json.loads(response["body"])
        for field in ("pipeline_version", "status", "task_type",
                      "complexity", "summary", "timestamp",
                      "report_s3_key", "s3_upload"):
            self.assertIn(field, body)

    def test_s3_upload_success_reflected_in_response(self):
        event = {"body": json.dumps({"task": "Write a function to add numbers"})}
        with patch("lambda_function.save_report_to_s3", return_value=True):
            response = lambda_handler(event, None)
        body = json.loads(response["body"])
        self.assertEqual(body["s3_upload"], "success")
        self.assertIsNotNone(body["report_s3_key"])

    def test_s3_upload_failure_reflected_in_response(self):
        # S3 upload fails — response must clearly say 'failed', not pretend success
        event = {"body": json.dumps({"task": "Write a function to add numbers"})}
        with patch("lambda_function.save_report_to_s3", return_value=False):
            response = lambda_handler(event, None)
        body = json.loads(response["body"])
        self.assertEqual(body["s3_upload"], "failed")
        self.assertIsNone(body["report_s3_key"])
        # Pipeline itself still succeeded — status is independent of S3
        self.assertEqual(body["status"], "success")


# ---------------------------------------------------------------------------
# reporter S3 tests — all boto3 calls are mocked, zero real AWS calls
# ---------------------------------------------------------------------------

from agents.reporter import save_report_to_s3
import sys
import types


def _make_mock_boto3(mock_s3_client):
    """Build a minimal fake boto3 module whose .client() returns mock_s3_client."""
    fake_boto3 = types.ModuleType("boto3")
    fake_boto3.client = MagicMock(return_value=mock_s3_client)
    return fake_boto3


class TestReporterS3(unittest.TestCase):

    def _sample_report(self):
        return {
            "pipeline_version": "1.0.0",
            "timestamp": "2026-09-28T09:53:04Z",
            "task": "Write a function to reverse a string",
            "status": "success",
        }

    def test_save_report_to_s3_calls_put_object(self):
        mock_s3 = MagicMock()
        fake_boto3 = _make_mock_boto3(mock_s3)
        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            save_report_to_s3(self._sample_report(), "agentforge-reports", "reports/test/key.json")

        fake_boto3.client.assert_called_once_with("s3")
        mock_s3.put_object.assert_called_once()
        call_kwargs = mock_s3.put_object.call_args[1]
        self.assertEqual(call_kwargs["Bucket"], "agentforge-reports")
        self.assertEqual(call_kwargs["Key"], "reports/test/key.json")
        self.assertEqual(call_kwargs["ContentType"], "application/json")

    def test_save_report_to_s3_body_is_valid_json(self):
        mock_s3 = MagicMock()
        fake_boto3 = _make_mock_boto3(mock_s3)
        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            save_report_to_s3(self._sample_report(), "agentforge-reports", "reports/test/key.json")

        body = mock_s3.put_object.call_args[1]["Body"]
        parsed = json.loads(body)
        self.assertEqual(parsed["status"], "success")

    def test_save_report_to_s3_returns_true_on_success(self):
        mock_s3 = MagicMock()
        fake_boto3 = _make_mock_boto3(mock_s3)
        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            result = save_report_to_s3(
                self._sample_report(), "agentforge-reports", "reports/test/key.json"
            )
        self.assertTrue(result)

    def test_save_report_to_s3_returns_false_on_error(self):
        # S3 call raises — must return False, not raise
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = Exception("S3 unavailable")
        fake_boto3 = _make_mock_boto3(mock_s3)
        with patch.dict(sys.modules, {"boto3": fake_boto3}):
            result = save_report_to_s3(
                self._sample_report(), "agentforge-reports", "reports/test/key.json"
            )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
