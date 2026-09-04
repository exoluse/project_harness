from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from .constants import (
    HARNESS_DIR,
    PROJECT_RECORD_ID,
    RECORD_DIRECTORIES,
    RECORD_EXTENSIONS,
)
from .record_documents import (
    MarkdownRecordError,
    read_markdown_record,
    render_markdown_record,
)


_LOCAL_FILESYSTEM_MUTEXES: dict[str, threading.RLock] = {}
_LOCAL_FILESYSTEM_MUTEXES_GUARD = threading.Lock()


def _local_filesystem_mutex(lock: Path) -> threading.RLock:
    """Queue same-process contenders before starting the filesystem timeout."""

    key = os.path.normcase(str(lock.resolve(strict=False)))
    with _LOCAL_FILESYSTEM_MUTEXES_GUARD:
        return _LOCAL_FILESYSTEM_MUTEXES.setdefault(key, threading.RLock())


class HarnessError(RuntimeError):
    """A user-actionable harness error."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def utc_after(minutes: int) -> str:
    return (datetime.now(UTC) + timedelta(minutes=minutes)).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise HarnessError(f"Cannot hash missing path: {path}")
    entries: list[dict[str, str]] = []
    for child in sorted(
        (candidate for candidate in path.rglob("*") if candidate.is_file()),
        key=lambda candidate: candidate.relative_to(path).as_posix().casefold(),
    ):
        entries.append(
            {
                "path": child.relative_to(path).as_posix(),
                "sha256": sha256_file(child),
            }
        )
    return sha256_bytes(canonical_json(entries).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    if path.suffix.casefold() == ".md":
        try:
            value, _body = read_markdown_record(path)
        except MarkdownRecordError as exc:
            raise HarnessError(f"Invalid Markdown record in {path}: {exc}") from exc
        return value
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"Expected a JSON object in {path}")
    return value


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    if path.suffix.casefold() == ".md":
        body: str | None = None
        if path.is_file():
            try:
                _record, body = read_markdown_record(path)
            except MarkdownRecordError as exc:
                raise HarnessError(
                    f"Refusing to overwrite invalid Markdown record {path}: {exc}"
                ) from exc
        atomic_write_text(path, render_markdown_record(value, body))
        return
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def find_project_root(start: str | Path | None = None) -> Path:
    current = Path(start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        harness = candidate / HARNESS_DIR
        # A copied template carries its runtime before it has an identity.
        if (harness / "project.json").is_file() or (
            harness / "tooling" / "project_harness"
        ).is_dir():
            return candidate
    raise HarnessError(
        f"No {HARNESS_DIR} found from {current}. Copy the harness folder here or run `init`."
    )


def run_git(root: Path, *args: str) -> tuple[int, str]:
    process = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return process.returncode, process.stdout.strip()


def git_head(root: Path) -> str | None:
    code, output = run_git(root, "rev-parse", "HEAD")
    return output if code == 0 else None


def git_common_dir(root: Path) -> Path | None:
    code, output = run_git(root, "rev-parse", "--git-common-dir")
    if code != 0 or not output:
        return None
    candidate = Path(output)
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve()


def git_status(root: Path) -> list[str]:
    process = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "status",
            "--short",
            "--untracked-files=all",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if process.returncode != 0:
        return []
    return [line.rstrip("\r") for line in process.stdout.split("\n") if line.strip()]


def git_changed_paths(root: Path, base_commit: str | None = None) -> set[str] | None:
    code, _output = run_git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return None
    commands: list[tuple[str, ...]] = [
        ("diff", "--name-only", "--relative", "-z"),
        ("diff", "--cached", "--name-only", "--relative", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ]
    if base_commit:
        commands.append(("diff", "--name-only", "--relative", "-z", base_commit, "HEAD"))
    changed: set[str] = set()
    for command in commands:
        process = subprocess.run(
            ["git", *command],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if process.returncode != 0:
            raise HarnessError(
                f"Unable to inspect Git changes with {' '.join(command)}: "
                + process.stderr.decode("utf-8", errors="replace").strip()
            )
        for raw in process.stdout.decode("utf-8", errors="surrogateescape").split("\0"):
            if raw:
                changed.add(normalize_claim_path(root, raw))
    return changed


def record_path(root: Path, kind: str, record_id: str) -> Path:
    if kind not in RECORD_DIRECTORIES:
        raise HarnessError(f"Unknown record kind: {kind}")
    directory, prefix = RECORD_DIRECTORIES[kind]
    if not re.fullmatch(rf"{re.escape(prefix)}\d{{4,}}", record_id):
        raise HarnessError(f"Invalid {kind} ID: {record_id!r}; expected {prefix}<digits>")
    canonical = root / HARNESS_DIR / directory / f"{record_id}{RECORD_EXTENSIONS[kind]}"
    if canonical.is_file() or RECORD_EXTENSIONS[kind] == ".json":
        return canonical
    legacy = canonical.with_suffix(".json")
    return legacy if legacy.is_file() else canonical


def iter_record_files(root: Path) -> Iterable[tuple[str, Path]]:
    for kind, (directory, _prefix) in RECORD_DIRECTORIES.items():
        base = root / HARNESS_DIR / directory
        if not base.exists():
            continue
        patterns = ("*.md", "*.json") if RECORD_EXTENSIONS[kind] == ".md" else ("*.json",)
        paths = sorted(
            {path for pattern in patterns for path in base.glob(pattern)},
            key=lambda path: path.name.casefold(),
        )
        for path in paths:
            yield kind, path


def load_record_index(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    records: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    for _kind, path in iter_record_files(root):
        record = load_json(path)
        record_id = record.get("id")
        if isinstance(record_id, str):
            if record_id in records:
                raise HarnessError(f"Duplicate record ID {record_id}: {paths[record_id]} and {path}")
            records[record_id] = record
            paths[record_id] = path
        if record.get("kind") == "feature":
            for criterion in record.get("completion_criteria", []):
                if isinstance(criterion, dict) and isinstance(criterion.get("id"), str):
                    criterion_id = criterion["id"]
                    if criterion_id in records:
                        raise HarnessError(
                            f"Duplicate record or completion criterion ID {criterion_id}"
                        )
                    records[criterion_id] = {
                        **criterion,
                        "kind": "completion_criterion",
                        "feature_id": record_id,
                    }
                    paths[criterion_id] = path
    project_path = root / HARNESS_DIR / "project.json"
    if project_path.is_file():
        project = load_json(project_path)
        for criterion in project.get("closure_contract", []):
            if isinstance(criterion, dict) and isinstance(criterion.get("id"), str):
                criterion_id = criterion["id"]
                if criterion_id in records:
                    raise HarnessError(
                        f"Duplicate record or closure criterion ID {criterion_id}"
                    )
                records[criterion_id] = {
                    **criterion,
                    "kind": "closure_criterion",
                    "project_id": PROJECT_RECORD_ID,
                }
                paths[criterion_id] = project_path
    return records, paths


def next_id(directory: Path, prefix: str, width: int = 4) -> str:
    highest = 0
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$", re.IGNORECASE)
    if directory.exists():
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.casefold() not in {".json", ".md"}:
                continue
            match = pattern.match(path.stem)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"{prefix}{highest + 1:0{width}d}"


def _process_start_token(pid: int) -> str | None:
    """Return a best-effort process creation token to detect PID reuse."""
    if pid <= 0:
        return None
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            process_query_limited_information = 0x1000
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [
                wintypes.DWORD,
                wintypes.BOOL,
                wintypes.DWORD,
            ]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetProcessTimes.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(wintypes.FILETIME),
                ctypes.POINTER(wintypes.FILETIME),
                ctypes.POINTER(wintypes.FILETIME),
                ctypes.POINTER(wintypes.FILETIME),
            ]
            kernel32.GetProcessTimes.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            handle = kernel32.OpenProcess(
                process_query_limited_information, False, pid
            )
            if not handle:
                return None
            try:
                creation = wintypes.FILETIME()
                exit_time = wintypes.FILETIME()
                kernel = wintypes.FILETIME()
                user = wintypes.FILETIME()
                if not kernel32.GetProcessTimes(
                    handle,
                    ctypes.byref(creation),
                    ctypes.byref(exit_time),
                    ctypes.byref(kernel),
                    ctypes.byref(user),
                ):
                    return None
                value = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
                return f"win-filetime:{value}"
            finally:
                kernel32.CloseHandle(handle)
        except (AttributeError, OSError, ValueError):
            return None
    stat_path = Path(f"/proc/{pid}/stat")
    try:
        value = stat_path.read_text(encoding="ascii")
        # Fields following the final ')' start at procfs field 3; starttime is
        # field 22. The command name itself may contain spaces and parentheses.
        fields = value[value.rfind(")") + 2 :].split()
        return f"procfs-start:{fields[19]}"
    except (FileNotFoundError, OSError, IndexError, UnicodeDecodeError):
        return None


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            process_query_limited_information = 0x1000
            still_active = 259
            error_access_denied = 5
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [
                wintypes.DWORD,
                wintypes.BOOL,
                wintypes.DWORD,
            ]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetExitCodeProcess.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(wintypes.DWORD),
            ]
            kernel32.GetExitCodeProcess.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            handle = kernel32.OpenProcess(
                process_query_limited_information, False, pid
            )
            if not handle:
                # Access denied means the process exists but this identity may
                # not inspect it. Fail closed and keep its lock.
                return ctypes.get_last_error() == error_access_denied
            try:
                exit_code = wintypes.DWORD()
                if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return True
                return exit_code.value == still_active
            finally:
                kernel32.CloseHandle(handle)
        except (AttributeError, OSError, ValueError):
            # An inconclusive Windows query must not authorize lock theft.
            return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _local_lock_owner_state(owner: dict[str, Any]) -> str:
    """Return ALIVE, DEAD, or UNKNOWN for an owner on the current host."""
    host = owner.get("host")
    if not isinstance(host, str) or host.casefold() != socket.gethostname().casefold():
        return "UNKNOWN"
    pid = owner.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return "UNKNOWN"
    if not _pid_is_alive(pid):
        return "DEAD"
    expected_token = owner.get("process_start_token")
    if not isinstance(expected_token, str) or not expected_token:
        # Fail closed when a live local PID cannot be disambiguated.
        return "ALIVE"
    actual_token = _process_start_token(pid)
    if actual_token is None:
        return "ALIVE"
    return "ALIVE" if actual_token == expected_token else "DEAD"


def _write_lock_recovery(
    directory: Path | None, lock: Path, previous_owner: dict[str, Any] | None
) -> None:
    if directory is None:
        return
    identifier = f"{time.time_ns()}-{uuid.uuid4().hex}"
    atomic_write_json(
        directory / f"{identifier}.json",
        {
            "schema": "harness.filesystem-lock-recovery/v1",
            "kind": "filesystem_lock_recovery",
            "lock": str(lock),
            "previous_owner": previous_owner,
            "recovered_at": utc_now(),
        },
    )


def _try_reclaim_filesystem_lock(
    lock: Path,
    *,
    stale_after_seconds: float,
    recovery_directory: Path | None,
) -> bool:
    owner: dict[str, Any] | None
    try:
        owner = load_json(lock / "owner.json")
    except OSError:
        # Windows can briefly deny shared reads while another process/thread
        # atomically installs the owner file. Treat that as a live/contended
        # lock and retry instead of attempting recovery or failing the caller.
        return False
    except HarnessError:
        owner = None

    if owner is not None:
        local_state = _local_lock_owner_state(owner)
        if local_state == "ALIVE":
            # A timestamp alone never authorizes stealing from a still-running
            # local process, including a long critical section past its lease.
            return False
        if local_state != "DEAD":
            try:
                expired = parse_utc(str(owner.get("expires_at", ""))) <= datetime.now(UTC)
            except (TypeError, ValueError):
                try:
                    expired = time.time() - lock.stat().st_mtime >= stale_after_seconds
                except FileNotFoundError:
                    return True
            if not expired:
                return False
    else:
        try:
            if time.time() - lock.stat().st_mtime < stale_after_seconds:
                return False
        except FileNotFoundError:
            return True

    quarantine = lock.with_name(f"{lock.name}.reclaim-{uuid.uuid4().hex}")
    try:
        os.replace(lock, quarantine)
    except FileNotFoundError:
        return True
    except OSError:
        return False
    try:
        _write_lock_recovery(recovery_directory, lock, owner)
    finally:
        shutil.rmtree(quarantine, ignore_errors=True)
    return True


@contextmanager
def filesystem_mutex(
    lock: Path,
    *,
    timeout_seconds: float = 5.0,
    lease_seconds: float = 300.0,
    recovery_directory: Path | None = None,
    timeout_message: str = "Timed out waiting for a filesystem lock",
):
    """Acquire an atomic directory lock with owner identity and stale recovery."""
    if timeout_seconds <= 0:
        raise HarnessError("Filesystem lock timeout must be greater than zero")
    if lease_seconds <= 0:
        raise HarnessError("Filesystem lock lease must be greater than zero")
    with _local_filesystem_mutex(lock):
        lock.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + timeout_seconds
        nonce = uuid.uuid4().hex
        owner = {
            "schema": "harness.filesystem-lock/v1",
            "kind": "filesystem_lock",
            "nonce": nonce,
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "process_start_token": _process_start_token(os.getpid()),
            "acquired_at": utc_now(),
            "expires_at": (
                datetime.now(UTC) + timedelta(seconds=lease_seconds)
            ).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
        while True:
            try:
                lock.mkdir()
                try:
                    atomic_write_json(lock / "owner.json", owner)
                except Exception:
                    shutil.rmtree(lock, ignore_errors=True)
                    raise
                break
            except FileExistsError:
                if _try_reclaim_filesystem_lock(
                    lock,
                    stale_after_seconds=lease_seconds,
                    recovery_directory=recovery_directory,
                ):
                    continue
                if time.monotonic() >= deadline:
                    raise HarnessError(timeout_message)
                time.sleep(0.05)
        try:
            yield owner
        finally:
            try:
                current_owner = load_json(lock / "owner.json")
            except HarnessError:
                current_owner = None
            if current_owner is not None and current_owner.get("nonce") == nonce:
                try:
                    (lock / "owner.json").unlink()
                    lock.rmdir()
                except FileNotFoundError:
                    pass
                except OSError:
                    # Never remove a directory whose contents changed while held.
                    pass


def allocate_record_id(root: Path, directory: Path, prefix: str, width: int = 4) -> str:
    common = git_common_dir(root)
    allocator_root = (
        common / "project-harness-runtime" / "id-sequences"
        if common is not None
        else root / HARNESS_DIR / "runtime" / "id-sequences"
    )
    allocator_root.mkdir(parents=True, exist_ok=True)
    lock = allocator_root / f"{prefix.rstrip('-').casefold()}.lock"
    with filesystem_mutex(
        lock,
        recovery_directory=allocator_root / "lock-recoveries",
        timeout_message=f"Timed out allocating a unique {prefix} ID; inspect its lock owner metadata",
    ):
        counter_path = allocator_root / f"{prefix.rstrip('-').casefold()}.txt"
        counter = 0
        if counter_path.is_file():
            try:
                counter = int(counter_path.read_text(encoding="ascii").strip())
            except ValueError as exc:
                raise HarnessError(f"Invalid shared ID counter: {counter_path}") from exc
        local_next = next_id(directory, prefix, width)
        local_number = int(local_next.removeprefix(prefix))
        number = max(counter + 1, local_number)
        atomic_write_text(counter_path, f"{number}\n")
        return f"{prefix}{number:0{width}d}"


def subject_fingerprint(record: dict[str, Any]) -> str:
    kind = record.get("kind")
    projected: Any
    if kind == "plan":
        projected = record["approval_subject"]
    elif kind == "requirement":
        projected = {
            key: record.get(key)
            for key in ("required", "priority", "statement", "source_refs", "acceptance_criteria")
        }
    elif kind == "feature":
        projected_criteria = []
        for criterion in record.get("completion_criteria", []):
            projected_criteria.append(
                {
                    key: criterion.get(key)
                    for key in (
                        "id",
                        "statement",
                        "required",
                        "verification_plan",
                        "required_profiles",
                        "required_bindings",
                    )
                }
            )
        projected = {
            "required": record.get("required"),
            "requirement_refs": record.get("requirement_refs"),
            "completion_criteria": projected_criteria,
            "customer_acceptance_required": record.get("customer_acceptance_required"),
        }
    elif kind == "work_item":
        projected = {
            key: record.get(key)
            for key in (
                "plan_id",
                "feature_refs",
                "criterion_refs",
                "dependencies",
                "blocked_by",
                "write_scope",
                "preexisting_dirty_paths",
                "logical_locks",
                "verification",
                "risk",
                "capabilities",
                "capability_approval_refs",
                "forbidden_actions",
            )
        }
    elif kind == "change":
        projected = {
            key: record.get(key)
            for key in ("classification", "source_refs", "affects", "impact")
        }
    elif kind == "completion_criterion":
        projected = {
            key: record.get(key)
            for key in (
                "feature_id",
                "statement",
                "required",
                "verification_plan",
                "required_profiles",
                "required_bindings",
            )
        }
    elif kind == "closure_criterion":
        projected = {
            key: record.get(key)
            for key in (
                "project_id",
                "required",
                "required_profiles",
            )
        }
    elif kind == "project":
        projected_closure_contract = []
        for criterion in record.get("closure_contract", []):
            if not isinstance(criterion, dict):
                projected_closure_contract.append(criterion)
                continue
            projected_closure_contract.append(
                {
                    key: criterion.get(key)
                    for key in (
                        "id",
                        "required",
                        "required_profiles",
                    )
                }
                | {"evidence_refs": []}
            )
        projected = {
            "required_features": record.get("required_features"),
            "closure_contract": projected_closure_contract,
            "policy": record.get("policy"),
        }
    else:
        projected = record
    identity = {
        "schema": record.get("schema"),
        "id": record.get("id"),
        "version": record.get("version"),
        "approval_subject": projected,
    }
    return sha256_bytes(canonical_json(identity).encode("utf-8"))


def normalize_agent_id(value: str) -> str:
    normalized = value.strip().casefold()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{0,63}", normalized):
        raise HarnessError(
            "Agent IDs must start with a letter or number and contain only "
            "letters, numbers, dot, underscore, or hyphen"
        )
    return normalized


def subject_fingerprint_for_path(path: Path) -> str:
    record = load_json(path)
    identity = {
        "subject": subject_fingerprint(record),
        "dependencies": {},
    }
    dependencies = record.get("approval_dependencies", [])
    if dependencies:
        if not isinstance(dependencies, list) or any(
            not isinstance(value, str) for value in dependencies
        ):
            raise HarnessError("approval_dependencies must be a string list")
        root = find_project_root(path)
        for value in sorted(dependencies, key=str.casefold):
            normalized = normalize_claim_path(root, value)
            dependency_path = root / normalized
            if not dependency_path.is_file():
                raise HarnessError(f"Approval dependency is missing: {value}")
            identity["dependencies"][normalized] = subject_fingerprint(load_json(dependency_path))
    return sha256_bytes(canonical_json(identity).encode("utf-8"))


def normalize_claim_path(root: Path, value: str) -> str:
    raw = value.strip().replace("\\", "/")
    if raw == "**":
        return raw
    if not raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise HarnessError(f"Claim paths must be relative to the repository: {value!r}")
    if any(part in {"", ".", ".."} for part in raw.split("/")):
        raise HarnessError(f"Unsafe or non-normalized claim path: {value!r}")
    target = (root / raw).resolve(strict=False)
    try:
        relative = target.relative_to(root.resolve())
    except ValueError as exc:
        raise HarnessError(f"Claim path escapes the repository: {value!r}") from exc
    normalized = relative.as_posix().rstrip("/")
    if not normalized:
        raise HarnessError("Use ** for a workspace-exclusive claim")
    return normalized


def paths_overlap(left: str, right: str) -> bool:
    left = left.replace("\\", "/").casefold()
    right = right.replace("\\", "/").casefold()
    if left == "**" or right == "**":
        return True
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def is_path_within(path: str, allowed: Iterable[str]) -> bool:
    folded = path.replace("\\", "/").casefold()
    normalized_allowed = [candidate.replace("\\", "/").casefold() for candidate in allowed]
    return any(
        candidate == "**" or folded == candidate or folded.startswith(candidate + "/")
        for candidate in normalized_allowed
    )


def record_event(root: Path, event_type: str, payload: dict[str, Any]) -> Path:
    events = root / HARNESS_DIR / "events"
    event_id = allocate_record_id(root, events, "EVT-")
    value = {
        "schema": "harness.event/v1",
        "id": event_id,
        "kind": "event",
        "event_type": event_type,
        "occurred_at": utc_now(),
        "payload": payload,
    }
    path = events / f"{event_id}.json"
    atomic_write_json(path, value)
    return path


def binding_status(root: Path, binding: dict[str, Any]) -> tuple[bool, str]:
    value = binding.get("path")
    expected = binding.get("sha256")
    if not isinstance(value, str) or not isinstance(expected, str):
        return False, "binding requires path and sha256"
    try:
        normalized = normalize_claim_path(root, value)
    except HarnessError as exc:
        return False, str(exc)
    path = root / normalized
    if not path.exists():
        return False, f"bound file is missing: {value}"
    actual = sha256_path(path)
    if actual != expected:
        return False, f"bound file hash changed: {value}"
    return True, "current"
