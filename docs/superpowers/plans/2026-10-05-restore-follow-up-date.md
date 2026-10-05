# Restore Follow-Up Date Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release version `0.6.0` with a required report-level follow-up date while retaining visit nature and independent per-action deadlines.

**Architecture:** `skills/relatorio-reuniao/SKILL.md` remains the runtime contract. The existing generic absolute-date validation and confirmation flow handles `follow_up_date`; only schema, rendering, fixtures, contract assertions, public documentation, and release metadata change. No new helper or dependency is needed.

**Tech Stack:** Markdown Agent Skill, embedded JSON, Python 3 standard library, JSON fixtures, Bash packaging.

**Spec:** `docs/superpowers/specs/2026-10-05-restore-follow-up-date-design.md`

---

## File Structure

| File | Responsibility | Change |
| --- | --- | --- |
| `skills/relatorio-reuniao/SKILL.md` | Runtime contract | Restore required follow-up field, validation, workflow, intake, and report output |
| `scripts/test_flow.py` | Deterministic state machine and package checks | Render follow up and assert the restored twelve-field contract |
| `tests/scenarios.json` | Extracted-fact fixtures | Restore follow-up values and regression scenarios |
| `README.md` | Public project documentation | Document twelve required fields and archive version |
| `INSTRUCOES_DE_USO.md` | User guide | Add follow-up guidance and examples |
| `docs/public-submission.md` | Marketplace review material | Update release notes and review cases |
| `tests/chatgpt-acceptance.md` | Manual acceptance procedure | Set the `0.6.0` baseline and follow-up cases |
| `plugin.json`, `.codex-plugin/plugin.json` | Plugin manifests | Set version `0.6.0` |
| `dist/documentar-reuniao-0.6.0.zip` | Ignored public artifact | Rebuild and verify the four-file archive |

---

### Task 1: Restore The Runtime Contract And Regression Coverage

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `tests/scenarios.json`
- Modify: `skills/relatorio-reuniao/SKILL.md`

- [ ] **Step 1: Replace removal assertions with failing restoration assertions**

In `check_packaging()` in `scripts/test_flow.py`, replace the assertions that require `follow_up_date` to be absent with this contract check:

```python
    required_fields = [
        field for field in FIELD_SCHEMA["fields"] if field.get("required")
    ]
    if len(required_fields) != 12:
        raise AssertionError("the report contract must expose twelve required fields")
    follow_up_field = next(
        (
            field
            for field in FIELD_SCHEMA["fields"]
            if field["id"] == "follow_up_date"
        ),
        None,
    )
    if follow_up_field != {
        "id": "follow_up_date",
        "label": "Data para follow up",
        "required": True,
        "type": "string",
        "allowExplicitNone": True,
        "explicitNoneValue": "Não haverá follow up",
        "validation": {
            "kind": "absolute_date",
            "formats": ["YYYY-MM-DD", "DD/MM/YYYY"],
        },
    }:
        raise AssertionError("follow_up_date must restore the required date contract")
    if validation_rules.get("explicitNegativeAnswers", {}).get(
        "follow_up_date"
    ) != [
        "não haverá follow up",
        "não será feito follow up",
        "sem follow up",
    ]:
        raise AssertionError("follow_up_date must restore its accepted negative phrases")
```

Remove the fixed scenario-count assertion:

```python
    if len(scenarios) != 41:
        raise AssertionError(f"expected 41 scenarios, found {len(scenarios)}")
```

The suite should validate behavior, not a brittle fixture count.

- [ ] **Step 2: Run the harness to verify the new contract assertion fails**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL in `check_packaging()` with `the report contract must expose twelve required fields`.

- [ ] **Step 3: Restore the field in the skill schema and validation rules**

In `skills/relatorio-reuniao/SKILL.md`:

1. Add `- data para follow up;` after the next-steps intake bullet.
2. Change every current statement of eleven required fields to twelve.
3. Insert this field after `next_steps` and before `elaborado_por`:

```json
{"id":"follow_up_date","label":"Data para follow up","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não haverá follow up","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}}
```

4. Restore `follow_up_date` in `explicitNegativeAnswers`:

```json
"follow_up_date":["não haverá follow up","não será feito follow up","sem follow up"]
```

Keep `valueAliases.visit_nature` and every current validation phrase unchanged.

- [ ] **Step 4: Restore the workflow semantics**

Update the workflow rules in `SKILL.md` so they state all of the following explicitly:

```markdown
2. Validate all twelve fields and every required nested item field after every turn. A list is not complete when any required property of any item is absent or invalid. Ask one concise question containing only missing, invalid, conflicting, or unconfirmed information.
```

```markdown
5. A direct statement that no follow up will occur becomes `Não haverá follow up`. Negative answers complete no field except the configured explicit-none values for next steps, follow up and technical representative.
```

```markdown
6. Resolve relative meeting, follow-up and next-step deadline dates from the conversation date. Show every interpreted calendar date and wait for confirmation or correction before complete report generation.
```

Extend the generation and override rules with these requirements:

```markdown
- Never derive `follow_up_date` from a next-step deadline or another date.
- Follow-up dates and next-step deadlines are independent and have no required chronological order.
- An explicit override may generate a draft while a follow-up date is absent, invalid, conflicting or unconfirmed, but the draft must render `Não informado`, never the unconfirmed inferred date, and list `Data para follow up` under `Pendências de informação`.
- The existing explicit override remains the only exception for an unresolved follow-up date or next-step deadline.
```

- [ ] **Step 5: Restore intake, missing-field example, and report output**

Use this relative-date intake sentence:

```markdown
Se você usar datas relativas, como “ontem” para a visita, “sexta que vem” para o prazo de uma ação ou “terça que vem” para o follow up, eu mostrarei as datas interpretadas para sua confirmação.
```

Add this missing-field bullet after `Próximos Passos`:

```markdown
- Data para follow up;
```

Add the restored template line after `Responsável técnico`, preserving the two-space Markdown hard break on the preceding line:

```markdown
**Responsável técnico:** {{responsavel_tecnico}}  
**Data para follow up:** {{follow_up_date}}
```

Add common-mistake guidance that the skill must not infer follow up from an action deadline and must not render an unconfirmed inferred date in an overridden draft.

- [ ] **Step 6: Restore deterministic rendering and package assertions**

In the `values` mapping in `render_report()` in `scripts/test_flow.py`, insert:

```python
        "follow_up_date": value_or_missing("follow_up_date"),
```

Place it after `responsavel_tecnico` to match the report template.

Update `required_skill_concepts`:

```python
        "only these twelve fields are required",
        "não haverá follow up",
        "never derive `follow_up_date`",
```

Add `"data para follow up"` to `required_intake_labels` and `"Data para follow up"` to `required_partial_content`.

Add `"{{follow_up_date}}"` to `required_placeholders` after `"{{responsavel_tecnico}}"`. Replace the assertion that forbids this placeholder with an order assertion covering:

```python
    required_template_content = (
        "**Cliente:**",
        "**Data:**",
        "**Natureza da Visita:**",
        "**Tipo de Visita:**",
        "**Responsável técnico:**",
        "**Data para follow up:**",
        "## Participantes",
        "## Próximos Passos",
    )
```

- [ ] **Step 7: Run the harness and verify only fixture migration failures remain**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: packaging checks pass. Scenario failures report missing `follow_up_date` in records that were previously complete.

- [ ] **Step 8: Restore follow-up values in existing fixtures**

In `tests/scenarios.json`, add a canonical extracted value to every record intended to be otherwise complete:

```json
"follow_up_date": "Não haverá follow up"
```

Place it after `next_steps` and before `elaborado_por`. Use a concrete date instead in scenarios that exercise a scheduled follow up. At minimum:

```json
"follow_up_date": "2026-09-11"
```

for `complete-on-first-turn`, whose action deadline is `2026-09-12`. This proves an earlier follow-up date remains valid because the fields have no chronological constraint. Use:

```json
"follow_up_date": "2026-09-18"
```

for the detailed scenario whose return occurs on `17/09/2026`, so action deadline and follow-up date remain visibly independent.

For intentionally incomplete records, add `follow_up_date` to the expected `missing` list in schema order after `next_steps` and before `elaborado_por`.

- [ ] **Step 9: Restore and add focused follow-up scenarios**

Adapt the existing cases rather than duplicating equivalent setup:

1. Rename `explicit-none-completes-next-steps` to `explicit-none-completes-next-steps-and-follow-up`. Use text `Não existem próximos passos e sem follow up.`, canonical extracted values for both fields, and assert both rendered values. The exact validation-rule assertion from Step 1 covers all three accepted phrases.
2. Rename `relative-meeting-date-requires-confirmation` to `relative-meeting-and-follow-up-dates-require-confirmation`. Add `follow_up_date: "2026-09-18"`, include both IDs in `inferredDates` and `confirmedDates`, and assert both labels and dates in the confirmation output.
3. Restore follow-up retraction in `ambiguous-conflict-asks-only-for-conflicting-field`: clear `follow_up_date`, resolve the company conflict, then supply `Não haverá follow up`; verify only the unresolved follow-up field remains after company resolution.
4. Keep `next-step-deadline-asks-only-for-deadline` with a valid `follow_up_date` to prove follow up does not satisfy a missing action deadline.
5. Keep `override-waives-next-step-deadline` with `follow_up_date: "Não haverá follow up"` to prove explicit no follow up does not waive the action deadline without override.

Append this focused missing-follow-up case using the same complete synthetic values as neighboring Acme fixtures:

```json
{
  "id": "action-deadline-does-not-satisfy-missing-follow-up",
  "invoked": true,
  "turns": [
    {
      "text": "A ação tem prazo, mas a data de follow up não foi informada.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-15",
        "visit_nature": "Comercial",
        "visit_type": "preventiva",
        "objetivo_visita": "Revisar o equipamento",
        "responsavel_comercial": "Bruna",
        "responsavel_tecnico": "Caio",
        "participantes": [
          {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
          {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
        ],
        "topics_discussed": ["Revisão"],
        "next_steps": [
          {"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}
        ],
        "elaborado_por": "Bruna"
      }
    }
  ],
  "expectations": [
    {
      "action": "ask_missing",
      "state": "WAITING_FOR_MISSING",
      "missing": ["follow_up_date"],
      "outputContains": ["Data para follow up"],
      "outputNotContains": ["Próximos Passos", "Prazo da ação", "Elaborado por"]
    }
  ]
}
```

Append an override case where the record contains an inferred `follow_up_date`, `inferredDates` contains `follow_up_date`, and the same turn affirmatively says `Continuar mesmo assim.`. Expect `DONE_WITH_GAPS`, `missing: ["follow_up_date"]`, output containing `Não informado`, `Data para follow up`, and `Pendências de informação`, and output not containing the inferred date.

The fixture text uses `sem follow up`, but its `fields.follow_up_date` contains the canonical extracted value `Não haverá follow up`. The harness does not parse natural language; the contract assertion verifies the complete accepted-phrase list.

- [ ] **Step 10: Validate JSON and run the full harness**

Run:

```bash
python3 -m json.tool tests/scenarios.json >/dev/null
python3 scripts/test_flow.py
```

Expected: valid JSON; every scenario prints `PASS`; final line reports all current scenarios passed without relying on a fixed count.

- [ ] **Step 11: Commit the runtime restoration**

```bash
git add skills/relatorio-reuniao/SKILL.md scripts/test_flow.py tests/scenarios.json
git commit -m "feat: restore required follow-up date"
```

---

### Task 2: Update Public Documentation And Release Metadata

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `README.md`
- Modify: `INSTRUCOES_DE_USO.md`
- Modify: `docs/public-submission.md`
- Modify: `tests/chatgpt-acceptance.md`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`

- [ ] **Step 1: Make release checks expect version `0.6.0`**

In `scripts/test_flow.py`, change:

```python
    expected_version = "0.6.0"
```

Require `Version 0.6.0`, `Version 0.6.0 delivers`, and `dist/documentar-reuniao-0.6.0.zip` in their current release checks.

Replace the public-document assertion that forbids follow-up language with:

```python
    for path, content in public_docs.items():
        if "Data para follow up" not in content:
            raise AssertionError(f"{path} must document the restored follow-up date")
```

- [ ] **Step 2: Run the harness to verify release checks fail**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL because the manifests and public documentation still identify version `0.5.1` and omit current follow-up guidance.

- [ ] **Step 3: Update README and usage instructions**

In `README.md`:

- add `data para follow up (ou a declaração de que não haverá);` after next steps;
- change the start-checklist count from eleven to twelve;
- state that accepted no-follow-up phrases render as `Não haverá follow up`;
- explain that follow up is independent from action deadlines;
- change the archive path to `dist/documentar-reuniao-0.6.0.zip`.

In `INSTRUCOES_DE_USO.md`:

- add the same follow-up collection item;
- add `O follow up será em 22/09/2026.` to the complete example;
- extend relative-date guidance to follow up;
- document `Não haverá follow up.` as the explicit absence response;
- include follow-up date in the report-content list.

- [ ] **Step 4: Update marketplace submission cases**

Use this release note in `docs/public-submission.md`:

```markdown
Version 0.6.0 restores `Data para follow up` as a required report field while retaining `Natureza da Visita` and the mandatory deadline for every action-based next step. The workflow accepts an absolute follow-up date or an explicit statement that no follow up will occur, confirms relative dates, and keeps follow-up dates independent from action deadlines.
```

Update cases as follows:

- P1 expects exactly twelve categories, including follow up.
- P2 adds `Follow up: 20/09/2026.` and expects it in the report.
- P3 includes `Data para follow up` among missing fields.
- P4 uses a relative follow-up date and an absolute action deadline, then expects confirmation of visit and follow-up dates.
- P5 adds `Follow up: 18/09/2026.`.
- N1 adds `Follow up: 20/09/2026.` so only visit type remains invalid.
- N2 and N3 remain behaviorally unchanged.

Keep exactly five positive and three negative marketplace cases.

- [ ] **Step 5: Update manual ChatGPT acceptance**

In `tests/chatgpt-acceptance.md`:

- set plugin version and procedure to `0.6.0`;
- record source verification as `43/43`, reflecting the existing 41 scenarios plus the two focused follow-up regressions from Task 1;
- expect twelve intake categories including follow up;
- add an absolute follow-up date to every otherwise complete prompt;
- make relative-date acceptance cover meeting and follow-up dates together;
- change `Explicit no next steps` to `Explicit no next steps and follow up`; run the case separately with `não haverá follow up`, `não será feito follow up`, and `sem follow up`, requiring `Não haverá follow up` in every rendered report;
- add an `Unconfirmed follow-up override` case that requires `Não informado` and a pending follow-up label, never the inferred date;
- retain the missing action-deadline acceptance case with a valid follow-up value.

- [ ] **Step 6: Update both manifests**

Set:

```json
"version": "0.6.0"
```

in `plugin.json` and `.codex-plugin/plugin.json`. Keep both long descriptions and all other manifest metadata unchanged.

- [ ] **Step 7: Run the full harness**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: every scenario passes; packaging checks accept version `0.6.0` and all updated public documentation.

- [ ] **Step 8: Verify the recorded source-verification total**

Confirm that the final line from Step 7 matches this line in `tests/chatgpt-acceptance.md`:

```markdown
- Source verification: passed (`python3 scripts/test_flow.py`, 43/43)
```

Then rerun:

```bash
python3 scripts/test_flow.py
```

Expected: `All 43 conversational flow scenarios passed.`

- [ ] **Step 9: Commit the release documentation and metadata**

```bash
git add README.md INSTRUCOES_DE_USO.md docs/public-submission.md tests/chatgpt-acceptance.md plugin.json .codex-plugin/plugin.json scripts/test_flow.py
git commit -m "chore: prepare follow-up date release"
```

---

### Task 3: Build And Verify The Public Artifact

**Files:**
- Create (ignored): `dist/documentar-reuniao-0.6.0.zip`

- [ ] **Step 1: Run the complete deterministic suite from a clean command**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: every scenario passes and the final line reports `All 43 conversational flow scenarios passed.`

- [ ] **Step 2: Build the public archive**

Run:

```bash
./scripts/build_public_zip.sh
```

Expected: the harness passes, archive integrity succeeds, and the final line is the absolute path ending in `dist/documentar-reuniao-0.6.0.zip`.

- [ ] **Step 3: Verify archive members and manifest version**

Run:

```bash
unzip -Z1 dist/documentar-reuniao-0.6.0.zip
unzip -p dist/documentar-reuniao-0.6.0.zip plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.6.0"; print("manifest ok")'
```

Expected archive members, in order:

```text
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

Expected final verification line: `manifest ok`.

- [ ] **Step 4: Verify the archived runtime contract**

Run:

```bash
unzip -p dist/documentar-reuniao-0.6.0.zip skills/relatorio-reuniao/SKILL.md | python3 -c 'import sys; t=sys.stdin.read(); assert "follow_up_date" in t; assert "Data para follow up" in t; assert "Não haverá follow up" in t; assert "Natureza da Visita" in t; assert "| Ação | Responsável | Prazo |" in t; print("contract ok")'
```

Expected: `contract ok`.

- [ ] **Step 5: Run final Git verification**

Run:

```bash
git status --short
git log --oneline -5
```

Expected: no tracked worktree changes; the ignored archive is not staged; the runtime and release commits are present.

---

## Verification Summary

- `SKILL.md` exposes twelve required fields and retains `Natureza da Visita`.
- `follow_up_date` accepts an absolute date or canonical `Não haverá follow up`.
- Relative follow-up dates require confirmation for complete reports.
- Overrides render unresolved follow up as `Não informado`, never as a confirmed inferred date.
- Follow-up dates and action deadlines remain independently required with no chronological constraint.
- The deterministic suite passes without enforcing a fixed fixture count.
- Both manifests and public documentation identify version `0.6.0`.
- `dist/documentar-reuniao-0.6.0.zip` contains only the four approved files.
