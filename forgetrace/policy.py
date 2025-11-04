"""
Policy Engine - Configurable Rule Enforcement
Author: Peter Kolawole, BAMG Studio LLC

Provides policy-as-code capabilities for IP auditing, allowing organizations
to codify and enforce compliance rules automatically.

Key Features:
- YAML-based policy definitions
- Support for BLOCK, WARN, INFO actions
- Safe expression evaluation (no code injection)
- Detailed violation reporting
- Policy inheritance and overrides

Example Policy:
    policies:
      - id: no-gpl-licenses
        name: Prohibit GPL Licenses
        severity: HIGH
        action: BLOCK
        condition: "'GPL' in license_types"
        enabled: true
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class PolicyEvaluationError(Exception):
    """Raised when a policy expression contains unsupported constructs."""


class PolicyAction(Enum):
    """
    Actions that can be taken when a policy is violated.
    
    BLOCK: Fail the audit (exit code 1) - for critical violations
    WARN: Print warning but continue - for important but not critical issues
    INFO: Log informational message - for awareness only
    """
    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"


class PolicySeverity(Enum):
    """
    Severity levels for policy violations.
    
    Used for prioritization and reporting. Does not affect action taken
    (that's determined by PolicyAction), but helps teams prioritize fixes.
    """
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class PolicyViolation:
    """
    Represents a single policy violation detected during audit.
    
    Contains all information needed to understand, report, and fix the violation.
    """
    
    def __init__(
        self,
        policy_id: str,
        policy_name: str,
        severity: PolicySeverity,
        action: PolicyAction,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a policy violation.
        
        Args:
            policy_id: Unique identifier for the violated policy
            policy_name: Human-readable policy name
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
            action: Action to take (BLOCK, WARN, INFO)
            message: Detailed explanation of the violation
            details: Additional context (e.g., specific files, values)
        """
        self.policy_id = policy_id
        self.policy_name = policy_name
        self.severity = severity
        self.action = action
        self.message = message
        self.details = details or {}
        
    def __repr__(self) -> str:
        return f"PolicyViolation({self.policy_id}, {self.severity.value}, {self.action.value})"


class PolicyEngine:
    """
    Main policy evaluation engine.
    
    Loads policies from YAML configuration and evaluates them against
    audit findings to detect violations.
    
    Design Decisions:
    -----------------
    1. Safe Evaluation: Uses limited expression language instead of eval()
       to prevent code injection attacks
    
    2. Fail-Safe: If policy evaluation fails, logs error but doesn't block
       audit (avoids false positives blocking legitimate work)
    
    3. Atomic Actions: Each policy is independent. One BLOCK violation
       fails entire audit (fail-fast for critical issues)
    
    4. Context Preservation: Violations include full context for debugging
       (what was checked, what value triggered violation, etc.)
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the policy engine.
        
        Args:
            config: Configuration dictionary containing 'policies' section
        
        Design Note: Takes full config instead of just policies section
        for future expansion (e.g., policy file path, debug mode, etc.)
        """
        self.config = config
        self.policies: List[Dict[str, Any]] = []
        self.violations: List[PolicyViolation] = []
        self._load_policies()
        
    def _load_policies(self) -> None:
        """
        Load and validate policies from configuration.
        
        Performs schema validation to catch errors early (fail-fast principle).
        Invalid policies are logged but not loaded (fail-safe principle).
        
        RATIONALE:
        - Early validation prevents cryptic runtime errors
        - Partial loading allows some policies to work even if others are broken
        - Clear error messages help users fix policy definitions
        """
        raw_policies = self.config.get("policies", [])
        
        if not raw_policies:
            print("ℹ️  No policies configured. Skipping policy enforcement.")
            return
        
        for policy in raw_policies:
            # Validate required fields
            if not self._validate_policy_schema(policy):
                print(f"⚠️  Skipping invalid policy: {policy.get('id', 'unknown')}")
                continue
            
            # Only load enabled policies (feature flag pattern)
            if policy.get("enabled", True):
                self.policies.append(policy)
        
        print(f"✅ Loaded {len(self.policies)} active policies")
    
    def _validate_policy_schema(self, policy: Dict[str, Any]) -> bool:
        """
        Validate that a policy has all required fields with correct types.
        
        Args:
            policy: Policy dictionary from YAML
            
        Returns:
            True if valid, False otherwise
            
        VALIDATION CHECKS:
        1. Required fields present (id, condition, action)
        2. Enum values are valid (action, severity)
        3. Condition is a string (not code object or other dangerous type)
        
        WHY THIS MATTERS:
        - Prevents runtime errors from malformed policies
        - Gives clear feedback about what's wrong
        - Security: Ensures we only evaluate strings, not code objects
        """
        required_fields = ["id", "condition", "action"]
        
        for field in required_fields:
            if field not in policy:
                print(f"❌ Policy validation failed: Missing required field '{field}'")
                return False
        
        # Validate action is a known enum value
        action = policy["action"].upper()
        if action not in [a.value for a in PolicyAction]:
            print(f"❌ Policy '{policy['id']}': Invalid action '{action}'. "
                  f"Must be one of: {', '.join(a.value for a in PolicyAction)}")
            return False
        
        # Validate severity if provided
        if "severity" in policy:
            severity = policy["severity"].upper()
            if severity not in [s.value for s in PolicySeverity]:
                print(f"❌ Policy '{policy['id']}': Invalid severity '{severity}'. "
                      f"Must be one of: {', '.join(s.value for s in PolicySeverity)}")
                return False
        
        # Validate condition is a string (security check)
        if not isinstance(policy["condition"], str):
            print(f"❌ Policy '{policy['id']}': Condition must be a string")
            return False
        
        return True
    
    def evaluate(self, findings: Dict[str, Any]) -> List[PolicyViolation]:
        """
        Evaluate all policies against audit findings.
        
        Args:
            findings: Complete audit findings from all scanners
            
        Returns:
            List of policy violations detected
            
        ALGORITHM:
        1. For each enabled policy:
           a. Build evaluation context from findings
           b. Safely evaluate condition expression
           c. If condition is True, record violation
        2. Return all violations for reporting
        
        ERROR HANDLING:
        - If policy evaluation crashes, log error but continue
        - Don't let one broken policy break entire audit
        - Track which policies failed for debugging
        
        PERFORMANCE:
        - Policies evaluated in order (deterministic)
        - Could parallelize in future but not worth complexity now
        - Most audits have < 50 policies, evaluation is fast
        """
        self.violations = []
        
        if not self.policies:
            return self.violations
        
        print("\n🔍 Evaluating policies...")
        
        for policy in self.policies:
            try:
                violated = self._evaluate_policy(policy, findings)
                if violated:
                    violation = self._create_violation(policy, findings)
                    self.violations.append(violation)
                    self._print_violation(violation)
            except Exception as e:
                # Fail-safe: Don't let broken policy crash audit
                print(f"⚠️  Error evaluating policy '{policy['id']}': {e}")
                continue
        
        # Summary
        if self.violations:
            self._print_summary()
        else:
            print("✅ All policies passed!")
        
        return self.violations
    
    def _evaluate_policy(self, policy: Dict[str, Any], findings: Dict[str, Any]) -> bool:
        """
        Evaluate a single policy condition.
        
        Args:
            policy: Policy definition
            findings: Audit findings to check against
            
        Returns:
            True if policy is VIOLATED (condition evaluated to True)
            False if policy is satisfied (condition evaluated to False)
            
        SECURITY - WHY NOT USE eval()?
        ------------------------------
        Using Python's eval() on user input is dangerous:
        
        BAD: eval(policy["condition"], {"findings": findings})
        # User could inject: "__import__('os').system('rm -rf /')"
        
        GOOD: Safe expression evaluator with limited operators
        # Only allow: ==, !=, >, <, in, and, or, not
        # No function calls, imports, or attribute access
        
        CURRENT IMPLEMENTATION:
        - Simple string matching for MVP
        - Future: Use 'simpleeval' library for safe expression evaluation
        
        TRADE-OFFS:
        - Simple: Fast to implement, easy to debug
        - Limited: Can't do complex logic (but 90% of cases are simple)
        - Secure: No code injection risk
        """
        condition = policy["condition"]
        
        # Build evaluation context
        context = self._build_evaluation_context(findings)
        
        # Evaluate condition with the restricted AST interpreter to prevent unsafe execution
        
        result = self._safe_eval(condition, context)
        return result
    
    def _build_evaluation_context(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the context dictionary for policy evaluation.
        
        Extracts key metrics and values from findings into a flat namespace
        that's easy to reference in policy conditions.
        
        Args:
            findings: Raw audit findings
            
        Returns:
            Dictionary of values accessible in policy conditions
            
        DESIGN DECISION - Flat vs Nested:
        ----------------------------------
        Option 1 (Nested): Keep original structure
          condition: "findings['licenses']['types']['GPL'] > 0"
          Pro: Flexible
          Con: Verbose, error-prone
        
        Option 2 (Flat): Extract common values
          condition: "gpl_license_count > 0"
          Pro: Simple, readable
          Con: Must anticipate all needed values
        
        CHOSEN: Hybrid approach
        - Flatten common values (80% of cases)
        - Keep original findings available for advanced cases
        """
        context: Dict[str, Any] = {}
        
        # License data
        if "licenses" in findings:
            licenses = findings["licenses"]
            context["license_types"] = licenses.get("types", [])
            context["license_count"] = len(context["license_types"])
            
            # Count specific license types
            for license_type in context["license_types"]:
                key = f"license_{license_type.replace('-', '_').replace('.', '_').lower()}_count"
                context[key] = context.get(key, 0) + 1
        
        # Vulnerability data
        if "vulnerabilities" in findings:
            vulns = findings["vulnerabilities"]
            context["vulnerability_count"] = vulns.get("by_severity", {})
            context["total_vulnerabilities"] = vulns.get("total_vulnerabilities", 0)
            context["vulnerable_packages"] = vulns.get("vulnerable_packages", 0)
        
        # SBOM/dependency data
        if "sbom" in findings:
            sbom = findings["sbom"]
            packages = sbom.get("packages", [])
            context["package_count"] = len(packages)
            context["packages"] = packages
        
        # Git/ownership data
        if "git" in findings:
            git = findings["git"]
            context["total_commits"] = git.get("total_commits", 0)
            context["contributors"] = git.get("contributors", [])
            context["contributor_count"] = len(context["contributors"])
        
        # Classification data
        if "classification" in findings:
            classification = findings["classification"]
            context["foreground_files"] = classification.get("foreground", [])
            context["background_files"] = classification.get("background", [])
            context["third_party_files"] = classification.get("third_party", [])
            
            total = len(context["foreground_files"]) + len(context["background_files"]) + len(context["third_party_files"])
            if total > 0:
                context["third_party_percentage"] = (len(context["third_party_files"]) / total) * 100
            else:
                context["third_party_percentage"] = 0
        
        # Keep raw findings for advanced queries
        context["findings"] = findings
        
        return context
    
    def _safe_eval(self, condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a policy condition using a restricted AST interpreter."""
        condition = condition.strip()
        if not condition:
            return False

        try:
            tree = ast.parse(condition, mode="eval")
        except SyntaxError as exc:
            print(f"⚠️  Invalid policy condition '{condition}': {exc}")
            return False

        try:
            self._validate_ast(tree)
            result = self._evaluate_ast(tree.body, context)
        except PolicyEvaluationError as exc:
            print(f"⚠️  Unsupported policy condition '{condition}': {exc}")
            return False
        except Exception as exc:  # Fail-safe: never let policy evaluation crash audit
            print(f"⚠️  Error evaluating condition '{condition}': {exc}")
            return False

        return bool(result)

    def _validate_ast(self, node: ast.AST) -> None:
        """Ensure the parsed expression only contains safe constructs."""
        if isinstance(node, ast.Expression):
            self._validate_ast(node.body)
            return

        if isinstance(node, ast.BoolOp):
            if not isinstance(node.op, (ast.And, ast.Or)):
                raise PolicyEvaluationError("Only 'and'/'or' boolean operators are allowed")
            for value in node.values:
                self._validate_ast(value)
            return

        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ast.Not):
                raise PolicyEvaluationError("Only 'not' unary operator is allowed")
            self._validate_ast(node.operand)
            return

        if isinstance(node, ast.Compare):
            allowed_ops = (ast.Eq, ast.NotEq, ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.In, ast.NotIn)
            for op in node.ops:
                if not isinstance(op, allowed_ops):
                    raise PolicyEvaluationError("Unsupported comparison operator")
            self._validate_ast(node.left)
            for comparator in node.comparators:
                self._validate_ast(comparator)
            return

        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
                raise PolicyEvaluationError("Unsupported arithmetic operator")
            self._validate_ast(node.left)
            self._validate_ast(node.right)
            return

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in {"len"}:
                raise PolicyEvaluationError("Only len() calls are permitted in policy expressions")
            if node.keywords:
                raise PolicyEvaluationError("Keyword arguments are not permitted in policy expressions")
            for arg in node.args:
                self._validate_ast(arg)
            return

        if isinstance(node, ast.Attribute):
            if node.attr.startswith("_"):
                raise PolicyEvaluationError("Private attributes are not accessible in policy expressions")
            self._validate_ast(node.value)
            return

        if isinstance(node, ast.Subscript):
            self._validate_ast(node.value)
            self._validate_ast(node.slice)
            return

        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            for element in node.elts:
                self._validate_ast(element)
            return

        if isinstance(node, ast.Dict):
            for key in node.keys:
                if key is not None:
                    self._validate_ast(key)
            for value in node.values:
                self._validate_ast(value)
            return

        if isinstance(node, (ast.Name, ast.Constant)):
            return

        raise PolicyEvaluationError(f"Unsupported expression: {ast.dump(node, include_attributes=False)}")

    def _evaluate_ast(self, node: ast.AST, context: Dict[str, Any]) -> Any:
        """Evaluate a validated AST node against the provided context."""
        if isinstance(node, ast.Expression):
            return self._evaluate_ast(node.body, context)

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                result = True
                for value in node.values:
                    result = result and bool(self._evaluate_ast(value, context))
                    if not result:
                        break
                return result
            if isinstance(node.op, ast.Or):
                result = False
                for value in node.values:
                    result = result or bool(self._evaluate_ast(value, context))
                    if result:
                        break
                return result

        if isinstance(node, ast.UnaryOp):
            return not bool(self._evaluate_ast(node.operand, context))

        if isinstance(node, ast.Compare):
            return self._apply_comparison(node, context)

        if isinstance(node, ast.BinOp):
            left = self._evaluate_ast(node.left, context)
            right = self._evaluate_ast(node.right, context)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            raise PolicyEvaluationError("Unsupported arithmetic operator")

        if isinstance(node, ast.Call):
            func_name = node.func.id
            args = [self._evaluate_ast(arg, context) for arg in node.args]
            if func_name == "len":
                if len(args) != 1:
                    raise PolicyEvaluationError("len() expects exactly one argument")
                return len(args[0])
            raise PolicyEvaluationError(f"Unsupported function '{func_name}' in policy expression")

        if isinstance(node, ast.Attribute):
            value = self._evaluate_ast(node.value, context)
            return self._resolve_attribute(value, node.attr)

        if isinstance(node, ast.Subscript):
            value = self._evaluate_ast(node.value, context)
            index = self._evaluate_ast(node.slice, context)
            try:
                return value[index]
            except (TypeError, KeyError, IndexError) as exc:
                raise PolicyEvaluationError(f"Invalid subscript access: {exc}") from exc

        if isinstance(node, ast.Name):
            if node.id in context:
                return context[node.id]
            raise PolicyEvaluationError(f"Unknown variable '{node.id}' in policy expression")

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.List):
            return [self._evaluate_ast(elem, context) for elem in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._evaluate_ast(elem, context) for elem in node.elts)

        if isinstance(node, ast.Set):
            return {self._evaluate_ast(elem, context) for elem in node.elts}

        if isinstance(node, ast.Dict):
            return {
                self._evaluate_ast(key, context): self._evaluate_ast(value, context)
                for key, value in zip(node.keys, node.values)
            }

        raise PolicyEvaluationError(f"Unsupported expression node '{type(node).__name__}'")

    def _apply_comparison(self, node: ast.Compare, context: Dict[str, Any]) -> bool:
        """Evaluate comparison expressions including chained comparisons."""
        left_value = self._evaluate_ast(node.left, context)
        for operator, comparator in zip(node.ops, node.comparators):
            right_value = self._evaluate_ast(comparator, context)

            if isinstance(operator, ast.In):
                result = left_value in right_value
            elif isinstance(operator, ast.NotIn):
                result = left_value not in right_value
            elif isinstance(operator, ast.Eq):
                result = left_value == right_value
            elif isinstance(operator, ast.NotEq):
                result = left_value != right_value
            elif isinstance(operator, ast.Gt):
                result = left_value > right_value
            elif isinstance(operator, ast.GtE):
                result = left_value >= right_value
            elif isinstance(operator, ast.Lt):
                result = left_value < right_value
            elif isinstance(operator, ast.LtE):
                result = left_value <= right_value
            else:
                raise PolicyEvaluationError("Unsupported comparison operator")

            if not result:
                return False
            left_value = right_value

        return True

    def _resolve_attribute(self, value: Any, attribute: str) -> Any:
        """Resolve attribute access on dictionaries or objects."""
        if isinstance(value, dict):
            if attribute in value:
                return value[attribute]
            raise PolicyEvaluationError(f"Key '{attribute}' not found in policy context")

        if hasattr(value, attribute):
            if attribute.startswith("_"):
                raise PolicyEvaluationError("Private attributes are not accessible in policy expressions")
            return getattr(value, attribute)

        raise PolicyEvaluationError(
            f"Cannot resolve attribute '{attribute}' on type {type(value).__name__}"
        )
    
    def _create_violation(self, policy: Dict[str, Any], findings: Dict[str, Any]) -> PolicyViolation:
        """
        Create a PolicyViolation object from a violated policy.
        
        Args:
            policy: Policy that was violated
            findings: Audit findings (for extracting details)
            
        Returns:
            PolicyViolation instance with full context
        """
        severity = PolicySeverity[policy.get("severity", "MEDIUM").upper()]
        action = PolicyAction[policy["action"].upper()]
        
        message = policy.get(
            "description",
            f"Policy '{policy.get('name', policy['id'])}' was violated"
        )
        
        # Add condition for debugging
        details = {
            "condition": policy["condition"],
            "policy_id": policy["id"]
        }
        
        return PolicyViolation(
            policy_id=policy["id"],
            policy_name=policy.get("name", policy["id"]),
            severity=severity,
            action=action,
            message=message,
            details=details
        )
    
    def _print_violation(self, violation: PolicyViolation) -> None:
        """Print a policy violation to console with formatting."""
        icon = {
            PolicyAction.BLOCK: "🚫",
            PolicyAction.WARN: "⚠️ ",
            PolicyAction.INFO: "ℹ️ "
        }[violation.action]
        
        print(f"\n{icon} {violation.severity.value} - {violation.policy_name}")
        print(f"   {violation.message}")
        print(f"   Condition: {violation.details.get('condition', 'N/A')}")
    
    def _print_summary(self) -> None:
        """Print summary of all violations."""
        blocks = [v for v in self.violations if v.action == PolicyAction.BLOCK]
        warns = [v for v in self.violations if v.action == PolicyAction.WARN]
        infos = [v for v in self.violations if v.action == PolicyAction.INFO]
        
        print(f"\n{'=' * 60}")
        print(f"Policy Violations Summary:")
        print(f"  🚫 BLOCK: {len(blocks)} (audit will fail)")
        print(f"  ⚠️  WARN:  {len(warns)} (warnings only)")
        print(f"  ℹ️  INFO:  {len(infos)} (informational)")
        print(f"{'=' * 60}\n")
    
    def should_fail_audit(self) -> bool:
        """
        Determine if audit should fail based on violations.
        
        Returns:
            True if any BLOCK-level violations exist
            
        RATIONALE:
        - Fail-fast: One critical violation should stop deployment
        - Clear signal: Exit code 1 tells CI to fail the build
        - Actionable: User knows they must fix BLOCK violations
        """
        return any(v.action == PolicyAction.BLOCK for v in self.violations)
    
    def get_violations_by_severity(self) -> Dict[PolicySeverity, List[PolicyViolation]]:
        """
        Group violations by severity for reporting.
        
        Returns:
            Dictionary mapping severity levels to violation lists
        """
        result: Dict[PolicySeverity, List[PolicyViolation]] = {
            severity: [] for severity in PolicySeverity
        }
        
        for violation in self.violations:
            result[violation.severity].append(violation)
        
        return result
