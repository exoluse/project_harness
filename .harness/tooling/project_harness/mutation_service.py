from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any, Callable

from .collaboration import ensure_claim_current, get_claim, runtime_root
from .constants import HARNESS_DIR
from .core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    filesystem_mutex,
    is_path_within,
    load_json,
    normalize_agent_id,
    normalize_claim_path,
    utc_now,
)
from .schema_validation import SCHEMA_FILES, SchemaSet


MutationValidator = Callable[[], None]


class AtomicMutationService:
    """Provide transaction integrity for multi-record canonical mutations."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.runtime = runtime_root(self.root) / "mutations"
        self.lock = self.runtime / "record.lock"
        self.transactions = self.runtime / "transactions"

    def _transaction_directories(self) -> list[Path]:
        if not self.transactions.is_dir():
            return []
        return sorted(path for path in self.transactions.glob("TXN-*") if path.is_dir())

    def _restore(self, directory: Path, manifest: dict[str, Any]) -> None:
        for index, entry in enumerate(manifest.get("targets", [])):
            target = self.root / entry["path"]
            if entry.get("existed"):
                backup = directory / "backups" / f"{index:04d}.bin"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(backup.read_bytes())
            elif target.exists():
                target.unlink()
        manifest["state"] = "ROLLED_BACK"
        manifest["rolled_back_at"] = utc_now()
        atomic_write_json(directory / "manifest.json", manifest)

    def recover_incomplete(self) -> list[str]:
        recovered: list[str] = []
        for directory in self._transaction_directories():
            manifest_path = directory / "manifest.json"
            manifest = load_json(manifest_path)
            if manifest.get("state") == "PREPARED":
                self._restore(directory, manifest)
                recovered.append(str(manifest.get("id")))
            if manifest.get("state") in {"COMMITTED", "ROLLED_BACK"}:
                shutil.rmtree(directory, ignore_errors=True)
        return recovered

    def apply(
        self,
        *,
        writes: dict[str, dict[str, Any]],
        event_type: str,
        event_payload: dict[str, Any],
        validate_before_commit: MutationValidator | None = None,
        fail_after_writes: int | None = None,
    ) -> dict[str, Any]:
        if not writes:
            raise HarnessError("Atomic mutation requires at least one target")
        normalized_writes: dict[str, dict[str, Any]] = {}
        for value, record in writes.items():
            normalized = normalize_claim_path(self.root, value)
            if normalized == "**":
                raise HarnessError("Atomic mutation target must be one file")
            normalized_writes[normalized] = record

        with filesystem_mutex(
            self.lock,
            timeout_seconds=30,
            recovery_directory=self.runtime / "lock-recoveries",
            timeout_message="Timed out waiting for the canonical mutation lock",
        ):
            recovered = self.recover_incomplete()
            transaction_id = f"TXN-{uuid.uuid4().hex}"
            directory = self.transactions / transaction_id
            backups = directory / "backups"
            backups.mkdir(parents=True, exist_ok=False)

            events = self.root / HARNESS_DIR / "events"
            event_id = allocate_record_id(self.root, events, "EVT-")
            event_relative = f"{HARNESS_DIR}/events/{event_id}.json"
            normalized_writes[event_relative] = {
                "schema": "harness.event/v1",
                "id": event_id,
                "kind": "event",
                "event_type": event_type,
                "occurred_at": utc_now(),
                "payload": event_payload,
            }

            targets: list[dict[str, Any]] = []
            for index, relative in enumerate(sorted(normalized_writes)):
                target = self.root / relative
                existed = target.is_file()
                if existed:
                    (backups / f"{index:04d}.bin").write_bytes(target.read_bytes())
                targets.append({"path": relative, "existed": existed})
            manifest = {
                "schema": "harness.atomic-mutation/v1",
                "id": transaction_id,
                "kind": "atomic_mutation",
                "state": "PREPARED",
                "event_id": event_id,
                "targets": targets,
                "prepared_at": utc_now(),
            }
            atomic_write_json(directory / "manifest.json", manifest)

            try:
                if validate_before_commit is not None:
                    validate_before_commit()
                applied = 0
                for relative in sorted(normalized_writes):
                    atomic_write_json(self.root / relative, normalized_writes[relative])
                    applied += 1
                    if fail_after_writes is not None and applied >= fail_after_writes:
                        raise OSError("injected atomic mutation failure")
            except Exception:
                self._restore(directory, manifest)
                shutil.rmtree(directory, ignore_errors=True)
                raise

            manifest["state"] = "COMMITTED"
            manifest["committed_at"] = utc_now()
            atomic_write_json(directory / "manifest.json", manifest)
            shutil.rmtree(directory, ignore_errors=True)
            return {
                "transaction_id": transaction_id,
                "event_id": event_id,
                "changed_files": sorted(normalized_writes),
                "recovered_transactions": recovered,
            }


def authorize_claim_targets(
    root: Path,
    *,
    claim_id: str | None,
    agent: str,
    targets: list[str],
) -> dict[str, Any]:
    """Enforce writer authority before a canonical mutation is prepared."""
    normalized_agent = normalize_agent_id(agent)
    normalized_targets = [normalize_claim_path(root, value) for value in targets]
    if claim_id is None:
        from .collaboration import list_claims, paths_overlap
        from .policy import claim_mode

        if claim_mode(root) != "WHEN_CONCURRENT":
            raise HarnessError("Canonical mutation requires an active claim")
        conflicts = [
            claim.get("id", "UNKNOWN")
            for claim in list_claims(root, active_only=True)
            if any(
                paths_overlap(target, owned)
                for target in normalized_targets
                for owned in claim.get("paths", [])
            )
        ]
        if conflicts:
            raise HarnessError(
                "Unclaimed mutation overlaps active ownership: "
                + ", ".join(sorted(conflicts))
            )
        return {
            "status": "UNCLAIMED",
            "agent": normalized_agent,
            "paths": normalized_targets,
        }
    claim, _path = get_claim(root, claim_id)
    if claim.get("status") != "ACTIVE" or claim.get("agent") != normalized_agent:
        raise HarnessError("Canonical mutation requires the agent's active claim")
    ensure_claim_current(root, claim)
    outside = [
        value
        for value in normalized_targets
        if not is_path_within(value, claim.get("paths", []))
    ]
    if outside:
        raise HarnessError(
            "Canonical mutation targets exceed the active claim: "
            + ", ".join(sorted(outside))
        )
    return claim


def validate_records(root: Path, values: list[tuple[str, dict[str, Any]]]) -> None:
    """Validate every prospective record before transaction preparation."""
    schemas = SchemaSet(root / "schemas")
    errors: list[str] = []
    for kind, value in values:
        errors.extend(schemas.validate(value, SCHEMA_FILES[kind]))
    if errors:
        raise HarnessError("Mutation would write invalid records: " + "; ".join(errors))
