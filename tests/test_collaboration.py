from __future__ import annotations

import tempfile
import subprocess
import socket
import time
import unittest
from pathlib import Path

from project_harness.collaboration import (
    _runtime_mutex,
    acquire_claim,
    create_handoff,
    get_claim,
    recover_claim,
    render_handoff,
    release_claim,
    runtime_root,
)
from project_harness.core import (
    HarnessError,
    allocate_record_id,
    atomic_write_json,
    load_json,
    load_record_index,
    record_path,
    sha256_bytes,
    utc_now,
)
from project_harness.gates import _latest_task_result_assessment
from project_harness.workflow import review_result, submit_result

from .helpers import HarnessTestCase, add_verified_evidence, create_ready_project


def git(root: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stdout)


def commit_fixture(root: Path) -> None:
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "harness-tests@example.invalid")
    git(root, "config", "user.name", "Harness Tests")
    git(root, "add", ".")
    git(root, "commit", "-m", "fixture baseline")


def recovery_manifest(claim_id: str, agent: str) -> dict:
    details = {
        "process": "No live owner process remains.",
        "worktree": "The claimed worktree was inspected and preserved.",
        "diff": "The current diff was inspected for incomplete writes.",
        "outbox": "The previous owner outbox contains no pending result.",
        "external_side_effects": "No external side effect was started.",
    }
    checks = [
        {
            "name": name,
            "outcome": "PASS",
            "detail": detail,
            "detail_sha256": sha256_bytes(detail.encode("utf-8")),
        }
        for name, detail in details.items()
    ]
    checks[-1].update(
        {"reconciliation": "NONE", "idempotency_keys": [], "receipts": []}
    )
    return {
        "schema": "harness.recovery/v1",
        "id": "RCV-0001",
        "kind": "recovery",
        "claim_id": claim_id,
        "recovered_by": agent,
        "observed_at": utc_now(),
        "checks": checks,
        "decision": "ABANDON_AND_RECLAIM",
        "reason": "Inspection supports abandoning the expired ownership lease.",
    }


class CollaborationTests(HarnessTestCase):
    def test_disjoint_claims_in_same_resolved_worktree_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            with self.assertRaisesRegex(HarnessError, "resolved worktree"):
                acquire_claim(
                    root, agent="claude", task_id="TASK-0001", paths=["tests"]
                )

    def test_handoff_view_is_system_managed_and_uses_latest_canonical_record(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            with self.assertRaisesRegex(HarnessError, "system-managed"):
                acquire_claim(
                    root,
                    agent="codex",
                    task_id="TASK-0001",
                    paths=["HANDOFF.md"],
                )

            def handoff(identifier: str, next_action: str) -> dict:
                return {
                    "schema": "harness.handoff/v1",
                    "id": identifier,
                    "kind": "handoff",
                    "task_id": "TASK-0001",
                    "from_agent": "codex",
                    "to_agent": "claude",
                    "base_commit": None,
                    "head_commit": None,
                    "summary": identifier,
                    "changed_files": [],
                    "verification": [
                        {"command": "python -m unittest", "outcome": "PASS"}
                    ],
                    "unverified": [],
                    "decisions": [],
                    "risks": [],
                    "next_action": next_action,
                }

            older = handoff("HOF-0001", "old action")
            latest = handoff("HOF-0002", "latest action")
            atomic_write_json(root / ".harness" / "handoffs" / "HOF-0001.json", older)
            atomic_write_json(root / ".harness" / "handoffs" / "HOF-0002.json", latest)
            rendered = render_handoff(root, older)
            self.assertEqual(rendered["id"], "HOF-0002")
            view = (root / "HANDOFF.md").read_text(encoding="utf-8")
            self.assertIn("HOF-0002.json", view)
            self.assertIn("latest action", view)

    def test_runtime_mutex_reclaims_dead_owner_but_never_live_local_owner(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            lock = runtime_root(root) / "claim-mutex"
            lock.mkdir()
            atomic_write_json(
                lock / "owner.json",
                {
                    "schema": "harness.filesystem-lock/v1",
                    "kind": "filesystem_lock",
                    "nonce": "dead-owner",
                    "pid": 99999999,
                    "host": socket.gethostname(),
                    "process_start_token": "unreachable",
                    "acquired_at": "2000-01-01T00:00:00Z",
                    "expires_at": "2999-01-01T00:00:00Z",
                },
            )
            with _runtime_mutex(root, timeout_seconds=0.5, lease_seconds=0.1):
                self.assertTrue((lock / "owner.json").is_file())
            self.assertTrue(any((runtime_root(root) / "lock-recoveries").glob("*.json")))

            with _runtime_mutex(root, lease_seconds=0.01):
                time.sleep(0.02)
                with self.assertRaises(HarnessError):
                    with _runtime_mutex(
                        root, timeout_seconds=0.1, lease_seconds=0.01
                    ):
                        self.fail("live local mutex owner must never be displaced")

    def test_record_allocator_reclaims_a_dead_owner_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            allocator = root / ".harness" / "runtime" / "id-sequences"
            lock = allocator / "tst.lock"
            lock.mkdir(parents=True)
            atomic_write_json(
                lock / "owner.json",
                {
                    "schema": "harness.filesystem-lock/v1",
                    "kind": "filesystem_lock",
                    "nonce": "dead-owner",
                    "pid": 99999999,
                    "host": socket.gethostname(),
                    "process_start_token": "unreachable",
                    "acquired_at": "2000-01-01T00:00:00Z",
                    "expires_at": "2999-01-01T00:00:00Z",
                },
            )
            identifier = allocate_record_id(root, root / "records", "TST-")
            self.assertEqual(identifier, "TST-0001")
            self.assertTrue(any((allocator / "lock-recoveries").glob("*.json")))

    def test_recovery_requires_and_preserves_a_structured_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            stored, claim_path = get_claim(root, claim["id"])
            stored["expires_at"] = "2000-01-01T00:00:00Z"
            atomic_write_json(claim_path, stored)
            with self.assertRaisesRegex(HarnessError, "recovery-manifest"):
                recover_claim(
                    root,
                    claim_id=claim["id"],
                    agent="coordinator",
                    reason="Free text alone is not inspection evidence.",
                )

            source = root / "artifacts" / "recovery.json"
            source.parent.mkdir()
            manifest = recovery_manifest(claim["id"], "coordinator")
            atomic_write_json(source, manifest)
            recovered = recover_claim(
                root,
                claim_id=claim["id"],
                agent="coordinator",
                reason="Operator authorizes recovery after inspection.",
                recovery_manifest="artifacts/recovery.json",
            )
            self.assertEqual(recovered["status"], "ABANDONED_AFTER_RECOVERY")
            self.assertEqual(recovered["recovery_id"], "RCV-0001")
            self.assertEqual(
                load_json(record_path(root, "recovery", "RCV-0001")), manifest
            )

    def test_recovery_rejects_a_stale_check_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            stored, claim_path = get_claim(root, claim["id"])
            stored["expires_at"] = "2000-01-01T00:00:00Z"
            atomic_write_json(claim_path, stored)
            manifest = recovery_manifest(claim["id"], "coordinator")
            manifest["checks"][0]["detail_sha256"] = "0" * 64
            source = root / "artifacts" / "recovery.json"
            source.parent.mkdir()
            atomic_write_json(source, manifest)
            with self.assertRaisesRegex(HarnessError, "detail_sha256"):
                recover_claim(
                    root,
                    claim_id=claim["id"],
                    agent="coordinator",
                    reason="Must not accept stale inspection evidence.",
                    recovery_manifest="artifacts/recovery.json",
                )

    def test_overlapping_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            first = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            with self.assertRaises(HarnessError):
                acquire_claim(root, agent="claude", task_id="TASK-0001", paths=["src/api"])
            release_claim(root, claim_id=first["id"], agent="codex")

    def test_handoff_releases_claim_and_renders_view(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            (root / "src").mkdir(exist_ok=True)
            target = root / "src" / "core.py"
            target.write_text("value = 0\n", encoding="utf-8")
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            target.write_text("value = 1\n", encoding="utf-8")
            handoff = create_handoff(
                root,
                claim_id=claim["id"],
                from_agent="codex",
                to_agent="claude",
                task_id="TASK-0001",
                summary="Implemented the core",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::passed"],
                next_action="Review src/core.py",
                unverified=["production"],
            )
            self.assertEqual(handoff["to_agent"], "claude")
            released, _path = get_claim(root, claim["id"])
            self.assertEqual(released["status"], "RELEASED")
            view = (root / "HANDOFF.md").read_text(encoding="utf-8")
            self.assertIn("Review src/core.py", view)

    def test_result_requires_independent_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            (root / "src").mkdir(exist_ok=True)
            target = root / "src" / "core.py"
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            target.write_text("value = 2\n", encoding="utf-8")
            result = submit_result(
                root,
                claim_id=claim["id"],
                agent="codex",
                summary="Core implemented",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::passed"],
                evidence_refs=["EVD-0001"],
                limitations=["not production verified"],
            )
            with self.assertRaises(HarnessError):
                review_result(
                    root,
                    result_id=result["id"],
                    reviewer="codex",
                    decision="PASS",
                    basis="self review",
                    checks=["tests"],
                )
            verdict = review_result(
                root,
                result_id=result["id"],
                reviewer="claude",
                decision="PASS",
                basis="Independent code and evidence review",
                checks=["diff", "test evidence"],
            )
            self.assertEqual(verdict["decision"], "PASS")

    def test_stale_result_cannot_receive_pass_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            target = root / "src" / "core.py"
            claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            target.write_text("value = 2\n", encoding="utf-8")
            result = submit_result(
                root,
                claim_id=claim["id"],
                agent="codex",
                summary="Current only at submission",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::PASS"],
                evidence_refs=["EVD-0001"],
                limitations=[],
            )
            target.write_text("value = 3\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                review_result(
                    root,
                    result_id=result["id"],
                    reviewer="claude",
                    decision="PASS",
                    basis="Must not approve stale code",
                    checks=["file hashes"],
                )

    def test_incomplete_result_cannot_receive_pass_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            target = root / "src" / "core.py"
            claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            target.write_text("value = 2\n", encoding="utf-8")
            result = submit_result(
                root,
                claim_id=claim["id"],
                agent="codex",
                summary="Verification blocked",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::BLOCKED"],
                evidence_refs=["EVD-0001"],
                limitations=["test environment unavailable"],
            )
            with self.assertRaises(HarnessError):
                review_result(
                    root,
                    result_id=result["id"],
                    reviewer="claude",
                    decision="PASS",
                    basis="Cannot override verification",
                    checks=["result verification state"],
                )

    def test_later_incomplete_attempt_supersedes_earlier_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            target = root / "src" / "core.py"
            first_claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            target.write_text("value = 2\n", encoding="utf-8")
            first = submit_result(
                root,
                claim_id=first_claim["id"],
                agent="codex",
                summary="First passing attempt",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::PASS"],
                evidence_refs=["EVD-0001"],
                limitations=[],
            )
            review_result(
                root,
                result_id=first["id"],
                reviewer="claude",
                decision="PASS",
                basis="First attempt review",
                checks=["diff", "tests"],
            )
            second_claim = acquire_claim(
                root, agent="codex", task_id="TASK-0001", paths=["src"]
            )
            target.write_text("value = 3\n", encoding="utf-8")
            second = submit_result(
                root,
                claim_id=second_claim["id"],
                agent="codex",
                summary="Later incomplete attempt",
                changed_files=["src/core.py"],
                verifications=["python -m unittest::BLOCKED"],
                evidence_refs=["EVD-0001"],
                limitations=["runner unavailable"],
            )
            records, _paths = load_record_index(root)
            latest, _review, reasons = _latest_task_result_assessment(
                root,
                "TASK-0001",
                records,
            )
            self.assertEqual(latest["id"], second["id"])
            self.assertTrue(reasons)

    def test_path_traversal_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            with self.assertRaises(HarnessError):
                acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["../escape"])

    def test_stale_claim_cannot_submit_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / "core.py").write_text("value = 1\n", encoding="utf-8")
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            task_path = record_path(root, "work_item", "TASK-0001")
            task = load_json(task_path)
            task["verification"].append("python -m compileall src")
            atomic_write_json(task_path, task)
            with self.assertRaises(HarnessError):
                submit_result(
                    root,
                    claim_id=claim["id"],
                    agent="codex",
                    summary="Cannot launder stale scope",
                    changed_files=["src/core.py"],
                    verifications=["python -m unittest::passed"],
                    evidence_refs=["EVD-0001"],
                    limitations=[],
                )

    def test_agent_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            from project_harness.workflow import dispatch_task

            with self.assertRaises(HarnessError):
                dispatch_task(
                    root,
                    task_id="TASK-0001",
                    to_agent="../escape",
                    issued_by="human",
                    instructions="unsafe",
                )

    def test_handoff_accepts_transferred_dirty_files_once(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            (root / "src").mkdir(exist_ok=True)
            target = root / "src" / "core.py"
            target.write_text("value = 0\n", encoding="utf-8")
            commit_fixture(root)

            first = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            target.write_text("value = 1\n", encoding="utf-8")
            handoff = create_handoff(
                root,
                claim_id=first["id"],
                from_agent="codex",
                to_agent="claude",
                task_id="TASK-0001",
                summary="Transfer uncommitted implementation",
                changed_files=["src/core.py"],
                verifications=["python -m compileall src::passed"],
                next_action="Continue TASK-0001",
            )
            unknown = root / "src" / "user-owned.py"
            unknown.write_text("unknown = True\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                acquire_claim(
                    root,
                    agent="claude",
                    task_id="TASK-0001",
                    paths=["src"],
                    handoff_id=handoff["id"],
                )
            unknown.unlink()
            with self.assertRaises(HarnessError):
                acquire_claim(root, agent="claude", task_id="TASK-0001", paths=["src"])
            second = acquire_claim(
                root,
                agent="claude",
                task_id="TASK-0001",
                paths=["src"],
                handoff_id=handoff["id"],
            )
            self.assertEqual(second["accepted_handoff_id"], handoff["id"])
            release_claim(root, claim_id=second["id"], agent="claude")

    def test_result_rejects_changes_outside_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            (root / "src").mkdir(exist_ok=True)
            target = root / "src" / "core.py"
            target.write_text("value = 0\n", encoding="utf-8")
            outside = root / "README.md"
            outside.write_text("baseline\n", encoding="utf-8")
            commit_fixture(root)
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            target.write_text("value = 1\n", encoding="utf-8")
            outside.write_text("changed outside claim\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                submit_result(
                    root,
                    claim_id=claim["id"],
                    agent="codex",
                    summary="Must fail",
                    changed_files=["src/core.py"],
                    verifications=["python -m unittest::passed"],
                    evidence_refs=["EVD-0001"],
                    limitations=[],
                )

    def test_non_git_result_rejects_changes_outside_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            target = root / "src" / "core.py"
            outside = root / "README.md"
            outside.write_text("baseline\n", encoding="utf-8")
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            target.write_text("value = 2\n", encoding="utf-8")
            outside.write_text("unauthorized\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                submit_result(
                    root,
                    claim_id=claim["id"],
                    agent="codex",
                    summary="Must fail without Git too",
                    changed_files=["src/core.py"],
                    verifications=["python -m unittest::PASS"],
                    evidence_refs=["EVD-0001"],
                    limitations=[],
                )

    def test_audit_event_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            commit_fixture(root)
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            (root / "src" / "core.py").write_text("value = 2\n", encoding="utf-8")
            acquisition_events = sorted((root / ".harness" / "events").glob("EVT-*.json"))
            acquisition_events[-1].write_text("{}\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                submit_result(
                    root,
                    claim_id=claim["id"],
                    agent="codex",
                    summary="Tampered audit log",
                    changed_files=["src/core.py"],
                    verifications=["python -m unittest::PASS"],
                    evidence_refs=["EVD-0001"],
                    limitations=[],
                )

    def test_preclaim_tracked_audit_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            commit_fixture(root)
            event = sorted((root / ".harness" / "events").glob("EVT-*.json"))[0]
            event.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(HarnessError):
                acquire_claim(
                    root,
                    agent="codex",
                    task_id="TASK-0001",
                    paths=["src"],
                )

    def test_expired_claim_cannot_be_refreshed_or_submitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = create_ready_project(Path(temp) / "demo")
            add_verified_evidence(root)
            (root / "src").mkdir(exist_ok=True)
            (root / "src" / "core.py").write_text("value = 1\n", encoding="utf-8")
            claim = acquire_claim(root, agent="codex", task_id="TASK-0001", paths=["src"])
            stored, claim_path = get_claim(root, claim["id"])
            stored["expires_at"] = "2000-01-01T00:00:00Z"
            atomic_write_json(claim_path, stored)
            from project_harness.collaboration import refresh_claim

            with self.assertRaises(HarnessError):
                refresh_claim(root, claim_id=claim["id"], agent="codex", ttl_minutes=30)
            with self.assertRaises(HarnessError):
                submit_result(
                    root,
                    claim_id=claim["id"],
                    agent="codex",
                    summary="Expired",
                    changed_files=["src/core.py"],
                    verifications=["python -m unittest::passed"],
                    evidence_refs=["EVD-0001"],
                    limitations=[],
                )


if __name__ == "__main__":
    unittest.main()
