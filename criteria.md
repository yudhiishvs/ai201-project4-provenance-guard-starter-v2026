# Capstone Acceptance Criteria

## 1. Local Execution

The Provenance Guard system must start using the documented command in RUNNING.md and successfully process at least 3 out of 3 valid requests without requiring changes to the source code.

Reason: A reproducible local run demonstrates that the system can operate outside the development environment and that another person can follow the setup instructions.

## 2. Structured Logging

At least 10 out of 10 requests must produce structured log records containing a timestamp, input, output, execution duration, and status.

Reason: Every request needs a complete record so that system behavior can be inspected and evaluated after execution.

## 3. Logging Accuracy

For at least 9 out of 10 requests, the input and output recorded in the structured log must match the actual submitted input and returned response, and the recorded duration must be nonnegative.

Reason: Logs are only useful for debugging and evaluation if they accurately represent what happened during execution.

## 4. Failure Handling and Logging

At least 5 out of 5 deliberately malformed or empty requests must produce a controlled rejection or error response without terminating the application. Each rejected request must also generate a structured log record identifying the failure.

Reason: Invalid inputs should not crash the system or disappear from its execution history. Recording failures makes it possible to identify and diagnose problems.

## 5. Existing Functionality Preservation

At least 9 out of 10 previously valid Provenance Guard test inputs must continue to produce their expected results after the local execution and logging extensions are added.

Reason: Adding operational capabilities should not compromise the system's original provenance-checking behavior. This criterion checks that the extension does not introduce regressions.

The earlier project targets are preserved in [Unit 8 acceptance criteria](docs/unit8-criteria.md).
