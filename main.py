"""
main.py
Entry point for the AgentForge local prototype.

Runs the full 6-step pipeline from the command line:
  1. Accept task input
  2. Analyze the task
  3. Generate an implementation plan
  4. Generate a code template
  5. Validate the code
  6. Produce and display the final report

Usage:
  "C:\Program Files\Python310\python.exe" main.py
  "C:\Program Files\Python310\python.exe" main.py "Write a function to reverse a string"
"""

import sys
import json

from agents.task_analyzer import analyze_task
from agents.plan_generator import generate_plan
from agents.code_generator import generate_code
from agents.validator import validate_code
from agents.reporter import generate_report, format_report, save_report


def run_pipeline(task_text: str) -> dict:
    """
    Execute the full AgentForge pipeline for a given task.

    Args:
        task_text: The raw software task description.

    Returns:
        The final report dict.
    """
    print("\n[1/6] Analyzing task...")
    analyzed = analyze_task(task_text)

    print("[2/6] Generating implementation plan...")
    plan = generate_plan(analyzed)

    print("[3/6] Generating code template...")
    code_result = generate_code(analyzed)

    print("[4/6] Validating generated code...")
    validation = validate_code(code_result)

    print("[5/6] Assembling report...")
    report = generate_report(analyzed, plan, code_result, validation)

    print("[6/6] Done.\n")
    return report


def main():
    # Get task from command-line argument or prompt the user
    if len(sys.argv) > 1:
        task_text = " ".join(sys.argv[1:])
    else:
        print("AgentForge — AI-Powered Software Task Automation")
        print("=" * 50)
        task_text = input("Enter your software task: ").strip()

    if not task_text:
        print("Error: No task provided. Please enter a task description.")
        sys.exit(1)

    # Run the pipeline
    report = run_pipeline(task_text)

    # Display the formatted report
    print(format_report(report))

    # Save JSON report to disk
    output_file = "report.json"
    save_report(report, output_file)
    print(f"\nJSON report saved to: {output_file}\n")


if __name__ == "__main__":
    main()
