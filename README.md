# AgentForge

**AI-Powered Software Task Automation Platform**

AgentForge is a portfolio project demonstrating agentic AI pipeline design, Python engineering, code validation, and AWS-ready architecture.

It accepts a plain-English software task and processes it through an automated pipeline that analyzes the task, creates an implementation plan, generates a Python code template, validates the generated code, and produces a structured report.

---

## What it does

AgentForge processes a software task through six stages:

| Step | Component        | Description                                                      |
| ---- | ---------------- | ---------------------------------------------------------------- |
| 1    | `main.py`        | Accepts the software task                                        |
| 2    | `task_analyzer`  | Classifies the task, extracts keywords, and estimates complexity |
| 3    | `plan_generator` | Produces a numbered implementation plan                          |
| 4    | `code_generator` | Generates a Python code template                                 |
| 5    | `validator`      | Validates generated code using AST and compile checks            |
| 6    | `reporter`       | Builds and saves the structured final report                     |

The project also includes an AWS Lambda-compatible handler that can save generated reports to Amazon S3.

---

## Architecture

```text
Software Task
     |
     v
+------------------+
|  Task Analyzer   |
+------------------+
     |
     v
+------------------+
|  Plan Generator  |
+------------------+
     |
     v
+------------------+
|  Code Generator  |
+------------------+
     |
     v
+------------------+
|    Validator     |
+------------------+
     |
     v
+------------------+
|     Reporter     |
+------------------+
     |
     +------> report.json
     |
     +------> Amazon S3
```

---

## Project structure

```text
AgentForge/
├── agents/
│   ├── __init__.py
│   ├── task_analyzer.py
│   ├── plan_generator.py
│   ├── code_generator.py
│   ├── validator.py
│   └── reporter.py
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py
├── main.py
├── lambda_function.py
├── requirements.txt
└── README.md
```

---

## Technologies

* Python 3.10+
* AWS Lambda-compatible handler
* Amazon S3
* Boto3
* Rich
* Python AST
* Python `unittest`
* JSON

---

## How to run

### Prerequisites

* Python 3.10+
* Install dependencies using `requirements.txt`

```powershell
& "C:\Program Files\Python310\python.exe" -m pip install -r requirements.txt
```

### Run the pipeline

Interactive mode:

```powershell
& "C:\Program Files\Python310\python.exe" main.py
```

Or provide a task directly:

```powershell
& "C:\Program Files\Python310\python.exe" main.py "Write a function to reverse a string"
```

A `report.json` file is generated after a successful local run.

### Run tests

```powershell
& "C:\Program Files\Python310\python.exe" -m unittest tests/test_pipeline.py -v
```

---

## Example

Example task:

```text
Write a function to reverse a string
```

Pipeline:

```text
[1/6] Analyzing task...
[2/6] Generating implementation plan...
[3/6] Generating code template...
[4/6] Validating generated code...
[5/6] Assembling report...
[6/6] Done.
```

The generated report contains:

* Task type
* Complexity
* Extracted keywords
* Implementation plan
* Generated Python code
* Validation results
* Execution status
* Timestamp

---

## Validation

The project has been verified with:

* **49/49 automated tests passed**
* **6/6 pipeline stages completed successfully**
* Local Lambda handler returned **HTTP 200**
* S3 report upload successfully verified
* S3 test object successfully cleaned up
* Lambda ZIP size: **34 KB**
* No IAM changes required for the development checkpoint
* No Lambda or API Gateway resources created during the development checkpoint

---

## AWS integration

The AWS-specific entry point is:

```text
lambda_function.py
```

The Lambda handler accepts an API Gateway-style request:

```json
{
  "task": "Write a function to reverse a string"
}
```

It then:

1. Parses the incoming request.
2. Runs the existing AgentForge pipeline.
3. Generates the final report.
4. Uploads the report to Amazon S3.
5. Returns a structured JSON response.

S3 report keys follow this format:

```text
reports/<timestamp>/<task_type>/<task_id>.json
```

The S3 upload functionality is implemented in:

```text
agents/reporter.py
```

The project uses `boto3` for the S3 integration.

---

## Local-first design

The core AgentForge pipeline can run locally without requiring AWS deployment.

This approach allows the project to:

* Develop and test the core pipeline locally
* Validate functionality before cloud deployment
* Keep cloud usage and infrastructure costs controlled
* Separate application logic from AWS-specific integration

The Lambda handler provides an AWS-compatible entry point without changing the core pipeline architecture.

---

## Future AWS architecture

The project is designed to support a future cloud architecture:

```text
Client
  |
  v
API Gateway
  |
  v
AWS Lambda
  |
  +--> Task Analysis
  |
  +--> Planning
  |
  +--> Code Generation
  |
  +--> Validation
  |
  +--> Reporting
  |
  +--> Amazon S3
  |
  +--> CloudWatch
```

Future phases may introduce additional AWS services such as Amazon Bedrock or DynamoDB where appropriate.

AWS deployment is intentionally separate from the current local development checkpoint.

---

## Design principles

### Single Responsibility

Each pipeline stage has a focused responsibility and can be tested independently.

### Local-First Development

The core application can be developed and verified locally before cloud deployment.

### Defensive Programming

The code generator includes `_safe_identifier` to help prevent invalid Python identifiers from being generated from task input.

### Code Validation

Generated Python code is checked using AST parsing and compilation checks before being included in the final report.

### AWS-Ready Architecture

The core pipeline is separated from the AWS-specific Lambda handler, making the application easier to integrate with AWS services.

---

## Interview talking points

### Why use a pipeline?

The workflow is divided into independent stages, making each stage easier to test, maintain, and replace.

### Why local-first development?

The core architecture can be validated before introducing cloud infrastructure and deployment costs.

### Why use `ast.parse`?

AST parsing allows Python syntax to be inspected without executing the generated code.

### How does the project use AWS?

The Lambda-compatible handler wraps the existing pipeline and the reporter module can store generated reports in Amazon S3.

### What is `_safe_identifier`?

It is a defensive helper used by the code generator to convert task-derived names into valid Python identifiers.

---

## Current project status

| Component              | Status                              |
| ---------------------- | ----------------------------------- |
| Core pipeline          | Complete                            |
| Six-stage workflow     | Verified                            |
| Automated tests        | 49/49 Passed                        |
| Local Lambda handler   | Verified                            |
| S3 integration         | Verified                            |
| GitHub-ready structure | Complete                            |
| AWS deployment         | Not required for current checkpoint |

---

## Cost-conscious development

The current project checkpoint was developed and verified without creating new Lambda or API Gateway resources.

AWS deployment is being kept separate until the required services, permissions, and potential costs are reviewed.

---

## License

This project is created as a personal portfolio and learning project.


## Current AWS Deployment

- AWS Lambda: AgentForge � Active
- API Gateway: AgentForgeAPI � Deployed
- API endpoint: POST /tasks � Working
- Amazon S3: agentforge-reports � Working
- End-to-end API Gateway ? Lambda ? S3 test � Successful
- Automated tests: 49/49 Passed

