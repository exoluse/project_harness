# CHG-00002

README guidance alignment after the document organization and ID policy change.

Baseline: `098da4b93d1601277f72cfd48a328270d598de86`; the working tree was clean
before this edit. This small documentation change keeps its scope and evidence
in one note, indexed in [current document work](../DATA_MODEL.md#current-document-work).
It follows the existing project ID convention; a namespace search found the
IDs allocated below unused. No existing IDs or historical records are migrated.

## DEC-00003

Source: after the assistant's README review identified the old flat example,
ambiguous task-number wording and dispersed guidance, the user requested in
this conversation: "README 파일 수정할거 있으면 수정해."
This authorizes README corrections and document checks. The scope is README,
this concise change note and its index entry; product/runtime changes are
excluded. Git delivery was outside this initial scope and is subsequently
authorized by [DEC-00004](#dec-00004). Inputs are ready, no ownership conflict was
found, and local document edits require no external permission.

## REQ-00007

Readers can apply the existing feature/work document and stable-ID policy from
README without interpreting its examples as a default single-file-per-type
layout or permission to renumber tasks. Acceptance: one coherent document
guidance section shows independent feature documents, a small-change exception,
autonomous document/item classification, stable IDs and resolvable item-link
syntax, with the existing preservation and authority boundaries retained.
Covered by [TASK-DOC-00004](#task-doc-00004); checked by [VER-00004](#ver-00004).

## TASK-DOC-00004

Under [DEC-00003](#dec-00003), satisfy [REQ-00007](#req-00007) by keeping a brief
introduction near the repository map and consolidating detail under the existing
README document heading. Replace the flat example with login/search units and
a small change, explain document/item identities and references, and replace
task-number-change wording with order/group/location changes while retaining IDs.
The existing section heading is preserved for incoming links. The main risk is
making an illustrative layout or prefix vocabulary appear mandatory; the text
explicitly leaves these choices to the agent and labels examples as examples.
Edits are implemented; verification is recorded in [VER-00004](#ver-00004).

## VER-00004

Subject: this README change and its note/index on the baseline above in the
Windows/PowerShell workspace. Method: review the diff against [REQ-00007](#req-00007)
and current policy, check Markdown/UTF-8/whitespace, resolve actual local links
and anchors, and scan IDs for unique definitions. Expected: consistent guidance,
preserved policy boundaries and no format, reference or identity errors.
Result: STATIC_VERIFIED. Diff review confirmed the requested corrections and
preserved scope/format exceptions. `git diff --check` passed. PowerShell checks
passed for all three changed/new Markdown files and 46 local file/anchor links,
including UTF-8, titles, whitespace and balanced fences. A scan of 22 project
Markdown files found 25 unique real ID definitions and a valid identity for
this new note. Fenced and inline syntax examples were excluded from actual
reference checks; the example's heading and link syntax were reviewed directly.
No rendered-browser or product test is claimed.

At initial completion, the README correction was in the local working tree. The
change note and index retain the decision and verification; no required work
remains in this documentation scope.

## DEC-00004

Source: after the completed README correction was reported, the user requested
in this conversation: "커밋 & 푸시하자." This authorizes committing and normally
pushing the three reviewed Markdown files for [CHG-00002](#chg-00002) to the
current branch's configured upstream, `origin/main`.

Preflight: only the known README, index and change-note edits are present.
`git fetch origin` succeeded; local `main` and `origin/main` both resolve to
the baseline above, with zero commits ahead or behind. The delivery uses the
existing repository author identity through command-scoped Git options, as in
the previous delivery. Sequence: check the documents and staged diff, commit,
normal push and compare the remote commit with local HEAD. The final conversation
response records the actual delivery receipt. No force push or history rewrite
is included.

The delivery-preparation document recheck passed for three Markdown files,
48 local file/anchor links and 26 unique real IDs across 22 project Markdown
files, including this decision. UTF-8, headings, fences, whitespace and
new-document identity checks passed; `git diff --check` also passed.
