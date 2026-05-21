#!/usr/bin/env python3
"""
compile-profile.py — Aggregate sub-agent JSON outputs into the final profile document.

Usage:
    python3 compile-profile.py \
        --run-dir <path>/.anthril/profile-run/<PROFILE_ID> \
        --template <skill_dir>/templates/codebase-profile-template.md \
        --schema <skill_dir>/templates/profile-schema.json \
        --output-md <path>/.anthril/codebase-profile.md \
        --output-json <path>/.anthril/codebase-profile.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_agent(run_dir: Path, agent_name: str) -> dict:
    path = run_dir / f"{agent_name}.json"
    if not path.exists():
        return {"agent": agent_name, "status": "missing", "findings": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"agent": agent_name, "status": f"parse_error: {e}", "findings": []}


def load_context(run_dir: Path) -> dict:
    path = run_dir / "context.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def score_dimension(signals: dict, dimension: str) -> str:
    """Return ✓, ⚠, or ✗ based on dimension and signals."""
    def s(key, default=None):
        return signals.get(key, default)

    if dimension == "dependency_health":
        vulns = s("vulnerabilities", {})
        if vulns.get("critical", 0) > 0:
            return "✗"
        if vulns.get("high", 0) > 2 or s("outdated", {}).get("count", 0) > (s("total_direct", 1) * 0.3):
            return "⚠"
        return "✓"

    if dimension == "test_coverage":
        ratio = s("test_to_source_ratio", 0)
        cov = s("coverage_pct")
        if s("framework", "none") == "none":
            return "✗"
        if cov is not None:
            if cov >= 70:
                return "✓"
            if cov >= 40:
                return "⚠"
            return "✗"
        if ratio >= 0.5:
            return "✓"
        if ratio >= 0.2:
            return "⚠"
        return "✗"

    if dimension == "type_safety":
        if not s("typed_language", True):
            return "⚠"
        any_count = s("any_count", 0)
        ts_nocheck = s("ts_nocheck_files", [])
        if ts_nocheck or any_count > 100:
            return "✗"
        if any_count > 20:
            return "⚠"
        return "✓"

    if dimension == "code_complexity":
        large = s("large_files_count", 0)
        source = s("source_files", 100)
        pct = large / max(source, 1) * 100
        if pct > 15:
            return "✗"
        if pct > 5:
            return "⚠"
        return "✓"

    if dimension == "security_surface":
        secrets = s("secret_patterns_detected", 0)
        env_ok = s("env_files_in_gitignore", True)
        if secrets > 0 or not env_ok:
            severities = [f.get("severity", "") for f in s("secret_findings", [])]
            if "CRITICAL" in severities:
                return "✗"
            if secrets > 0:
                return "⚠"
        if not env_ok:
            return "⚠"
        return "✓"

    if dimension == "infrastructure_maturity":
        hosting = s("hosting_provider", "unknown")
        ci = s("ci_providers", [])
        if hosting == "unknown" and not ci:
            return "✗"
        if not ci:
            return "⚠"
        return "✓"

    if dimension == "observability":
        error = s("error_tracking", "none")
        logging = s("logging", "none")
        if error == "none" and logging in ("none", "console.log"):
            return "✗"
        if error == "none":
            return "⚠"
        return "✓"

    if dimension == "developer_experience":
        readme = s("readme_present", False)
        linting = s("linting_config_present", False)
        if not readme and not linting:
            return "✗"
        if not readme or not linting:
            return "⚠"
        return "✓"

    return "⚠"


def derive_health_tier(scores: dict) -> str:
    x_count = sum(1 for v in scores.values() if v == "✗")
    warn_count = sum(1 for v in scores.values() if v == "⚠")
    if x_count >= 3:
        return "Significant Risk"
    if x_count >= 1 or warn_count >= 3:
        return "Needs Attention"
    return "Healthy"


def build_focus_areas(scores: dict, agents: dict) -> list:
    areas = []
    order = ["security_surface", "dependency_health", "test_coverage",
             "type_safety", "code_complexity", "observability",
             "infrastructure_maturity", "developer_experience"]
    labels = {
        "security_surface": "Security surface requires attention",
        "dependency_health": "Dependency health needs review",
        "test_coverage": "Test coverage is insufficient",
        "type_safety": "Type safety issues detected",
        "code_complexity": "Code complexity is high",
        "observability": "Observability tooling is missing or minimal",
        "infrastructure_maturity": "Infrastructure configuration is incomplete",
        "developer_experience": "Developer experience signals are weak",
    }
    for dim in order:
        score = scores.get(dim, "⚠")
        if score in ("✗", "⚠"):
            areas.append({"status": score, "dimension": dim, "label": labels.get(dim, dim)})
    # Add ✓ areas to round out to 5
    for dim in order:
        if len(areas) >= 5:
            break
        if scores.get(dim) == "✓":
            areas.append({"status": "✓", "dimension": dim, "label": labels.get(dim, dim)})
    return areas[:5]


def render_template(template: str, ctx: dict) -> str:
    for key, val in ctx.items():
        template = template.replace("{{" + key + "}}", str(val) if val is not None else "unknown")
    return template


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    template_path = Path(args.template)
    schema_path = Path(args.schema)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)

    context = load_context(run_dir)
    dep = load_agent(run_dir, "dependency-analyst")
    arch = load_agent(run_dir, "architecture-mapper")
    qual = load_agent(run_dir, "quality-profiler")
    infra = load_agent(run_dir, "infra-security-scanner")

    # Build scoring signals
    dep_data = dep.get("dependencies", {})
    vuln_data = dep.get("vulnerabilities", {})
    outdated_data = dep.get("outdated", {})
    qual_type = qual.get("type_safety", {})
    qual_tests = qual.get("tests", {})
    qual_complex = qual.get("complexity", {})
    qual_lint = qual.get("linting", {})
    infra_sec = infra.get("secrets", {})
    infra_env = infra.get("env_management", {})
    infra_obs = infra.get("observability", {})
    infra_infra = infra.get("infrastructure", {})
    infra_ci = infra.get("ci_cd", {})
    infra_dx = {}

    signals = {
        "vulnerabilities": vuln_data,
        "total_direct": dep_data.get("direct", 0),
        "outdated": outdated_data,
        "test_to_source_ratio": qual_tests.get("test_to_source_ratio", 0),
        "coverage_pct": qual_tests.get("coverage_pct"),
        "framework": qual_tests.get("framework", "none"),
        "typed_language": qual_type.get("typed_language", True),
        "any_count": qual_type.get("any_count", 0),
        "ts_nocheck_files": qual_type.get("ts_nocheck_files", []),
        "large_files_count": qual_complex.get("large_files_count", 0),
        "source_files": qual_tests.get("source_file_count", 100),
        "secret_patterns_detected": infra_sec.get("patterns_detected", 0),
        "secret_findings": infra_sec.get("findings", []),
        "env_files_in_gitignore": infra_env.get("all_in_gitignore", True),
        "hosting_provider": infra_infra.get("hosting_provider", "unknown"),
        "ci_providers": infra_ci.get("providers", []),
        "error_tracking": infra_obs.get("error_tracking", "none"),
        "logging": infra_obs.get("logging", "none"),
        "readme_present": context.get("readme_present", False),
        "linting_config_present": bool(qual_lint.get("configs_found", [])),
    }

    dimensions = [
        "dependency_health", "test_coverage", "type_safety", "code_complexity",
        "security_surface", "infrastructure_maturity", "observability", "developer_experience"
    ]
    scores = {d: score_dimension(signals, d) for d in dimensions}
    health_tier = derive_health_tier(scores)
    focus_areas = build_focus_areas(scores, {})

    profile_id = context.get("profile_id", "unknown")
    target = context.get("target_dir", "unknown")
    stack = context.get("stack", {})
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M %Z")

    # Build JSON sidecar
    schema = json.loads(schema_path.read_text(encoding="utf-8")) if schema_path.exists() else {}
    profile_json = {
        "schema_version": schema.get("properties", {}).get("schema_version", {}).get("const", "1.0.0"),
        "profile": {
            "id": profile_id,
            "generated_at": generated_at,
            "target": target,
            "profiler_version": "1.0.0",
            "profile_depth": context.get("profile_depth", "full")
        },
        "stack": stack,
        "metrics": context.get("metrics", {}),
        "dependencies": {
            "direct": dep_data.get("direct", 0),
            "dev": dep_data.get("dev", 0),
            "transitive_estimate": dep_data.get("transitive_estimate", 0),
            "vulnerable": {
                "critical": vuln_data.get("critical", 0),
                "high": vuln_data.get("high", 0),
                "moderate": vuln_data.get("moderate", 0)
            },
            "outdated_count": outdated_data.get("count", 0),
            "circular_imports": dep.get("circular_imports", {}).get("cycles", []),
            "licenses": dep.get("licences", {})
        },
        "architecture": {
            "entry_points": arch.get("entry_points", []),
            "api_routes_count": arch.get("api_surface", {}).get("route_files_count", 0),
            "client_server_boundary": arch.get("client_server_boundary", {}).get("model", "unknown"),
            "data_layer": arch.get("data_layer", {}).get("orm", ""),
            "mermaid_diagram": arch.get("mermaid_diagram", "")
        },
        "quality": {
            "type_coverage_pct": qual_type.get("type_coverage_pct"),
            "any_usage_count": qual_type.get("any_count", 0),
            "ts_ignore_count": qual_type.get("ts_ignore_count", 0),
            "test_framework": qual_tests.get("framework", ""),
            "test_to_source_ratio": qual_tests.get("test_to_source_ratio", 0),
            "coverage_pct": qual_tests.get("coverage_pct"),
            "large_files_count": qual_complex.get("large_files_count", 0),
            "todo_count": qual_complex.get("todo_count", 0)
        },
        "security": {
            "secret_patterns_detected": infra_sec.get("patterns_detected", 0),
            "env_files_in_gitignore": infra_env.get("all_in_gitignore", True),
            "auth_library": infra.get("auth", {}).get("library", ""),
            "secret_patterns": [
                {"severity": f.get("severity"), "type": f.get("type"),
                 "file": f.get("file"), "line": f.get("line"), "value": "[REDACTED]"}
                for f in infra_sec.get("findings", [])
            ]
        },
        "infrastructure": {
            "hosting": infra_infra.get("hosting_provider", ""),
            "ci_cd": infra_ci.get("providers", []),
            "observability": [v for v in [
                infra_obs.get("error_tracking"),
                infra_obs.get("logging"),
                infra_obs.get("apm_tracing")
            ] if v and v != "none"]
        },
        "health": {
            "tier": health_tier,
            "dimensions": scores,
            "focus_areas": [f["label"] for f in focus_areas]
        }
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(profile_json, indent=2), encoding="utf-8")
    print(f"[compile-profile] JSON sidecar written: {output_json}", file=sys.stderr)

    # Render template
    if template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")
        ctx = {
            "profile_id": profile_id,
            "generated_at": generated_at,
            "target": target,
            "profiler_version": "1.0.0",
            "profile_depth": context.get("profile_depth", "full"),
            "health_tier": health_tier,
            "health_tier_emoji": {"Healthy": "✅", "Needs Attention": "⚠️", "Significant Risk": "🚨"}.get(health_tier, "❓"),
            "primary_language": stack.get("primary_language", "unknown"),
            "framework": stack.get("framework", "unknown"),
            "framework_version": stack.get("framework_version", ""),
            "runtime_version": stack.get("runtime_version", "unknown"),
            "package_manager": stack.get("package_manager", "unknown"),
            "typescript_strict": stack.get("typescript_strict", "unknown"),
            "monorepo": stack.get("monorepo", {}).get("monorepo", False),
        }
        rendered = render_template(template_content, ctx)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(rendered, encoding="utf-8")
        print(f"[compile-profile] Profile document written: {output_md}", file=sys.stderr)
    else:
        print(f"[compile-profile] Template not found at {template_path}", file=sys.stderr)

    print(json.dumps({
        "status": "complete",
        "health_tier": health_tier,
        "scores": scores,
        "focus_areas": [f["label"] for f in focus_areas]
    }))


if __name__ == "__main__":
    main()
