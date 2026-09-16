# Next-Step Deadlines Design

## Goal

Collect and render a deadline for every action-based next step, shown as a `Prazo` column in the report's next-steps table.

## Current Behavior

`next_steps` items require only `action` and `responsible`. The report renders them as a table with `Ação` and `Responsável` columns. Deadlines for individual actions are not captured; only the report-level `follow_up_date` exists.

## Field Contract

Add `deadline` as a third required item field of `next_steps`:

- `itemFields` becomes `["action", "responsible", "deadline"]` with `itemFieldTypes` adding `"deadline": "date"`.
- Deadline values are calendar dates. Relative deadline phrases (for example, "até sexta") require calendar-date confirmation exactly like existing date fields.
- A next step is complete only with all three fields. A step missing only its deadline asks only for that deadline.

## Generation Without Deadlines

The user may override generation while a step deadline is unresolved. In that case the affected table cell renders `Não informado`, consistent with all other unresolved fields. This differs from the item-level rule: `action` and `responsible` remain hard item requirements, while `deadline` may be explicitly waived by the generation override.

Explicit absence of all next steps continues to render `Nenhum próximo passo definido` with no table.

## Report Rendering

The next-steps table gains a third column:

```markdown
| Ação | Responsável | Prazo |
| --- | --- | --- |
| Enviar a proposta | Bruno | 18/09/2026 |
```

Steps rendered through the override waiver show `Não informado` in the `Prazo` cell. The template and harness rendering stay aligned.

## Versioning

Release as version `0.3.6` in both manifests. Version `0.3.5` is already submitted to the portal and must remain unchanged. Update release notes, README references, and the acceptance baseline. The packaging script derives the filename from root `plugin.json`, producing `dist/documentar-reuniao-0.3.6.zip`.

## Runtime Scope

The change remains instruction-only and skills-only:

- `skills/relatorio-reuniao/SKILL.md` updates the schema and rendering instructions;
- `scripts/test_flow.py` models per-item deadline collection and confirmation;
- no new package member is required; and
- the public ZIP allowlist remains unchanged.

## Validation

The offline harness must validate:

- complete items include action, responsible, and deadline;
- an item missing only its deadline asks only for that deadline;
- relative deadline phrases require calendar-date confirmation;
- overridden generation with an unresolved deadline renders `Não informado` in the `Prazo` cell;
- explicit next-steps absence still renders `Nenhum próximo passo definido`;
- all existing scenarios updated with `deadline` keep passing; and
- both manifests, README, and submission notes reference version `0.3.6`.

The harness cannot prove live model behavior. Final acceptance also requires a ChatGPT Work conversation confirming the three-column table renders correctly and that a deadline-less override shows `Não informado`.

## Acceptance

The improvement is ready when:

- all conversational scenarios, including new deadline cases, pass;
- the report table shows `Ação`, `Responsável`, and `Prazo` columns;
- ChatGPT Work renders the three-column table and the `Não informado` waiver cell;
- `dist/documentar-reuniao-0.3.6.zip` passes the existing integrity and allowlist checks.
