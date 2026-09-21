# Required Fields And Unified Description Design

## Problem

Version `0.3.8` collects seven required fields and renders `Assuntos discutidos` separately from `Registro detalhado`. Real commercial visit reports observed in production additionally record company-side ownership and attribution data the plugin never captures: the commercial representative, the technical representative, the visit objective, every participant with their side and role, and the author of the report. The plugin also splits topics and supporting facts into two sections, duplicating content and encouraging topic bullets without their supporting context.

## Goals

- Add five required fields that mirror real visit reports: commercial representative, technical representative, visit objective, participants with side and role, and report author.
- Replace the separate `Pessoa(s) de contato` field with the richer `Participantes` field.
- Render one unified `Descrição` section grouped by discussed topic, replacing the `Assuntos discutidos` and `Registro detalhado` sections.
- Rename the report heading to `Relatório de Visita`.
- Keep every existing behavior for dates, overrides, corrections, detail-fidelity rewriting, and the copy boundary.

## Non-Goals

- Changing the relative-date, override, correction, or missing-field workflow mechanics.
- Adding tools, storage, transcription, APIs, or external integrations.
- Renaming the skill, the plugin, or the installed product name.
- Rendering the meeting date inside the report heading.
- Deduplicating participants against the commercial or technical representatives.

## Data Model

The schema grows from seven to twelve fields. `contacts` is removed without backward compatibility. Schema order defines missing-field prompt order:

1. `company` — string, required, unchanged.
2. `meeting_date` — string, required, unchanged.
3. `visit_type` — enum `corretiva|preventiva|desenvolvimento|negociação`, required, unchanged.
4. `objetivo_visita` — string, required, no explicit none: the objective exists by definition of the visit.
5. `responsavel_comercial` — string, required, no explicit none; always a member of the registering company.
6. `responsavel_tecnico` — string, required, `allowExplicitNone` with `explicitNoneValue` `Não houve responsável técnico`; purely commercial visits have none.
7. `participantes` — array of objects, required, replaces `contacts`; every item requires `nome` (string), `lado` (enum `cliente|empresa`), and `funcao` (string). `funcao` accepts the explicit value `função não informada` when the role is unknown; `nome` and `lado` have no escape. There is no whole-field explicit none: a visit always has at least the reporter.
8. `topics_discussed` — array of strings, required, unchanged.
9. `provided_details` — array of strings, optional, unchanged; never requested.
10. `next_steps` — array of objects with `action`, `responsible`, `deadline`, required, unchanged.
11. `follow_up_date` — string, required, unchanged, including `Não haverá follow up`.
12. `elaborado_por` — string, required, no explicit none; the reporter is known to themselves.

The commercial and technical representatives may also appear as participants with `lado` `empresa`; the model records only what the user supplies, with no automatic deduplication.

The reporter's own first-person actions keep first person in the detailed record.

## Validation Rules

- After every turn, validate all eleven required fields (twelve minus the optional `provided_details`).
- Missing-field prompts enumerate only unresolved labels, as today. A participant item missing `nome`, `lado`, or `funcao` leaves the whole `Participantes` field unresolved, prompting one question for that field.
- New explicit phrases: a direct statement that there was no technical representative completes only that field as `Não houve responsável técnico`; the value `função não informada` completes only the `funcao` of the referenced participant.
- Supplied details without any topic do not satisfy `topics_discussed`; topics are requested as today.
- A participant correction replaces the affected item while preserving unrelated items; field corrections follow the existing replacement rule.
- The new fields carry no dates, so relative-date confirmation applies only to `meeting_date`, next-step deadlines, and `follow_up_date` as today.
- An overridden report renders all twelve fields with `Não informado` in unresolved labels, explicit-none values where stated, and the existing `Pendências de informação` section.

## Intake

The intake lists eleven collection items: empresa, data, tipo, objetivo da visita, responsável comercial, responsável técnico, participantes (com lado e função), assuntos discutidos, próximos passos com responsável e prazo, data para follow up, e elaborado por. The intake continues to state that extra narrated facts are welcome but details are never requested.

## Report Format

The entire message must be exactly the report, beginning with `# Relatório de Visita`, rendered as Markdown without code fences, as today.

```markdown
# Relatório de Visita

**Empresa (cliente):** {{company}}  
**Data da reunião/visita:** {{meeting_date}}  
**Tipo de reunião/visita:** {{visit_type}}  
**Objetivo da visita:** {{objetivo_visita}}  
**Responsável comercial:** {{responsavel_comercial}}  
**Responsável técnico:** {{responsavel_tecnico}}  
**Data para follow up:** {{follow_up_date}}

## Participantes

- {{nome}} — {{Lado}} — {{funcao}}

## Descrição

{{descricao_section}}

## Próximos passos

{{next_steps_table}}

**Elaborado por:** {{elaborado_por}}
```

Rendering rules:

- `Participantes` renders as one line per participant: `Nome — Lado — Função`, with `Lado` capitalized as `Cliente` or `Empresa`; the escape renders as `(função não informada)`.
- `Descrição` replaces both former sections. Each supplied topic renders as a bold topic label followed by professional prose containing its supporting facts, applying the rewriting rules from the detail-fidelity contract. A topic without details renders as the bold label alone. Supplied facts that fit no informed topic render in a final unlabeled paragraph. The detailed record never reproduces dictated sentences near-verbatim.
- `Próximos passos` keeps the existing table with `Ação`, `Responsável`, and `Prazo`, including the `Não informado` deadline cell for overridden steps.
- `Elaborado por` closes the report as a signature line after the next-steps table.
- An overridden report appends `Pendências de informação` after the signature line.

## Behavioral Flow

The nine existing workflow steps remain, with these adjustments:

1. Step 1 extracts the five new fields and participant items in addition to the existing facts.
2. Step 2 validates the eleven required fields and asks only for unresolved labels.
3. The explicit-none handling covers `responsavel_tecnico` and per-item `funcao` in addition to the existing `next_steps` and `follow_up_date` cases.
4. Generation, override, correction, and date-confirmation steps keep their current contracts.

## Test Strategy

### Deterministic Harness

- Update `render_report` to render the extended header, the participant list, the unified `Descrição` grouped by topic with a trailing unlabeled paragraph when needed, the signature line, and the new heading.
- Migrate every fixture that uses `contacts` to the `participantes` structure; update `outputContains` assertions from `Pessoa(s) de contato` to the new labels.
- Add scenarios verifying: (a) `responsavel_tecnico` explicit none renders `Não houve responsável técnico`; (b) a participant with `função não informada`; (c) `Descrição` groups facts by topic, including an unlabeled trailing paragraph; (d) the message begins with `# Relatório de Visita`; (e) the intake lists the eleven collection items; (f) participant items missing a required subfield prompt only for `Participantes`.
- Update the pinned expected version to `0.4.0`, the README archive name, and the submission release-note assertions.

### ChatGPT Work Acceptance

- Update the acceptance baseline to `0.4.0` and refresh the `Start checklist` expectation to the eleven collection items.
- Update `docs/public-submission.md`: long description, P2, P3, and P5 prompts supplying the new fields, and the release notes.
- P5 acceptance requires the unified `Descrição` in professional prose grouped by topic; near-verbatim dictation echo records `Failed`.

## Release Scope

Release as version `0.4.0` in both manifests. The implementation updates `SKILL.md`, the harness and fixtures, the acceptance record, README, INSTRUCOES_DE_USO, public-submission notes, both manifests, and the `agents/openai.yaml` field references where present. No runtime files, tools, or integrations are added. Regenerate `dist/documentar-reuniao-0.4.0.zip`; existing dist archives remain.
