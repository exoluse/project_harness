from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import load_record_index
from .validation import Issue, validate_project


@dataclass(frozen=True)
class EvaluationContext:
    """Immutable repository view shared by all gates in one command."""

    root: Path
    records: dict[str, dict[str, Any]]
    paths: dict[str, Path]
    validation_issues: tuple[Issue, ...]

    @classmethod
    def load(cls, root: Path) -> "EvaluationContext":
        resolved = root.resolve()
        records, paths = load_record_index(resolved)
        issues = tuple(validate_project(resolved))
        return cls(
            root=resolved,
            records=records,
            paths=paths,
            validation_issues=issues,
        )

    def require_root(self, root: Path) -> None:
        if root.resolve() != self.root:
            raise ValueError("EvaluationContext belongs to a different project root")
