import type { ExecutionResult, VerificationIssue } from "./types.js";

const ISSUE_PATTERNS: Array<{ test: RegExp; severity: VerificationIssue["severity"]; suggestion: string }> =
  [
    {
      test: /TODO|FIXME/i,
      severity: "warn",
      suggestion: "Resolve outstanding TODO/FIXME items before finalising."
    },
    {
      test: /error|exception|traceback/i,
      severity: "error",
      suggestion: "Investigate the referenced error output and re-run tests."
    },
    {
      test: /missing|not found/i,
      severity: "warn",
      suggestion: "Confirm referenced resources exist or update the plan."
    }
  ];

export function verify(results: ExecutionResult[]): VerificationIssue[] {
  const issues: VerificationIssue[] = [];

  for (const result of results) {
    for (const pattern of ISSUE_PATTERNS) {
      if (pattern.test.test(result.output)) {
        issues.push({
          stepId: result.stepId,
          description: `Detected "${pattern.test.source}" indicator in output.`,
          severity: pattern.severity,
          suggestion: pattern.suggestion
        });
      }
    }
  }

  return issues;
}
