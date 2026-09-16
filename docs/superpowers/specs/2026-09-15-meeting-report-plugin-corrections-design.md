# Meeting Report Plugin Corrections Design

## Goal

Deliver an installable, skills-only plugin that runs the meeting-report workflow in ChatGPT. The workflow must collect every required field, ask only for missing or invalid required information, and generate a structured report when the record is complete.

The package must remain modular and must not introduce an MCP server, backend, database, external API, CRM integration, credentials, or persistence.

The pre-submission target is ChatGPT with a local marketplace installation. Android testing is not a pre-submission acceptance criterion. The customer-facing Android test occurs only after the plugin is publicly listed in the ChatGPT marketplace and the customer can install it from that listing.

## Package Architecture

The meeting-report skill will be self-contained:

```text
skills/relatorio-reuniao/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- workflow.md
|   |-- field-schema.json
|   `-- validation-rules.json
`-- assets/
    |-- intake-message.md
    |-- meeting-report-template.md
    `-- report-delivery-guidance.md
```

Responsibilities:

- `SKILL.md` defines activation, resource-loading order, and orchestration.
- `references/workflow.md` defines conversation states and transitions.
- `references/field-schema.json` defines required fields, types, and allowed values.
- `references/validation-rules.json` defines completeness, explicit negative answers, date confirmation, and override behavior.
- `assets/intake-message.md` contains the initial checklist shown to the user.
- `assets/meeting-report-template.md` defines the report layout.
- `assets/report-delivery-guidance.md` distinguishes complete and incomplete delivery.
- `agents/openai.yaml` defines the displayed name, starter prompt, and implicit-invocation policy.
- Root-level `tests/` and `scripts/` validate the package but are not runtime skill resources.

Runtime resources will have one canonical copy inside the skill. Every resource path in `SKILL.md` will be relative to the skill root. The portable root manifest will continue discovering the skill through the standard `skills/` directory.

## Invocation

ChatGPT is the primary acceptance surface. The explicit ChatGPT path is selection of the real `@Documentar Reunião` skill mention from the composer. Plain text that resembles a mention is not sufficient evidence that the host attached the skill.

The supported activation paths are:

- explicit `@Documentar Reunião` selection in ChatGPT;
- a clear meeting-documentation request matched through implicit invocation;
- `$relatorio-reuniao` in Codex as a secondary development check.

`allow_implicit_invocation` remains enabled. Explicit and implicit activation enter the same state machine.

If activation has no meeting notes, or its payload is only `começar`, `iniciar`, or `start`, the first response is the complete intake checklist. If activation already includes notes, those notes are the first collection turn and the checklist is not repeated unnecessarily.

## Conversation Flow

1. Activation creates a new active meeting record.
2. Collection extracts only user-provided facts and merges them with facts from later turns.
3. Explicit corrections replace prior values.
4. Ambiguous conflicts produce one question about the conflicting field.
5. Validation identifies all missing, invalid, or unconfirmed required fields.
6. When required information is missing, the assistant asks only for those fields.
7. A subsequent answer is merged into the same active record and validation runs again.
8. A complete record generates the report immediately, without another permission question.
9. An incomplete record generates only after an explicit override and is visibly marked as incomplete.
10. A correction after generation reopens validation and regenerates the report without repeating intake.

The workflow must not infer business facts such as companies, contacts, topics, visit types, actions, or responsible people.

## Required Data

| Field | Valid value |
| --- | --- |
| Company | Substantive text explicitly provided by the user |
| Meeting or visit date | An absolute date, or a context-derived date confirmed by the user |
| Contacts | One or more explicitly provided people |
| Meeting or visit type | Exactly `corretiva`, `preventiva`, `desenvolvimento`, or `negociação` after configured normalization |
| Topics discussed | One or more explicitly provided topics |
| Next steps | One or more actions, each with a responsible person, or an explicit statement that no next steps exist |
| Follow-up date | An absolute date, a context-derived date confirmed by the user, or an explicit statement that no follow up will occur |

Negative answers are field-specific. They can complete only `next_steps` and `follow_up_date`. Generic negative answers cannot complete company, meeting date, contacts, visit type, or topics.

## Date Handling

Absolute dates supplied by the user are accepted without an inference step.

Relative dates such as `ontem` or `sexta que vem` are resolved from the current conversation date and available context. The assistant must present each resolved calendar date and ask the user to confirm it before report generation. An inferred date remains pending until the user confirms or corrects it.

When context allows more than one reasonable interpretation, the assistant presents the proposed interpretation rather than silently choosing. One confirmation turn may cover multiple inferred dates.

No external date service or API is required.

## Missing Information And Overrides

Validation runs after each collection turn. A missing-information prompt enumerates only required fields that are absent, invalid, incomplete, conflicting, or awaiting date confirmation.

For action-based next steps, every action requires a responsible person. An explicit statement that no next steps exist is a complete value and is rendered as `Nenhum próximo passo definido`.

An explicit statement that no follow up will occur is a complete value and is rendered as `Não haverá follow up`.

Overrides are accepted only for affirmative phrases configured in `validation-rules.json`. Substring matching must not turn negated text, such as `não quero continuar mesmo assim`, into an override. Without a valid override, an incomplete report is not generated.

## Report Output

The complete report contains, at minimum:

```markdown
# Relatório de reunião/visita

**Empresa (cliente):**
**Data da reunião/visita:**
**Pessoa(s) de contato:**
**Tipo de reunião/visita:**
**Data para follow up:**

## Assuntos discutidos

## Próximos passos
```

Action-based next steps use a table with `Ação` and `Responsável` columns. Explicit absence uses the configured negative text instead of an empty table.

The `Pendências de informação` section is conditional. It appears only in a report generated through an explicit override. A complete report has no pending section or missing-value placeholders. An overridden report is labeled as an incomplete draft and lists every unresolved required field.

## Testing Strategy

### Package Structure

Static checks verify that:

- every resource referenced by `SKILL.md` exists relative to the skill root;
- no runtime resource path escapes the skill root;
- runtime resources have no duplicate canonical copies at the plugin root;
- portable and compatibility manifests have consistent identity and version;
- all JSON and YAML files are valid;
- no MCP, backend, or external-integration configuration is present.

### Deterministic Contract

The offline harness validates states, field types, transitions, missing-field lists, and rendered output. It does not claim to test natural-language extraction or host routing.

Scenarios cover:

- complete intake checklist output;
- complete notes in the first turn;
- questions containing only missing fields;
- merging answers across turns;
- invalid visit type;
- action without a responsible person;
- explicit absence of next steps;
- explicit absence of follow up;
- relative-date inference awaiting confirmation;
- confirmation and correction of inferred dates;
- explicit override;
- negated override phrase;
- correction and regeneration after report generation.

Fixtures may provide already-extracted fields, but fixture text and field data must not contradict each other. Tests that exercise intake must compare the rendered intake content, not only an abstract `send_intake` action.

### Installed Plugin Integration

Install a new plugin version from the local marketplace, verify the installed cache against the source, and start a new conversation. The skill must load its resources directly from documented paths, without failed reads or fallback searches.

Codex `$relatorio-reuniao` testing is secondary evidence for package loading. It does not replace ChatGPT acceptance.

### ChatGPT Acceptance

Use the real skill selection from the ChatGPT `@` menu and start a new conversation for each isolation-sensitive scenario. At minimum:

1. Send `@Documentar Reunião começar` and verify that the first response immediately contains all seven required field categories.
2. Send an activation containing complete notes and verify immediate report generation.
3. Send partial notes and verify that only missing required information is requested.
4. Exercise relative meeting and follow-up dates and verify confirmation before generation.
5. Exercise explicit absence of next steps and follow up and verify successful report generation.
6. Exercise an explicit override and verify an incomplete report with all pending fields.

Record the installed version and retain a transcript or capture for each acceptance scenario. Restart ChatGPT after plugin installation or replacement and avoid reusing conversations that loaded an older skill version.

## Delivery Milestones

### Ready For Submission

The plugin is ready for public submission when:

- all package, contract, and installed-plugin checks pass;
- ChatGPT local-marketplace acceptance passes in a new conversation;
- the checklist appears immediately on start activation;
- missing information is requested without repeating completed fields;
- inferred dates require confirmation;
- complete reports contain every required field;
- incomplete reports require explicit override;
- public listing metadata and publisher requirements have been reviewed.

### Post-Publication Android Smoke Test

Local-marketplace validation is performed on a supported local ChatGPT authoring surface. No Android test is required or expected before submission. The definitive Android test occurs only after public marketplace publication and installation by the customer from that public listing.

The Android smoke test must verify `@Documentar Reunião começar`, one partial-information flow, and one complete report. Android failure after desktop acceptance is treated as a host-surface compatibility issue and investigated from the selected mention, installed version, and conversation transcript before changing workflow instructions.
