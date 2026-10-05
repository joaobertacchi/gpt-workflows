# Restore Follow-Up Date Design

## Problem

Version `0.5.1` requires a deadline for every action-based next step, but it no longer records when the overall follow-up will occur. The follow-up date existed as a required report field before version `0.5.0` and was removed when `Natureza da Visita` was added.

Action deadlines and the report follow-up date have different meanings:

- `Prazo` is the completion deadline for one next-step action.
- `Data para follow up` is the date when the visit outcome or pending actions will be reviewed.

## Goals

- Restore `Data para follow up` as a required report field.
- Keep `Natureza da Visita` and every current required field.
- Accept an absolute date or the explicit value `Não haverá follow up`.
- Confirm relative follow-up dates before report generation.
- Render the follow-up date in the report header.
- Keep every existing next-step deadline rule unchanged.

## Non-Goals

- Deriving the follow-up date from a next-step deadline.
- Making follow up conditional on the existence of next steps.
- Adding follow-up ownership, purpose, reminders, storage, or integrations.
- Changing the allowed visit natures or visit types.

## Data Model

The schema contains twelve required fields plus optional `provided_details`. Add this field after `next_steps` and before `elaborado_por`:

```json
{"id":"follow_up_date","label":"Data para follow up","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não haverá follow up","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}}
```

Restore these explicit negative answers for `follow_up_date`:

```json
["não haverá follow up","não será feito follow up","sem follow up"]
```

An absent, invalid, conflicting, or unconfirmed follow-up date leaves only `follow_up_date` unresolved when all other fields are complete. The existing explicit override can still generate a draft with `Não informado` and list `Data para follow up` under `Pendências de informação`.

## Intake And Workflow

The intake adds `data para follow up` after next steps and before `elaborado por`. Its relative-date guidance covers the visit date, next-step deadlines, and follow-up date.

Validation follows the existing absolute-date path used by `meeting_date`. A relative follow-up date is resolved from the conversation date, shown as a calendar date, and held for confirmation or correction. The skill must not infer it from an action deadline or any unrelated date.

The report generates automatically only after `follow_up_date` contains either:

- a valid absolute date; or
- the explicit value `Não haverá follow up`.

## Report Format

Render the restored field in the header after `Responsável técnico` and before `Participantes`:

```markdown
**Responsável técnico:** {{responsavel_tecnico}}  
**Data para follow up:** {{follow_up_date}}
```

The `Próximos Passos` table remains unchanged with `Ação`, `Responsável`, and `Prazo` columns.

## Implementation Scope

- `skills/relatorio-reuniao/SKILL.md`: restore the intake item, schema field, explicit negatives, workflow rules, missing-field example, and report placeholder.
- `scripts/test_flow.py`: render the field and replace assertions that currently require its absence with assertions for the restored contract.
- `tests/scenarios.json`: add the field to complete records and cover missing, explicit-none, relative-date confirmation, correction, and override behavior.
- `README.md` and `INSTRUCOES_DE_USO.md`: document twelve required fields and update examples.
- `docs/public-submission.md` and `tests/chatgpt-acceptance.md`: update release and acceptance cases.
- `plugin.json` and `.codex-plugin/plugin.json`: release the behavior as version `0.6.0`.
- `dist/documentar-reuniao-0.6.0.zip`: rebuild the public four-file archive.

## Test Strategy

The deterministic harness must verify:

1. A complete report renders `Data para follow up` with an absolute date.
2. A missing follow-up date blocks generation and requests only that field when nothing else is unresolved.
3. `Não haverá follow up` completes only `follow_up_date`.
4. A relative follow-up date requires confirmation and then renders the confirmed calendar date.
5. An explicit override renders `Não informado` and lists `Data para follow up` as pending.
6. A correction replaces the prior follow-up value and regenerates the report.
7. Next-step deadlines remain independently required and are never reused as the follow-up date.
8. Intake, template, public documentation, manifests, and archive assertions match version `0.6.0`.

The ChatGPT Work acceptance procedure must cover the intake, a complete first-turn report, missing-field collection, relative-date confirmation, explicit no follow up, and report-only rendering.

## Success Criteria

- The skill exposes twelve required fields and retains `Natureza da Visita`.
- A report cannot complete without a valid follow-up date or `Não haverá follow up`, unless the user invokes the existing explicit override.
- The final report displays `Data para follow up` separately from next-step deadlines.
- The full deterministic suite, package build, archive checks, and manual acceptance procedure pass for version `0.6.0`.
