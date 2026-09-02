from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .approvals import (
    approval_assurance,
    approval_status,
    prepare_approval_request,
    record_procedural_approval,
    record_signed_approval,
)
from .collaboration import (
    acquire_claim,
    acknowledge_mailbox,
    create_handoff,
    get_claim,
    list_claims,
    list_mailbox,
    recover_claim,
    refresh_claim,
    release_claim,
)
from .constants import (
    EXIT_BLOCKED,
    EXIT_INVALID,
    EXIT_PASS,
    EXIT_STALE,
    EXIT_USAGE,
    RECORD_DIRECTORIES,
    RECORD_KIND_ALIASES,
)
from .core import (
    HarnessError,
    atomic_write_json,
    find_project_root,
    load_json,
    normalize_claim_path,
    record_path,
    subject_fingerprint_for_path,
)
from .gates import (
    feature_completion_gate,
    plan_preflight_gate,
    project_completion_gate,
    task_start_gate,
)
from .lifecycle import apply_plan_decision
from .mutations import record_evidence, transition_record
from .reporting import (
    completion_report,
    decision_package,
    doctor_report,
    pretty,
    status_report,
    trace_report,
)
from .scaffold import init_project, new_record
from .validation import issue_counts, validate_project
from .workflow import dispatch_task, review_result, submit_result


def _root(args: argparse.Namespace) -> Path:
    return find_project_root(args.root)


def _print(value, as_json: bool = False) -> None:
    if as_json or isinstance(value, (dict, list)):
        print(pretty(value))
    else:
        print(value)


def cmd_init(args: argparse.Namespace) -> int:
    root = init_project(Path(args.path), args.project_id, args.name, force=args.force)
    print(f"Initialized project harness at {root}")
    return EXIT_PASS


def cmd_doctor(args: argparse.Namespace) -> int:
    report = doctor_report(_root(args))
    _print(report, args.json)
    return EXIT_INVALID if report["validation"]["errors"] else EXIT_PASS


def cmd_status(args: argparse.Namespace) -> int:
    _print(status_report(_root(args)), args.json)
    return EXIT_PASS


def cmd_validate(args: argparse.Namespace) -> int:
    issues = validate_project(_root(args))
    result = {"issues": [item.as_dict() for item in issues], "counts": issue_counts(issues)}
    _print(result, args.json)
    if result["counts"]["errors"]:
        return EXIT_INVALID
    if args.strict and result["counts"]["warnings"]:
        return EXIT_INVALID
    return EXIT_PASS


def cmd_new(args: argparse.Namespace) -> int:
    root = _root(args)
    kind = RECORD_KIND_ALIASES.get(args.kind, args.kind)
    if kind not in RECORD_DIRECTORIES or kind in {
        "approval",
        "handoff",
        "result",
        "review",
    }:
        raise HarnessError(f"Unsupported generic record kind: {args.kind}")
    _directory, prefix = RECORD_DIRECTORIES[kind]
    if not args.id.startswith(prefix):
        raise HarnessError(f"{kind} IDs must start with {prefix}")
    path = record_path(root, kind, args.id)
    if path.exists():
        raise HarnessError(f"Record already exists: {args.id}")
    value = new_record(kind, args.id, args.title)
    atomic_write_json(path, value)
    _print({"created": str(path.relative_to(root)), "record": value}, args.json)
    return EXIT_PASS


def cmd_fingerprint(args: argparse.Namespace) -> int:
    root = _root(args)
    path = root / normalize_claim_path(root, args.path)
    print(subject_fingerprint_for_path(path))
    return EXIT_PASS


def cmd_approval_prepare(args: argparse.Namespace) -> int:
    value = prepare_approval_request(
        _root(args),
        output_path=args.output,
        approval_type=args.type,
        subject_path=args.subject,
        decision=args.decision,
        approver=args.approver,
        authority_role=args.authority_role,
        basis=args.basis,
        conditions=args.condition,
        condition_refs=args.condition_ref,
        authorized_actions=args.authorized_action,
        excluded_actions=args.excluded_action,
        ttl_minutes=args.ttl_minutes,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_approval_record(args: argparse.Namespace) -> int:
    value = record_signed_approval(
        _root(args), request_path=args.request, signature_path=args.signature
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_approval_confirm(args: argparse.Namespace) -> int:
    value = record_procedural_approval(
        _root(args),
        approval_type=args.type,
        subject_path=args.subject,
        decision=args.decision,
        approver=args.approver,
        basis=args.basis,
        confirm_fingerprint=args.confirm_fingerprint,
        confirmation_id=args.confirmation_id,
        confirmation_channel=args.confirmation_channel,
        confirmation_reference=args.confirmation_reference,
        conditions=args.condition,
        condition_refs=args.condition_ref,
        authorized_actions=args.authorized_action,
        excluded_actions=args.excluded_action,
        acknowledge_procedural=args.acknowledge_procedural,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_approval_check(args: argparse.Namespace) -> int:
    root = _root(args)
    approval = load_json(record_path(root, "approval", args.id))
    status, reason = approval_status(root, approval)
    _print(
        {
            "id": args.id,
            "status": status,
            "reason": reason,
            "assurance": approval_assurance(approval),
        },
        args.json,
    )
    if status == "CURRENT":
        return EXIT_PASS
    return EXIT_STALE if status in {"STALE", "SUPERSEDED"} else EXIT_BLOCKED


def cmd_plan_apply_decision(args: argparse.Namespace) -> int:
    value = apply_plan_decision(_root(args), approval_id=args.approval)
    _print(value, args.json)
    return EXIT_PASS


def _gate_result(result, as_json: bool) -> int:
    _print(result.as_dict(), as_json)
    return EXIT_PASS if result.passed else EXIT_BLOCKED


def cmd_gate_plan(args: argparse.Namespace) -> int:
    return _gate_result(
        plan_preflight_gate(_root(args), args.id, require_approval=args.require_approval),
        args.json,
    )


def cmd_gate_task(args: argparse.Namespace) -> int:
    return _gate_result(task_start_gate(_root(args), args.id), args.json)


def cmd_gate_feature(args: argparse.Namespace) -> int:
    return _gate_result(feature_completion_gate(_root(args), args.id), args.json)


def cmd_gate_project(args: argparse.Namespace) -> int:
    return _gate_result(project_completion_gate(_root(args)), args.json)


def cmd_claim_acquire(args: argparse.Namespace) -> int:
    value = acquire_claim(
        _root(args),
        agent=args.agent,
        task_id=args.task,
        paths=args.paths,
        logical_locks=args.logical_lock,
        ttl_minutes=args.ttl_minutes,
        handoff_id=args.handoff,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_claim_list(args: argparse.Namespace) -> int:
    _print(list_claims(_root(args), active_only=args.active), args.json)
    return EXIT_PASS


def cmd_claim_release(args: argparse.Namespace) -> int:
    value = release_claim(
        _root(args), claim_id=args.id, agent=args.agent, reason=args.reason
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_claim_refresh(args: argparse.Namespace) -> int:
    value = refresh_claim(
        _root(args), claim_id=args.id, agent=args.agent, ttl_minutes=args.ttl_minutes
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_claim_recover(args: argparse.Namespace) -> int:
    value = recover_claim(
        _root(args),
        claim_id=args.id,
        agent=args.agent,
        reason=args.reason,
        recovery_manifest=args.recovery_manifest,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_mailbox_list(args: argparse.Namespace) -> int:
    values = list_mailbox(
        _root(args),
        box=args.box,
        agent=args.agent,
        include_acknowledged=args.all,
    )
    _print(values, args.json)
    return EXIT_PASS


def cmd_mailbox_ack(args: argparse.Namespace) -> int:
    value = acknowledge_mailbox(
        _root(args), box=args.box, agent=args.agent, item_id=args.id
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_handoff_create(args: argparse.Namespace) -> int:
    value = create_handoff(
        _root(args),
        claim_id=args.claim,
        from_agent=args.from_agent,
        to_agent=args.to_agent,
        task_id=args.task,
        summary=args.summary,
        changed_files=args.changed_file,
        verifications=args.verification,
        next_action=args.next_action,
        decisions=args.decision,
        risks=args.risk,
        unverified=args.unverified,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_trace(args: argparse.Namespace) -> int:
    _print(trace_report(_root(args), args.id), args.json)
    return EXIT_PASS


def cmd_report_decision_package(args: argparse.Namespace) -> int:
    value = decision_package(_root(args), args.id)
    _print(value, args.json)
    return EXIT_PASS if value["preflight"]["passed"] else EXIT_BLOCKED


def cmd_report_completion(args: argparse.Namespace) -> int:
    value = completion_report(_root(args))
    _print(value, args.json)
    return EXIT_PASS if value["authorized_closure"]["passed"] else EXIT_BLOCKED


def cmd_dispatch(args: argparse.Namespace) -> int:
    value = dispatch_task(
        _root(args),
        task_id=args.task,
        to_agent=args.to_agent,
        issued_by=args.issued_by,
        instructions=args.instructions,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_result_submit(args: argparse.Namespace) -> int:
    value = submit_result(
        _root(args),
        claim_id=args.claim,
        agent=args.agent,
        summary=args.summary,
        changed_files=args.changed_file,
        verifications=args.verification,
        evidence_refs=args.evidence,
        limitations=args.limitation,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_review_record(args: argparse.Namespace) -> int:
    value = review_result(
        _root(args),
        result_id=args.result,
        reviewer=args.reviewer,
        decision=args.decision,
        basis=args.basis,
        checks=args.check,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_evidence_record(args: argparse.Namespace) -> int:
    value = record_evidence(
        _root(args),
        claim_id=args.claim_id,
        agent=args.agent,
        claim_text=args.claim_text,
        supports=args.support,
        profile=args.profile,
        method=args.method,
        environment=args.environment,
        expected=args.expected,
        actual=args.actual,
        result=args.result,
        ambiguity_level=args.ambiguity_level,
        ambiguity_reasons=args.ambiguity_reason,
        binding_paths=args.binding,
        limitations=args.limitation,
    )
    _print(value, args.json)
    return EXIT_PASS


def cmd_transition_record(args: argparse.Namespace) -> int:
    value = transition_record(
        _root(args),
        claim_id=args.claim_id,
        agent=args.agent,
        kind=args.kind,
        record_id=args.id,
        target_status=args.to,
        reason=args.reason,
        rework=args.rework,
    )
    _print(value, args.json)
    return EXIT_PASS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-harness")
    parser.add_argument("--root", default=".", help="project directory or a path inside it")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize a project harness")
    init.add_argument("path")
    init.add_argument("--project-id", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    doctor = sub.add_parser("doctor")
    doctor.set_defaults(func=cmd_doctor)
    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)
    validate = sub.add_parser("validate")
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=cmd_validate)

    new = sub.add_parser("new", help="create a canonical record draft")
    new.add_argument("kind", choices=sorted(set(RECORD_DIRECTORIES) | set(RECORD_KIND_ALIASES)))
    new.add_argument("id")
    new.add_argument("title")
    new.set_defaults(func=cmd_new)

    fingerprint = sub.add_parser("fingerprint")
    fingerprint.add_argument("path")
    fingerprint.set_defaults(func=cmd_fingerprint)

    approval = sub.add_parser("approval")
    approval_sub = approval.add_subparsers(dest="approval_command", required=True)
    approval_prepare = approval_sub.add_parser("prepare")
    approval_prepare.add_argument("--output", required=True)
    approval_prepare.add_argument("--type", required=True)
    approval_prepare.add_argument("--subject", required=True)
    approval_prepare.add_argument("--decision", required=True)
    approval_prepare.add_argument("--approver", required=True)
    approval_prepare.add_argument("--authority-role", default="HUMAN_PROJECT_OWNER")
    approval_prepare.add_argument("--basis", required=True)
    approval_prepare.add_argument("--condition", action="append", default=[])
    approval_prepare.add_argument("--condition-ref", action="append", default=[])
    approval_prepare.add_argument("--authorized-action", action="append", default=[])
    approval_prepare.add_argument("--excluded-action", action="append", default=[])
    approval_prepare.add_argument("--ttl-minutes", type=int, default=60)
    approval_prepare.set_defaults(func=cmd_approval_prepare)
    approval_record = approval_sub.add_parser("record")
    approval_record.add_argument("--request", required=True)
    approval_record.add_argument("--signature", required=True)
    approval_record.set_defaults(func=cmd_approval_record)
    approval_confirm = approval_sub.add_parser(
        "confirm",
        help="record a non-authenticating procedural PLAN confirmation",
    )
    approval_confirm.add_argument("--type", required=True)
    approval_confirm.add_argument("--subject", required=True)
    approval_confirm.add_argument("--decision", required=True)
    approval_confirm.add_argument("--approver", required=True)
    approval_confirm.add_argument("--basis", required=True)
    approval_confirm.add_argument("--confirm-fingerprint", required=True)
    approval_confirm.add_argument("--confirmation-id", required=True)
    approval_confirm.add_argument("--confirmation-channel", required=True)
    approval_confirm.add_argument("--confirmation-reference", required=True)
    approval_confirm.add_argument("--condition", action="append", default=[])
    approval_confirm.add_argument("--condition-ref", action="append", default=[])
    approval_confirm.add_argument("--authorized-action", action="append", default=[])
    approval_confirm.add_argument("--excluded-action", action="append", default=[])
    approval_confirm.add_argument("--acknowledge-procedural", action="store_true")
    approval_confirm.set_defaults(func=cmd_approval_confirm)
    approval_check = approval_sub.add_parser("check")
    approval_check.add_argument("id")
    approval_check.set_defaults(func=cmd_approval_check)

    plan = sub.add_parser("plan", help="manage plan lifecycle decisions")
    plan_sub = plan.add_subparsers(dest="plan_command", required=True)
    plan_apply = plan_sub.add_parser(
        "apply-decision",
        help="materialize a current PLAN approval into plan and project state",
    )
    plan_apply.add_argument("--approval", required=True)
    plan_apply.set_defaults(func=cmd_plan_apply_decision)

    gate = sub.add_parser("gate")
    gate_sub = gate.add_subparsers(dest="gate_command", required=True)
    gate_plan = gate_sub.add_parser("plan")
    gate_plan.add_argument("id")
    gate_plan.add_argument("--require-approval", action="store_true")
    gate_plan.set_defaults(func=cmd_gate_plan)
    gate_task = gate_sub.add_parser("task")
    gate_task.add_argument("id")
    gate_task.set_defaults(func=cmd_gate_task)
    gate_feature = gate_sub.add_parser("feature")
    gate_feature.add_argument("id")
    gate_feature.set_defaults(func=cmd_gate_feature)
    gate_project = gate_sub.add_parser("project")
    gate_project.set_defaults(func=cmd_gate_project)

    claim = sub.add_parser("claim")
    claim_sub = claim.add_subparsers(dest="claim_command", required=True)
    claim_acquire = claim_sub.add_parser("acquire")
    claim_acquire.add_argument("--agent", required=True)
    claim_acquire.add_argument("--task", required=True)
    claim_acquire.add_argument("--paths", nargs="+")
    claim_acquire.add_argument("--logical-lock", action="append", default=None)
    claim_acquire.add_argument("--ttl-minutes", type=int, default=120)
    claim_acquire.add_argument("--handoff")
    claim_acquire.set_defaults(func=cmd_claim_acquire)
    claim_list = claim_sub.add_parser("list")
    claim_list.add_argument("--active", action="store_true")
    claim_list.set_defaults(func=cmd_claim_list)
    claim_release = claim_sub.add_parser("release")
    claim_release.add_argument("id")
    claim_release.add_argument("--agent", required=True)
    claim_release.add_argument("--reason")
    claim_release.set_defaults(func=cmd_claim_release)
    claim_refresh = claim_sub.add_parser("refresh")
    claim_refresh.add_argument("id")
    claim_refresh.add_argument("--agent", required=True)
    claim_refresh.add_argument("--ttl-minutes", type=int, default=120)
    claim_refresh.set_defaults(func=cmd_claim_refresh)
    claim_recover = claim_sub.add_parser("recover")
    claim_recover.add_argument("id")
    claim_recover.add_argument("--agent", required=True)
    claim_recover.add_argument("--reason", required=True)
    claim_recover.add_argument("--recovery-manifest", required=True)
    claim_recover.set_defaults(func=cmd_claim_recover)

    mailbox = sub.add_parser("mailbox")
    mailbox_sub = mailbox.add_subparsers(dest="mailbox_command", required=True)
    mailbox_list = mailbox_sub.add_parser("list")
    mailbox_list.add_argument("--box", choices=["inbox", "outbox"], default="inbox")
    mailbox_list.add_argument("--agent", required=True)
    mailbox_list.add_argument("--all", action="store_true")
    mailbox_list.set_defaults(func=cmd_mailbox_list)
    mailbox_ack = mailbox_sub.add_parser("ack")
    mailbox_ack.add_argument("--box", choices=["inbox", "outbox"], default="inbox")
    mailbox_ack.add_argument("--agent", required=True)
    mailbox_ack.add_argument("--id", required=True)
    mailbox_ack.set_defaults(func=cmd_mailbox_ack)

    handoff = sub.add_parser("handoff")
    handoff_sub = handoff.add_subparsers(dest="handoff_command", required=True)
    handoff_create = handoff_sub.add_parser("create")
    handoff_create.add_argument("--claim", required=True)
    handoff_create.add_argument("--from-agent", required=True)
    handoff_create.add_argument("--to-agent", required=True)
    handoff_create.add_argument("--task", required=True)
    handoff_create.add_argument("--summary", required=True)
    handoff_create.add_argument("--changed-file", action="append", default=[])
    handoff_create.add_argument("--verification", action="append", default=[])
    handoff_create.add_argument("--unverified", action="append", default=[])
    handoff_create.add_argument("--decision", action="append", default=[])
    handoff_create.add_argument("--risk", action="append", default=[])
    handoff_create.add_argument("--next-action", required=True)
    handoff_create.set_defaults(func=cmd_handoff_create)

    dispatch = sub.add_parser("dispatch")
    dispatch.add_argument("--task", required=True)
    dispatch.add_argument("--to-agent", required=True)
    dispatch.add_argument("--issued-by", required=True)
    dispatch.add_argument("--instructions", required=True)
    dispatch.set_defaults(func=cmd_dispatch)

    result = sub.add_parser("result")
    result_sub = result.add_subparsers(dest="result_command", required=True)
    result_submit = result_sub.add_parser("submit")
    result_submit.add_argument("--claim", required=True)
    result_submit.add_argument("--agent", required=True)
    result_submit.add_argument("--summary", required=True)
    result_submit.add_argument("--changed-file", action="append", default=[])
    result_submit.add_argument("--verification", action="append", default=[])
    result_submit.add_argument("--evidence", action="append", default=[])
    result_submit.add_argument("--limitation", action="append", default=[])
    result_submit.set_defaults(func=cmd_result_submit)

    review = sub.add_parser("review")
    review_sub = review.add_subparsers(dest="review_command", required=True)
    review_record = review_sub.add_parser("record")
    review_record.add_argument("--result", required=True)
    review_record.add_argument("--reviewer", required=True)
    review_record.add_argument("--decision", required=True)
    review_record.add_argument("--basis", required=True)
    review_record.add_argument("--check", action="append", default=[])
    review_record.set_defaults(func=cmd_review_record)

    evidence = sub.add_parser("evidence", help="record governed criterion evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_command", required=True)
    evidence_record = evidence_sub.add_parser("record")
    evidence_record.add_argument("--claim-id")
    evidence_record.add_argument("--agent", required=True)
    evidence_record.add_argument("--claim-text", required=True)
    evidence_record.add_argument("--support", action="append", required=True)
    evidence_record.add_argument("--profile", required=True)
    evidence_record.add_argument("--method", required=True)
    evidence_record.add_argument("--environment", required=True)
    evidence_record.add_argument("--expected", required=True)
    evidence_record.add_argument("--actual", required=True)
    evidence_record.add_argument(
        "--result",
        required=True,
        choices=[
            "NOT_TESTED",
            "COLLECTED",
            "PARTIAL",
            "INCONCLUSIVE",
            "FAILED",
            "VERIFIED",
            "STALE",
            "REVOKED",
        ],
    )
    evidence_record.add_argument(
        "--ambiguity-level",
        default="NONE",
        choices=["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )
    evidence_record.add_argument("--ambiguity-reason", action="append", default=[])
    evidence_record.add_argument("--binding", action="append", default=[])
    evidence_record.add_argument("--limitation", action="append", default=[])
    evidence_record.set_defaults(func=cmd_evidence_record)

    transition = sub.add_parser("transition", help="apply a governed record transition")
    transition.add_argument(
        "--kind",
        required=True,
        choices=["project", "requirement", "feature", "work_item"],
    )
    transition.add_argument("--id", required=True)
    transition.add_argument("--to", required=True)
    transition.add_argument("--claim-id")
    transition.add_argument("--agent", required=True)
    transition.add_argument("--reason", required=True)
    transition.add_argument("--rework", action="store_true")
    transition.set_defaults(func=cmd_transition_record)

    trace = sub.add_parser("trace")
    trace.add_argument("id")
    trace.set_defaults(func=cmd_trace)

    report = sub.add_parser("report")
    report_sub = report.add_subparsers(dest="report_command", required=True)
    report_decision = report_sub.add_parser("decision-package")
    report_decision.add_argument("id")
    report_decision.set_defaults(func=cmd_report_decision_package)
    report_completion = report_sub.add_parser("completion")
    report_completion.set_defaults(func=cmd_report_completion)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except HarnessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return EXIT_USAGE
