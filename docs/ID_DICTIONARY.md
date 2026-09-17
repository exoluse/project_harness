# Document ID Dictionary

Use a small project format table to choose document IDs. This dictionary
provides a starting example for a web/backend/database/AI service with user
and administrator interfaces. Select only the kinds the project needs.
The [Information model](DATA_MODEL.md#item-ids) owns identity, allocation,
paths, preservation and validation; the project overview records or links
the formats actually in use.

This is harness guidance, so this file needs no project ID. All example
IDs below illustrate syntax, not allocated items, decisions or test results.

## Starter format table

Each file uses `<ID>.md` or `<ID>-<slug>.md` under
[document paths](DATA_MODEL.md#document-paths); the optional descriptive slug
is not part of the ID. In this example, `NNN` is a three-digit serial starting
at `001`; a final `NN` is a child serial starting
at `01`. In a child format, `NNN` copies the referenced parent's serial.
Projects can retain or choose other widths under their recorded convention.

| Kind | Format | Meaning | Allocation scope |
|---|---|---|---|
| Requirement / 요구사항 | `REQ-NNN` | Intended outcome or constraint. | Project-wide `REQ`. |
| Feature / 기능 | `FEATURE-NNN` | Groups related requirements, screens, contracts and work through links. | Project-wide `FEATURE`. |
| Screen / 화면 | `SCR-{surface}-NNN` | Screen behavior and specification for a named surface. | Each complete prefix, such as `SCR-PC`. |
| API contract / API 계약 | `API-NNN` | API contract with method/path, data and behavior in its body. | Project-wide `API`. |
| Task / 작업 | `TASK-{work}-NNN` | Independently assigned or completed work. | Each complete prefix, such as `TASK-API`. |
| Open item / 미결사항 | `OI-NNN` | Unresolved question, problem or decision needing follow-up. | Project-wide `OI`. |
| Decision detail / 결정·해결 상세 | `OD-NNN-NN` | Separately managed decision or resolution detail for `OI-NNN`. | Child serial per owning OI. |
| Architecture decision / 아키텍처 결정 | `ADR-NNN` | Architecture choice, alternatives and rationale, with actual decision provenance. | Project-wide `ADR`. |
| Contract test / 계약 테스트 | `CT-API-NNN-NN` | Separately managed contract check for `API-NNN`. | CT child serial per API. |
| Backend test / 백엔드 테스트 | `BT-API-NNN-NN` | Separately managed backend check for `API-NNN`. | BT child serial per API, independent of CT. |

Supporting outputs may register flat formats such as `DOC-NNN` for an overview
or dictionary, `DES-NNN` for shared design, `PLAN-NNN` for a work plan,
`VER-NNN` for broader verification, `DEC-NNN` for a standalone decision,
`CHG-NNN` for a change, or `HANDOFF-NNN` for a handoff. These are optional kinds,
not a required set of stage documents. Add other kinds only when needed.

## Optional filename descriptions

| Filename example | Stable ID | Optional description |
|---|---|---|
| `API-024.md` | `API-024` | None. |
| `API-024-service-context.md` | `API-024` | `service-context` |
| `TASK-ADMIN-060-user-list.md` | `TASK-ADMIN-060` | `user-list` |
| `OD-012-01-access-policy.md` | `OD-012-01` | `access-policy` |

The optional description uses exactly two lowercase words joined by one
hyphen, as specified in [document paths](DATA_MODEL.md#document-paths).
The first two rows are alternative filenames, not two owning documents.
The same suffix option applies to other registered ID formats. For example,
if a project uses `API-{area}-NNNNN` and registers `USER` as an area,
`API-USER-00001-service-context.md` has ID `API-USER-00001`.
The suffix adds no new classification or sequence. Follow the Information
model's slug syntax, identity and rename/link rules.

## Classification values

Classification values are local to their format; they need not share a
universal axis, spelling or token length.

| Field | Starter values | Meaning |
|---|---|---|
| Screen `surface` | `PC`, `MOB`, `AD` | Desktop user screen, mobile user screen, administrator screen. |
| Task `work` | `PC`, `MOB`, `API`, `ADMIN`, `COMMON` | Desktop UI, mobile UI, backend, admin UI, shared work. |

In this example, responsive user screens use PC/MOB when independently
specified; administrative screens use AD and describe supported devices in
the body. Task classifications describe work scope, not a person's identity
or an assignment of authority. Record actual ownership separately.

Start with these values only where they fit. If database or AI work needs its
own task classification, register `DB` or `AI`, for example `TASK-DB-001.md`
or `TASK-AI-001.md`. A cross-component task may use COMMON and describe its
web/server/database/model scope in the body. Do not force a split by technology
or enumerate every possible service component in advance.

## Selecting and extending formats

1. Find the project's format table and the existing owning item. Reuse its ID
   when updating the same item.
2. Choose the kind by output purpose. Add a classification only if useful for
   that kind; record audience, technology and implementation paths in the body
   when they need no ID segment.
3. If a kind or classification is missing, register its meaning, exact format,
   allowed values, serial width/start and allocation scope before first use.
   Define a child format's parent mapping explicitly. Follow the Information
   model's extension rules; routine additions need no separate approval.
4. Allocate against existing definitions, retired IDs and shared reservations
   using [allocation reuse](DATA_MODEL.md#allocation-and-validation-reuse),
   then apply [document validation](DATA_MODEL.md#document-validation).

A few rows in the project overview are enough for a small project. Create a
separate project dictionary only when it needs independent management, give it
an ID under the project convention and link it from the overview. Keep each
definition in one owning location. Counts belong to the actual item inventory;
they are not format limits and need no duplicate tally in the dictionary.

## Parent links and evidence

| Example | Required interpretation in this starter convention |
|---|---|
| `OD-012-01.md` | Detail for `OI-012`; its body links that open item's owning definition. A short answer can remain in OI without creating OD. |
| `CT-API-024-01.md` | Contract test for `API-024`; its body links the contract and identifies the checked version. |
| `BT-API-024-01.md` | Backend test for `API-024`; this is independent of the CT counter. |
| `TASK-API-060.md` | Backend task; its actual parent plan and requirements are explicit body links, not derived from `060`. |

OI records follow the [open-item lifecycle](WORKFLOW.md#open-item-lifecycle).
OD or ADR documents retain actual decision sources, scope and outcomes; their
existence does not mean an issue is resolved or implementation is authorized.
An ADR can link an OI directly without an additional OD repeating the decision.
Test documents record criteria and actual execution status, evidence and limits;
a test ID never establishes PASS.

Requirements own their acceptance conditions. FEATURE links that owning content.
Keep supporting decisions, steps and tests in their owning item unless the
[item-boundary rules](DATA_MODEL.md#independent-items-and-supporting-detail)
require independent management. The formats do not require a file for every
test function, screen variant or lifecycle transition.

## Existing conventions and exceptions

Reuse established project formats and meanings. Earlier harness examples used
`API-00001` for a backend plan and `SCR-00001` for a screen plan; preserve those
IDs and meanings in projects already using them. This starter table uses API
for a contract and SCR for a screen specification. A different width does not
make reusing an established prefix for a different meaning safe; follow the
Information model's compatibility rules before introducing a new convention.

Existing three-part IDs also remain valid. Preserve their allocation history,
and do not bulk rename records to match this example. The
[ID scope](DATA_MODEL.md#id-scope) and
[required-name exceptions](DATA_MODEL.md#required-name-exceptions) still apply.
Titles belong in the body and overview under
[document paths](DATA_MODEL.md#document-paths).
