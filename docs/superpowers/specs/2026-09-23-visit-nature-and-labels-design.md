# Visit Nature And Report Labels Design

## Problem

Version `0.4.0` still uses generic meeting/visit labels, requires a follow-up date, and has no structured distinction between the nature and type of a visit. The target report format uses shorter labels, does not record a follow-up date, and classifies each visit by both nature and type.

## Goals

- Rename the public labels for client, date, visit type, and next steps.
- Remove the follow-up date from intake, validation, rendering, overrides, fixtures, and documentation.
- Add required `Natureza da Visita` immediately before `Tipo de Visita`.
- Accept the canonical visit natures `Comercial`, `Técnica`, and `Técnica Comercial`.
- Accept the reversed alias `Comercial Técnica` and normalize it to `Técnica Comercial`.
- Keep the required-field count at eleven by replacing follow up with visit nature.

## Non-Goals

- Changing the allowed values for `Tipo de Visita`.
- Changing participant, description, next-step deadline, override, or detail-fidelity behavior.
- Adding storage, integrations, APIs, or persistence.
- Preserving a hidden or optional follow-up field.

## Data Model

The schema continues to contain eleven required fields plus optional `provided_details`, in this order:

1. `company` — label `Cliente`, string, required.
2. `meeting_date` — label `Data`, absolute date, required.
3. `visit_nature` — label `Natureza da Visita`, enum, required.
4. `visit_type` — label `Tipo de Visita`, enum, required.
5. `objetivo_visita` — label `Objetivo da visita`, string, required.
6. `responsavel_comercial` — label `Responsável comercial`, string, required.
7. `responsavel_tecnico` — label `Responsável técnico`, string, required, retaining its explicit-none value.
8. `participantes` — label `Participantes`, required, unchanged.
9. `topics_discussed` — label `Assuntos discutidos`, required, unchanged.
10. `provided_details` — optional, unchanged.
11. `next_steps` — label `Próximos Passos`, required, unchanged.
12. `elaborado_por` — label `Elaborado por`, string, required.

`follow_up_date` is removed completely. No compatibility field remains in the schema or active record.

## Visit-Nature Normalization

The canonical values are:

| Normalized input | Stored and rendered value |
| --- | --- |
| `comercial` | `Comercial` |
| `tecnica` | `Técnica` |
| `tecnica comercial` | `Técnica Comercial` |
| `comercial tecnica` | `Técnica Comercial` |

Comparison is case-insensitive and accent-insensitive, following the harness's existing `normalize` behavior. The schema exposes only the three canonical values. `VALIDATION_RULES` gains a value-alias map for `visit_nature`; extraction and deterministic rendering canonicalize aliases before storing or rendering them. An unsupported value leaves only `Natureza da Visita` unresolved when every other field is complete.

## Intake

The intake lists these eleven collection items:

- cliente;
- data;
- natureza da visita: comercial, técnica ou técnica comercial;
- tipo de visita: corretiva, preventiva, desenvolvimento ou negociação;
- objetivo da visita;
- responsável comercial;
- responsável técnico, or an explicit statement that none existed;
- participantes, with side and role;
- assuntos discutidos;
- próximos passos, with responsible person and deadline;
- elaborado por.

The intake contains no mention of follow up.

## Report Format

The entire response remains exactly the Markdown report, with no code fences or surrounding guidance:

```markdown
# Relatório de Visita

**Cliente:** {{company}}  
**Data:** {{meeting_date}}  
**Natureza da Visita:** {{visit_nature}}  
**Tipo de Visita:** {{visit_type}}  
**Objetivo da visita:** {{objetivo_visita}}  
**Responsável comercial:** {{responsavel_comercial}}  
**Responsável técnico:** {{responsavel_tecnico}}

## Participantes

{{participantes}}

## Descrição

{{descricao_section}}

## Próximos Passos

{{next_steps}}

**Elaborado por:** {{elaborado_por}}
```

The exact public label changes are:

- `Empresa (cliente)` becomes `Cliente`;
- `Data da reunião/visita` becomes `Data`;
- `Tipo de reunião/visita` becomes `Tipo de Visita`;
- `Próximos passos` becomes `Próximos Passos`;
- `Data para follow up` is removed.

## Validation And Workflow

- Validation continues to ask only for unresolved labels in schema order.
- `visit_nature` accepts canonical values or the reversed alias and stores the canonical value.
- Relative-date confirmation continues for `meeting_date` and next-step deadlines only.
- `VALIDATION_RULES.explicitNegativeAnswers` removes `follow_up_date` and retains the remaining configured fields.
- Overrides no longer render or list follow up as pending.
- Corrections to visit nature replace the prior value after canonicalization.
- Every existing rule for visit type, participants, description fidelity, next steps, technical-representative explicit none, and report-only delivery remains unchanged.

## Test Strategy

### Deterministic Harness

Migrate all 39 existing fixtures:

- remove `follow_up_date` values and missing-field expectations;
- add canonical `visit_nature` values to complete records;
- update field labels and section-heading assertions;
- update relative-date scenarios to cover only `Data` and next-step deadlines;
- adapt explicit-none scenarios to test next steps without follow up;
- replace unrelated-field negative-answer fixtures that depended on `Não haverá follow up` with a remaining configured negative answer.

Add two scenarios:

1. `commercial-technical-alias-normalizes-to-canonical` supplies `comercial técnica` and requires `**Natureza da Visita:** Técnica Comercial` in the rendered report.
2. `invalid-visit-nature-asks-only-for-nature` supplies an unsupported nature with every other field complete and requires a prompt containing only `Natureza da Visita`.

The expected deterministic total is 41 passing scenarios.

### ChatGPT Work Acceptance

- `começar` lists the revised eleven collection categories with no follow-up field.
- Complete first-turn prompts include a visit nature and omit follow up.
- The reversed phrase `comercial técnica` renders as `Técnica Comercial`.
- An invalid nature prompts only for `Natureza da Visita` when all other fields are complete.
- Existing detailed-description, participant, date, override, and report-only checks remain in force.

## Release Scope

Release as version `0.5.0`. Update `SKILL.md`, the deterministic harness, all fixtures, acceptance documentation, README, usage instructions, public-submission material, and both manifests. Regenerate `dist/documentar-reuniao-0.5.0.zip`, run the complete test suite, verify the four-member archive, and run the confidential history sweep before pushing.
