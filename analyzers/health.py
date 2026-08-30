"""Project health analysis - a simple scoring system."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HealthCheck:
    """A single health check."""

    name: str
    passed: bool
    description: str


@dataclass
class HealthReport:
    """Health report for a project."""

    checks: list[HealthCheck] = field(default_factory=list)

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        return int(sum(c.passed for c in self.checks) / len(self.checks) * 100)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)


def analyze_health(root: Path, files: list[Path]) -> HealthReport:
    """Check the basic health aspects of a project."""
    report = HealthReport()
    file_names = {f.name for f in files}
    file_paths = {str(f) for f in files}

    report.checks.append(HealthCheck(
        name="README",
        passed=any(n.lower().startswith("readme") for n in file_names),
        description="README file present",
    ))

    report.checks.append(HealthCheck(
        name=".gitignore",
        passed=".gitignore" in file_names,
        description=".gitignore present",
    ))

    report.checks.append(HealthCheck(
        name="License",
        passed=any(
            n.lower().startswith("license") or n.lower().startswith("licence")
            for n in file_names
        ),
        description="License file present",
    ))

    report.checks.append(HealthCheck(
        name="Dependencies",
        passed=bool({
            "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
            "package.json", "Cargo.toml", "go.mod", "pom.xml",
            "build.gradle", "Gemfile", "composer.json",
        } & file_names),
        description="Dependency config present",
    ))

    has_tests = any(
        "test" in p.lower() or "spec" in p.lower()
        for p in file_paths
    )
    report.checks.append(HealthCheck(
        name="Tests",
        passed=has_tests,
        description="Test files present",
    ))

    ci_patterns = [
        ".github/workflows",
        ".gitlab-ci.yml",
        ".circleci",
        ".travis.yml",
        "Jenkinsfile",
        "azure-pipelines.yml",
        ".drone.yml",
    ]
    has_ci = any(
        any(pat in p for pat in ci_patterns)
        for p in file_paths
    )
    report.checks.append(HealthCheck(
        name="CI/CD",
        passed=has_ci,
        description="CI/CD configuration present",
    ))

    return report
