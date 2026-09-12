# Record Format

Status: **decided on 2026-09-06, not yet implemented.** Today `PLAN-*` and
`TASK-*` are Markdown with strict front matter and every other canonical record
is JSON. The decision below makes Markdown the format of every canonical record
and of the project and state files, leaving JSON only where a file's exact bytes
are what a signature or a snapshot binds. Until the runtime change lands,
`AGENTS.md` and `docs/DATA_MODEL.md` describe the current split and it stays in
force.

## Decision

Every canonical record is a `.md` file: a strict front-matter block that holds
the complete schema-validated record, followed by a Markdown body for people.
This extends what PLAN and TASK already do to sources, artifacts, requirements,
features, open items, changes, evidence, approvals, results, reviews,
handoffs, recoveries, events, and to `project.md` and `state.md`.

The owner chose this knowing the cost: state and events are never written by a
person, so their body is an empty slot, and machine payloads lose the uniformity
of one serialization. The gain is that the whole record tree reads in any
Markdown viewer, diffs as prose, and every record has a place for the human
explanation that the front matter cannot carry.

## What stays JSON, and why

| Path | Reason |
|---|---|
| `.harness/decisions/*.request.json` and `.sig` | The SSH signature is verified over the request file's raw bytes. The signed bytes are the artifact; they are not re-rendered. |
| `.harness/baselines/<APR>/…` | Verbatim copies of the subject and dependency files at approval time. They take whatever extension the source has, so after this change they are `.md` copies; nothing is re-serialized. |
| `<git-common-dir>/project-harness-runtime/` and `.harness/runtime/` | Leases, mailboxes, mutation journals, id sequences, human-decision markers, and reset manifests are transient runtime state, not records. They stay JSON. |
| Protected authority config and decision ledger outside the repository | Owned by the external authority, not the harness. |

## Rules

1. **Front matter is the record.** Validation, fingerprints, gates, and
   approvals read the front matter only. This is already true for PLAN and
   TASK and becomes true for every record. The body never grants, changes, or
   revokes anything.
2. **Same grammar everywhere.** The dependency-free front-matter subset stays as
   it is: two-space indentation, string keys, JSON-compatible quoted scalars,
   arrays, and objects. Duplicate keys, tabs, mixed containers, and malformed
   values fail closed. Every existing record shape, including nested approval
   attestations and evidence bindings, is representable in it.
3. **Machine-written records get an empty body.** Commands that create
   evidence, approvals, results, reviews, events, recoveries, and state write
   the front matter and a one-line note that the canonical fields are above.
   A person may add prose afterwards; mutations preserve it.
4. **Preserve meaning and existing bindings.** Rendering the same parsed record
   as Markdown must preserve its governed values. Approval payloads also bind
   paths, and PLAN fingerprints include dependency paths, so a format migration
   must not assume every existing digest remains current. Preserve the original
   decision payloads, signatures, snapshots and hashes; implement and test a
   versioned compatibility contract before changing their path resolution.
5. **A format change is not a new owner decision.** Approval subjects are canonical paths.
   After migration a feature is `.harness/features/FUNC-0003.md` and a change is
   `.harness/changes/CR-0004.md`; the project file is `.harness/project.md`. An
   extension change alone must not require the owner to approve the same scope
   again. Migration must verify the old-to-new subject and dependency mapping
   without widening authority or rewriting signed decisions. If compatibility
   cannot be established, report a migration blocker and leave the affected
   records in their supported format. Current runtime gates remain in force;
   this future policy does not authorize redirecting approval paths today.
6. **Legacy JSON stays readable.** The loader already reads a `.json` record
   when the `.md` is absent. A tree with mixed formats validates; a record
   present in both formats is an error. New records are always `.md`.
7. **Line endings.** `.harness/.gitattributes` pins `*.md text eol=lf` and
   `*.json text eol=lf` so fingerprint inputs do not vary by platform.
8. **Names in policy and code.** `project.json` and `state.json` become
   `project.md` and `state.md` wherever policy text, `next`, `doctor`, and the
   scaffold name them. The reserved project id `PROJECT` and every schema id
   are unchanged.

## Migration

The future `records migrate` command first validates the proposed conversion
and approval/dependency compatibility for the affected records. It reports the
path mapping, preserved decisions and any blockers in `--dry-run`. Only a
compatible conversion is applied atomically: records are rendered as Markdown
with an empty body, and source JSON is removed only after record readability
and approval applicability are verified. Failure leaves the original records
usable. Baselines and signed payloads are not rewritten. A format-only migration
does not generate a list of new owner approvals.

A copied harness that has never run `init` has nothing to migrate; `init` on
`harness.project/v2` creates `project.md` and `state.md` directly.

## What changes in the runtime

| Area | Change |
|---|---|
| `constants.py` | `RECORD_EXTENSIONS` maps every kind to `.md`; project and state file names become `project.md`, `state.md` |
| `core.py` | `load_json` and the record writer already branch on extension; project/state readers switch to the record path helper |
| `scaffold.py` | `init` writes `project.md`, `state.md`, and the widened `.gitattributes`; `reset` removes the `.md` identity files |
| `approvals.py` | versioned compatibility for migrated subject/dependency paths; preserve existing decision payloads and baselines; request files remain JSON |
| `record_documents.py` | empty-body rendering for machine-written kinds |
| `mutation_service.py`, `evidence_mutations.py`, `lifecycle_mutations.py` | write through the Markdown renderer for every kind |
| `guidance.py`, `reporting.py`, `doctor` | name `project.md` and `state.md` |
| new `records migrate` command | atomic conversion with dry run, verified path mapping, preserved decisions and explicit blockers |
| schemas | `harness.project/v2`, `harness.state/v2` constants; record schemas unchanged |
| tests | every kind round-trips through `.md`; mixed-format tree; duplicate-format error; format-only migration preserves approval; changed scope is not silently authorized; failed migration preserves original records |

## What does not change

- The body of any record is non-authoritative, as it is for PLAN and TASK
  today.
- Which records exist, what they mean, and how they link is the data model in
  `docs/DATA_MODEL.md`; only the file format moves.
- The approval model, the five cryptographic boundaries, and the PLAN gate are
  untouched.
