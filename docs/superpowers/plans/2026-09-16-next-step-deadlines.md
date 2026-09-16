# Next-Step Deadlines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collect and render a mandatory `Prazo` calendar date for every next-step action, with relative-date confirmation and an override waiver that renders `Não informado`.

**Architecture:** Extend `next_steps` items with a third `deadline` field typed `date`. The offline harness learns per-item date confirmation (`inferredNextStepDeadlines`/`confirmedNextStepDeadlines`) and renders a three-column table. Runtime instructions in SKILL.md describe collection, confirmation, and the waiver cell. Version bumps to `0.3.6`.

**Tech Stack:** Python 3 stdlib harness (`scripts/test_flow.py`), JSON fixtures (`tests/scenarios.json`), Markdown skill contract (`skills/relatorio-reuniao/SKILL.md`), POSIX packaging script.

**Spec:** `docs/superpowers/specs/2026-09-16-next-step-deadlines-design.md`

---

### Task 1: Offline deadline contract

Model deadline completeness, per-item date confirmation, and the three-column table in the harness, and update all fixture items. This is the red-green core of the feature.

**Files:**
- Modify: `tests/scenarios.json` (existing `next_steps` items + three new cases)
- Modify: `skills/relatorio-reuniao/SKILL.md` (FIELD_SCHEMA JSON only)
- Modify: `scripts/test_flow.py` (completeness, simulation, date confirmation, table rendering)

- [ ] **Step 1: Update fixture items with deadlines and add three failing scenarios**

In `tests/scenarios.json`:

1. Line 48 (`explicit-mention-treats-suffix-as-first-turn`): replace
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],`
   with
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-12"}],`
2. Line 69 (`complete-on-first-turn`): replace
   `"next_steps": [{"action": "Enviar proposta revisada", "responsible": "Bruno"}],`
   with
   `"next_steps": [{"action": "Enviar proposta revisada", "responsible": "Bruno", "deadline": "2026-09-12"}],`
3. Line 95 (`ask-only-for-missing-then-merge`): replace
   `"next_steps": [{"action": "Preparar demonstração", "responsible": "Carla"}],`
   with
   `"next_steps": [{"action": "Preparar demonstração", "responsible": "Carla", "deadline": "2026-09-17"}],`
4. Line 163 (`invalid-visit-type-asks-only-for-type`): replace
   `"next_steps": [{"action": "Enviar instruções", "responsible": "Eva"}],`
   with
   `"next_steps": [{"action": "Enviar instruções", "responsible": "Eva", "deadline": "2026-09-18"}],`
5. Line 188 (`missing-only-visit-type-asks-only-for-type`): replace
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],`
   with
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}],`
6. Lines 225-228 (`generic-meeting-schema-does-not-satisfy-report-contract`): replace
   ```json
   "next_steps": [
     {"action": "Elaborar o protótipo e disponibilizar o plugin", "responsible": "eu"},
     {"action": "Instalar, testar e dar o retorno", "responsible": "Luciano"}
   ]
   ```
   with
   ```json
   "next_steps": [
     {"action": "Elaborar o protótipo e disponibilizar o plugin", "responsible": "eu", "deadline": "2026-09-14"},
     {"action": "Instalar, testar e dar o retorno", "responsible": "Luciano", "deadline": "2026-09-16"}
   ]
   ```
7. Line 616 (`negative-answers-inside-collections-are-invalid`): replace
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Sem follow up"}],`
   with
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Sem follow up", "deadline": "2026-09-18"}],`
   (the invalid `responsible` stays the sole cause of failure, keeping test intent focused)
8. Line 712 (`artifact-unavailable-uses-markdown-fallback`): replace
   `"next_steps": [{"action": "Enviar a proposta", "responsible": "Bruno"}],`
   with
   `"next_steps": [{"action": "Enviar a proposta", "responsible": "Bruno", "deadline": "18/09/2026"}],`
9. `relative-dates-require-confirmation`: replace
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],`
   with
   `"next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-17"}],`
10. `rich-notes-preserve-all-relevant-details` (actions keep their verbatim deadline phrases so existing `outputContains` fragments stay valid): replace

```json
            "next_steps": [
              {"action": "Preparar e enviar a prova de conceito até o fim do dia", "responsible": "eu"},
              {"action": "Instalar, testar em dispositivos móveis e enviar retorno até 17/09/2026", "responsible": "Luciano"}
            ],
```

with

```json
            "next_steps": [
              {"action": "Preparar e enviar a prova de conceito até o fim do dia", "responsible": "eu", "deadline": "2026-09-13"},
              {"action": "Instalar, testar em dispositivos móveis e enviar retorno até 17/09/2026", "responsible": "Luciano", "deadline": "2026-09-17"}
            ],
```

11. Add three new cases at the end of `cases` (after `artifact-unavailable-uses-markdown-fallback`). Add a trailing comma after the closing `}` of `artifact-unavailable-uses-markdown-fallback` before inserting, keeping the final `]` and `}` intact):

```json
    {
      "id": "next-step-deadline-asks-only-for-deadline",
      "invoked": true,
      "turns": [
        {
          "text": "Bruno enviará a proposta, mas o prazo ainda não foi definido.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "contacts": ["Ana"],
            "visit_type": "preventiva",
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],
            "follow_up_date": "Não haverá follow up"
          }
        },
        {
          "text": "O prazo do passo é 18/09/2026.",
          "fields": {
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}]
          }
        }
      ],
      "expectations": [
        {
          "action": "ask_missing",
          "state": "WAITING_FOR_MISSING",
          "missing": ["next_steps"],
          "outputContains": ["Próximos passos"],
          "outputNotContains": ["Empresa (cliente)", "Data da reunião/visita", "Pessoa(s) de contato", "Tipo de reunião/visita", "Assuntos discutidos", "Data para follow up"]
        },
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "relative-next-step-deadline-requires-confirmation",
      "invoked": true,
      "turns": [
        {
          "text": "Bruno enviará a proposta até sexta que vem.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "contacts": ["Ana"],
            "visit_type": "preventiva",
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}],
            "follow_up_date": "Não haverá follow up"
          },
          "inferredNextStepDeadlines": [0]
        },
        {
          "text": "Confirmo o prazo.",
          "fields": {},
          "confirmedNextStepDeadlines": [0]
        }
      ],
      "expectations": [
        {
          "action": "confirm_dates",
          "state": "WAITING_FOR_CONFIRMATION",
          "missing": ["next_steps"],
          "outputContains": ["Próximos passos", "2026-09-18"]
        },
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "override-waives-next-step-deadline",
      "invoked": true,
      "turns": [
        {
          "text": "Continuar mesmo assim.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "contacts": ["Ana"],
            "visit_type": "preventiva",
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],
            "follow_up_date": "Não haverá follow up"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE_WITH_GAPS",
          "missing": ["next_steps"],
          "outputContains": ["| Ação | Responsável | Prazo |", "Não informado", "Pendências de informação"]
        }
      ]
    }
```

- [ ] **Step 2: Run harness to verify the new cases fail**

Run: `python3 scripts/test_flow.py`
Expected: FAIL exactly for `next-step-deadline-asks-only-for-deadline`, `relative-next-step-deadline-requires-confirmation`, and `override-waives-next-step-deadline`; all 31 existing cases still PASS.

- [ ] **Step 3: Extend FIELD_SCHEMA in SKILL.md**

In `skills/relatorio-reuniao/SKILL.md`, inside `<!-- FIELD_SCHEMA_START -->`, replace line 49:

```json
    {"id":"next_steps","label":"Próximos passos","required":true,"type":"array<object>","itemFields":["action","responsible"],"itemFieldTypes":{"action":"string","responsible":"string"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
```

with:

```json
    {"id":"next_steps","label":"Próximos passos","required":true,"type":"array<object>","itemFields":["action","responsible","deadline"],"itemFieldTypes":{"action":"string","responsible":"string","deadline":"date"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
```

and add `"itemDateFormats"` right after `"missingValue": "Não informado",` so the schema block begins:

```json
{
  "missingValue": "Não informado",
  "itemDateFormats":["YYYY-MM-DD","DD/MM/YYYY"],
  "fields": [
```

- [ ] **Step 4: Extend the harness**

In `scripts/test_flow.py`:

4a. Replace the `array<object>` branch of `field_is_complete` (lines 135-152) so per-item kinds dispatch:

```python
    if field_type == "array<object>":
        item_fields = field.get("itemFields", [])
        item_field_types = field.get("itemFieldTypes", {})
        return (
            isinstance(value, list)
            and bool(value)
            and bool(item_fields)
            and all(
                isinstance(item, dict)
                and all(
                    item_value_is_complete(
                        item_field, item.get(item_field), item_field_types
                    )
                    for item_field in item_fields
                )
                for item in value
            )
        )
```

and add the helper directly above `field_is_complete`:

```python
def item_value_is_complete(
    item_field: str, value: Any, item_field_types: dict[str, str]
) -> bool:
    kind = item_field_types.get(item_field)
    if kind == "string":
        return isinstance(value, str) and is_substantive(value, MISSING_SENTINELS)
    if kind == "date":
        return is_absolute_date(value, ITEM_DATE_FORMATS)
    return False
```

4b. Extend `missing_fields` so unconfirmed item dates block their field. Replace lines 156-168:

```python
def missing_fields(
    record: dict[str, Any], blocked_fields: set[str] | None = None
) -> list[str]:
    blocked_fields = blocked_fields or set()
    return [
        field["id"]
        for field in FIELD_SCHEMA["fields"]
        if field["required"]
        and (
            field["id"] in blocked_fields
            or not field_is_complete(field, record.get(field["id"]))
        )
    ]
```

No change needed to `missing_fields` itself — instead the caller unions the item-date fields (see 4d).

4c. Extend `render_date_confirmation` (lines 228-235):

```python
def render_date_confirmation(
    record: dict[str, Any],
    field_ids: set[str],
    item_dates: set[tuple[str, int]] | None = None,
) -> str:
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}
    entries = [
        f"{labels[field_id]}: {record[field_id]}"
        for field_id in FIELD_IDS
        if field_id in field_ids
    ]
    for field_id, item_index in sorted(
        item_dates or set(),
        key=lambda entry: (FIELD_IDS.index(entry[0]), entry[1]),
    ):
        deadline = record[field_id][item_index]["deadline"]
        entries.append(f"{labels[field_id]} #{item_index + 1}: {deadline}")
    return f"Confirme as datas interpretadas: {'; '.join(entries)}. Estão corretas?"
```

4d. Replace the next-steps rendering inside `render_report` (lines 271-279):

```python
    next_steps = value_or_missing("next_steps")
    if isinstance(next_steps, list):
        rows = ["| Ação | Responsável |", "| --- | --- |"]
        rows.extend(
            f"| {item['action']} | {item['responsible']} |" for item in next_steps
        )
        rendered_steps = "\n".join(rows)
    else:
        rendered_steps = next_steps or FIELD_SCHEMA["missingValue"]
```

with:

```python
    rendered_steps = render_next_steps(record)
```

and add these three functions above `render_report`:

```python
def next_step_cell(value: Any) -> str:
    if (
        isinstance(value, str)
        and is_substantive(value, MISSING_SENTINELS)
        and not contains_explicit_negative(value)
    ):
        return value
    return str(FIELD_SCHEMA["missingValue"])


def next_step_deadline_cell(item: dict[str, Any]) -> str:
    deadline = item.get("deadline")
    if is_absolute_date(deadline, ITEM_DATE_FORMATS):
        return deadline
    return str(FIELD_SCHEMA["missingValue"])


def render_next_steps(record: dict[str, Any]) -> str:
    next_steps = record.get("next_steps")
    if (
        isinstance(next_steps, list)
        and bool(next_steps)
        and all(isinstance(item, dict) for item in next_steps)
    ):
        rows = ["| Ação | Responsável | Prazo |", "| --- | --- | --- |"]
        rows.extend(
            f"| {next_step_cell(item.get('action'))} | "
            f"{next_step_cell(item.get('responsible'))} | "
            f"{next_step_deadline_cell(item)} |"
            for item in next_steps
        )
        return "\n".join(rows)
    if isinstance(next_steps, str):
        return next_steps
    return FIELD_SCHEMA["missingValue"]
```

4e. Track per-item unconfirmed dates in `simulate`. In `simulate` (lines 421-471), replace:

```python
    unconfirmed_dates: set[str] = set()
```

with:

```python
    unconfirmed_dates: set[str] = set()
    unconfirmed_item_dates: set[tuple[str, int]] = set()
```

replace (after `record = merge_record(record, incoming)`):

```python
        unconfirmed_dates.difference_update(turn.get("confirmedDates", []))
        conflicting_fields.difference_update(incoming)
        conflicting_fields.update(turn.get("conflictingFields", []))
        missing = missing_fields(record, unconfirmed_dates | conflicting_fields)
```

with:

```python
        unconfirmed_dates.difference_update(turn.get("confirmedDates", []))
        if "next_steps" in incoming:
            unconfirmed_item_dates = {
                entry for entry in unconfirmed_item_dates if entry[0] != "next_steps"
            }
            unconfirmed_item_dates.update(
                ("next_steps", index)
                for index in turn.get("inferredNextStepDeadlines", [])
            )
        confirmed_item_dates = set(turn.get("confirmedNextStepDeadlines", []))
        unconfirmed_item_dates = {
            entry
            for entry in unconfirmed_item_dates
            if entry[1] not in confirmed_item_dates
        }
        conflicting_fields.difference_update(incoming)
        conflicting_fields.update(turn.get("conflictingFields", []))
        missing = missing_fields(
            record,
            unconfirmed_dates
            | conflicting_fields
            | {field_id for field_id, _ in unconfirmed_item_dates},
        )
```

and replace the action selection:

```python
        elif unconfirmed_dates:
            action = "confirm_dates"
            state = "WAITING_FOR_CONFIRMATION"
```

with:

```python
        elif unconfirmed_dates or unconfirmed_item_dates:
            action = "confirm_dates"
            state = "WAITING_FOR_CONFIRMATION"
```

and replace:

```python
        elif action == "confirm_dates":
            output = render_date_confirmation(record, unconfirmed_dates)
```

with:

```python
        elif action == "confirm_dates":
            output = render_date_confirmation(
                record, unconfirmed_dates, unconfirmed_item_dates
            )
```

4f. Register the item-date formats at module level. After `MISSING_SENTINELS = ...` (around line 839), add:

```python
ITEM_DATE_FORMATS = list(FIELD_SCHEMA.get("itemDateFormats", []))
```

- [ ] **Step 5: Run harness to verify all cases pass**

Run: `python3 scripts/test_flow.py`
Expected: `All 34 conversational flow scenarios passed.`

- [ ] **Step 6: Commit**

```bash
git add tests/scenarios.json skills/relatorio-reuniao/SKILL.md scripts/test_flow.py
git commit -m "test: model next-step deadline contract"
```

---

### Task 2: Runtime instructions and packaging checks

Teach the runtime prose (intake bullet, workflow, table instruction, waiver sentence, partial example) and make the packaging checks require it.

**Files:**
- Modify: `scripts/test_flow.py` (packaging phrase checks)
- Modify: `skills/relatorio-reuniao/SKILL.md` (intake, workflow, report output, partial example)
- Modify: `tests/scenarios.json` (intake expectations, two cases)

- [ ] **Step 1: Update packaging checks first (failing)**

In `scripts/test_flow.py`, in `check_packaging`:

1. In `required_intake_labels` (around line 753), replace
   `"responsável por cada ação",`
   with
   `"responsável e o prazo de cada ação",`
2. In `required_partial_content` (around line 771), replace
   `"Próximos passos, com responsável por cada ação",`
   with
   `"Próximos passos, com responsável e prazo de cada ação",`
3. In `required_skill_concepts` (around line 702), append three concepts after
   `"if the active surface cannot create or expose a markdown artifact",`:

```python
        "responsável e o prazo de cada ação",
        "`ação`, `responsável` and `prazo`",
        "`prazo` cell",
```

- [ ] **Step 2: Run harness to verify it fails**

Run: `python3 scripts/test_flow.py`
Expected: FAIL — `main()` calls `check_packaging()` first, so it raises the packaging assertion (missing intake label / skill concepts) with a traceback before scenarios execute. The two intake scenarios would also fail their `outputContains` phrase, observable after Steps 3-4 if run separately.

- [ ] **Step 3: Update SKILL.md runtime prose**

In `skills/relatorio-reuniao/SKILL.md`:

1. Intake bullet (line 26): replace
   `- próximos passos, com o responsável por cada ação;`
   with
   `- próximos passos, com o responsável e o prazo de cada ação;`
2. Workflow step 4 (line 71): replace
   `4. Require every next-step action to have a responsible person. A direct statement that no next steps exist becomes \`Nenhum próximo passo definido\`.`
   with
   `4. Require every next-step action to have a responsible person and a deadline date. A direct statement that no next steps exist becomes \`Nenhum próximo passo definido\`.`
3. Workflow step 6 (line 73): replace
   `6. Resolve relative meeting and follow-up dates from the conversation date. Show every calendar date and wait for confirmation or correction.`
   with
   `6. Resolve relative meeting, follow-up and next-step deadline dates from the conversation date. Show every calendar date and wait for confirmation or correction.`
4. Report Output paragraph (line 128): replace
   `Render this template in order. Render contacts as comma-separated names, topics as bullets, and action-based next steps as a table with \`Ação\` and \`Responsável\` columns.`
   with
   `Render this template in order. Render contacts as comma-separated names, topics as bullets, and action-based next steps as a table with \`Ação\`, \`Responsável\` and \`Prazo\` columns.`

   and append immediately after that paragraph:

   `If generation is overridden while a step deadline is unresolved, render \`Não informado\` in that \`Prazo\` cell.`
5. Partial example (line 120): replace
   `- Próximos passos, com responsável por cada ação;`
   with
   `- Próximos passos, com responsável e prazo de cada ação;`

- [ ] **Step 4: Update the two intake scenario expectations**

In `tests/scenarios.json`, in both `selected-plugin-starts-intake` (line 14) and `explicit-mention-start-command-starts-intake` (line 32), replace

```json
"responsável por cada ação"
```

with

```json
"responsável e o prazo de cada ação"
```

- [ ] **Step 5: Run harness to verify all cases pass**

Run: `python3 scripts/test_flow.py`
Expected: `All 34 conversational flow scenarios passed.`

- [ ] **Step 6: Commit**

```bash
git add skills/relatorio-reuniao/SKILL.md scripts/test_flow.py tests/scenarios.json
git commit -m "feat: require next-step deadlines in runtime contract"
```

---

### Task 3: Version 0.3.6 metadata

Bump both manifests, release notes, README, and the acceptance baseline. Packaging checks first (red), then metadata (green).

**Files:**
- Modify: `scripts/test_flow.py` (expected version + submission phrases)
- Modify: `plugin.json`, `.codex-plugin/plugin.json`
- Modify: `docs/public-submission.md`, `README.md`, `tests/chatgpt-acceptance.md`

- [ ] **Step 1: Update packaging expectations first (failing)**

In `scripts/test_flow.py` `check_packaging`:

1. Replace `expected_version = "0.3.5"` with `expected_version = "0.3.6"` (around line 565).
2. Replace `if "Version 0.3.5" not in submission:` block (around line 730):

```python
    if "Version 0.3.6" not in submission:
        raise AssertionError("submission release notes must name version 0.3.6")
```

3. Replace the README check (around line 732):

```python
    if "dist/documentar-reuniao-0.3.6.zip" not in readme:
        raise AssertionError("README must name the current public archive")
```

4. In `required_submission_content` (around line 744), replace
   `"Version 0.3.5 delivers meeting reports",`
   with
   `"Version 0.3.6 adds next-step deadlines",`

- [ ] **Step 2: Run harness to verify it fails**

Run: `python3 scripts/test_flow.py`
Expected: FAIL — `check_packaging` raises the version assertion before scenarios execute; all 34 conversational cases are unaffected.

- [ ] **Step 3: Bump manifests and documents**

1. `plugin.json` and `.codex-plugin/plugin.json`: replace `"version": "0.3.5"` with `"version": "0.3.6"` in both.
2. `docs/public-submission.md`, Release Notes section: replace the paragraph beginning `Version 0.3.5 delivers meeting reports...` with:

```markdown
Version 0.3.6 adds next-step deadlines: every action-based next step requires a calendar-date `Prazo`, relative deadline phrases are confirmed as calendar dates, and an explicit override renders `Não informado` in the unresolved `Prazo` cell. Reports continue to deliver as rendered Markdown file artifacts with a fenced Markdown fallback.
```

3. `README.md`: replace every occurrence of `documentar-reuniao-0.3.5.zip` with `documentar-reuniao-0.3.6.zip`, and after the paragraph ending `...o bloco Markdown bruto é usado somente como fallback.` append:

```markdown
A tabela de próximos passos inclui a coluna `Prazo` com a data de cada ação; passos gerados por override sem prazo exibem `Não informado`.
```

4. `tests/chatgpt-acceptance.md`:
   - Build section: `- Plugin version: 0.3.5` → `- Plugin version: 0.3.6`
   - Build section: `passed (\`python3 scripts/test_flow.py\`, 31/31)` → `passed (\`python3 scripts/test_flow.py\`, 34/34)`
   - Build section: `- Installed-cache verification: pending for 0.3.5` → `pending for 0.3.6`
   - Build section: `- Auxiliary Codex loading: pending for 0.3.5` → `pending for 0.3.6`
   - Local ChatGPT Scenarios table: update the `Rendered Markdown artifact` row's status cell from `Pending on 0.3.5` to `Pending on 0.3.6`, and add a new row after it:

```markdown
| Next-step deadline column | Pending on 0.3.6 | Verify the report table renders `Ação`, `Responsável` and `Prazo` columns; a relative deadline asks for calendar-date confirmation; an override with unresolved deadline shows `Não informado` in the `Prazo` cell. |
```

   - Procedure section: `after installing version \`0.3.5\`` → `after installing version \`0.3.6\``
   - In the report-scenario `Expected:` paragraph (around line 131), append before the final sentence: ` The next-steps table must include the \`Prazo\` column with a calendar date per action.`

- [ ] **Step 4: Run harness to verify everything passes**

Run: `python3 scripts/test_flow.py`
Expected: `All 34 conversational flow scenarios passed.` and no packaging assertion.

- [ ] **Step 5: Commit**

```bash
git add plugin.json .codex-plugin/plugin.json docs/public-submission.md README.md tests/chatgpt-acceptance.md scripts/test_flow.py
git commit -m "chore: prepare version 0.3.6"
```

---

### Task 4: Build and inspect the public ZIP

**Files:**
- Create (ignored): `dist/documentar-reuniao-0.3.6.zip`

- [ ] **Step 1: Build the archive**

Run: `./scripts/build_public_zip.sh`
Expected: 34 scenario PASS lines, `All 34 conversational flow scenarios passed.`, integrity check line `No errors detected in compressed data ...`, and final line `/Users/joaobertacchi/Documents/repos/gpt-workflows/dist/documentar-reuniao-0.3.6.zip`

- [ ] **Step 2: Inspect the archive**

Run:

```bash
unzip -Z1 "dist/documentar-reuniao-0.3.6.zip"
```

Expected exactly:

```
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

Run:

```bash
unzip -p "dist/documentar-reuniao-0.3.6.zip" plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.3.6"'
```

Expected: exit 0.

Run:

```bash
python3 -c 'import zipfile; archive = zipfile.ZipFile("dist/documentar-reuniao-0.3.6.zip"); skill = archive.read("skills/relatorio-reuniao/SKILL.md").decode(); assert "Prazo" in skill and "itemFields" in skill and "deadline" in skill'
```

Expected: exit 0.

- [ ] **Step 3: Final repository verification**

Run:

```bash
git diff --check && git status --short --branch && git log --oneline origin/main..HEAD
```

Expected: no whitespace errors; working tree clean except untracked `dist/` (ignored); `main` ahead of `origin/main` by this plan's commits.

---

### Task 5: Manual ChatGPT Work acceptance (user-executed)

Offline checks cannot prove live rendering. After this plan is merged and published:

1. Upload `dist/documentar-reuniao-0.3.6.zip` in the portal (Create plugin → Skills only).
2. In ChatGPT Work, select **Documentar Reunião** and generate a complete report.
3. Verify: the next-steps table renders `Ação`, `Responsável` and `Prazo`; a relative deadline triggers calendar-date confirmation; an override with an unresolved deadline shows `Não informado` in the `Prazo` cell.
4. Record evidence in `tests/chatgpt-acceptance.md` (rows `Next-step deadline column` and the still-pending `Rendered Markdown artifact`), then commit `test: record deadline acceptance` after user approval.
