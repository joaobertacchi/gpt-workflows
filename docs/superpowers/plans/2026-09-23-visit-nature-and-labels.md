# Visit Nature And Report Labels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Release version `0.5.0` with shorter report labels, no follow-up field, and a required canonicalized `Natureza da Visita` immediately before `Tipo de Visita`.

**Architecture:** `SKILL.md` remains the single runtime contract. `scripts/test_flow.py` reads its embedded schema and validation rules, canonicalizes top-level enum inputs when turns merge into the active record, and renders the Markdown template. JSON fixtures model extracted facts; documentation and manifests mirror the same public contract.

**Tech Stack:** Markdown Agent Skill, embedded JSON, Python 3 standard library, JSON fixtures, Bash packaging.

**Spec:** `docs/superpowers/specs/2026-09-23-visit-nature-and-labels-design.md`

**Confidentiality:** Use only synthetic fixture data already present in the repository. Do not store production-report names, organizations, products, locations, or the confidential audit keyword list in any tracked file.

---

## File Structure

| File | Responsibility | Change |
| --- | --- | --- |
| `skills/relatorio-reuniao/SKILL.md` | Runtime contract | Labels, schema, nature aliases, workflow, intake, examples, template |
| `scripts/test_flow.py` | Deterministic state machine and renderer | Canonicalization, nature rendering, packaging assertions, follow-up removal |
| `tests/scenarios.json` | Extracted-fact fixtures | Add nature, remove follow up, add alias/invalid-nature cases |
| `README.md` | Public project documentation | Required fields and archive version |
| `INSTRUCOES_DE_USO.md` | User guide | Intake/report descriptions and examples |
| `docs/public-submission.md` | Marketplace review material | Release notes and P/N prompts |
| `tests/chatgpt-acceptance.md` | Manual acceptance procedure | Baseline 0.5.0 and revised scenarios |
| `plugin.json`, `.codex-plugin/plugin.json` | Plugin manifests | Version and long description |

---

### Task 1: Update the SKILL.md contract

**Files:**
- Modify: `skills/relatorio-reuniao/SKILL.md`

- [ ] **Step 1: Replace the intake list**

Keep the opening and closing intake paragraphs, but replace the bullets with:

```markdown
- cliente;
- data;
- natureza da visita: comercial, técnica ou técnica comercial;
- tipo de visita: corretiva, preventiva, desenvolvimento ou negociação;
- objetivo da visita;
- responsável comercial;
- responsável técnico, ou a declaração de que não houve;
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- assuntos discutidos;
- próximos passos, com o responsável e o prazo de cada ação;
- elaborado por.
```

Update the relative-date sentence to mention examples that still exist:

```markdown
Se você usar datas relativas, como “ontem” para a visita ou “sexta que vem” para o prazo de uma ação, eu mostrarei as datas interpretadas para sua confirmação.
```

- [ ] **Step 2: Replace the FIELD_SCHEMA block**

Keep the markers and JSON fence. Use this exact schema:

```json
{
  "missingValue": "Não informado",
  "itemDateFormats":["YYYY-MM-DD","DD/MM/YYYY"],
  "fields": [
    {"id":"company","label":"Cliente","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"meeting_date","label":"Data","required":true,"type":"string","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}},
    {"id":"visit_nature","label":"Natureza da Visita","required":true,"type":"string","allowedValues":["Comercial","Técnica","Técnica Comercial"],"validation":{"kind":"enum","caseInsensitive":true}},
    {"id":"visit_type","label":"Tipo de Visita","required":true,"type":"string","allowedValues":["corretiva","preventiva","desenvolvimento","negociação"],"validation":{"kind":"enum","caseInsensitive":true}},
    {"id":"objetivo_visita","label":"Objetivo da visita","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"responsavel_comercial","label":"Responsável comercial","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"responsavel_tecnico","label":"Responsável técnico","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não houve responsável técnico","validation":{"kind":"non_empty"}},
    {"id":"participantes","label":"Participantes","required":true,"type":"array<object>","itemFields":["nome","lado","funcao"],"itemFieldTypes":{"nome":"string","lado":"enum","funcao":"string"},"itemAllowedValues":{"lado":["cliente","empresa"]},"validation":{"kind":"non_empty_list"}},
    {"id":"topics_discussed","label":"Assuntos discutidos","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"provided_details","label":"Fatos fornecidos","required":false,"type":"array<object>","itemFields":["texto"],"itemOptionalFields":["topico"],"itemFieldTypes":{"topico":"string","texto":"string"}},
    {"id":"next_steps","label":"Próximos Passos","required":true,"type":"array<object>","itemFields":["action","responsible","deadline"],"itemFieldTypes":{"action":"string","responsible":"string","deadline":"date"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
    {"id":"elaborado_por","label":"Elaborado por","required":true,"type":"string","validation":{"kind":"non_empty"}}
  ]
}
```

- [ ] **Step 3: Replace the VALIDATION_RULES block**

Keep the markers and JSON fence. Remove `follow_up_date`, add `valueAliases`, and preserve every other configured phrase:

```json
{
  "missingSentinels":["não informado","nao informado","não sei","nao sei","desconhecido","unknown","n/a","não disponível","nao disponivel","omitido"],
  "explicitOverridePhrases":["continuar mesmo assim","continuar com pendências","continuar com pendencias","gerar mesmo com pendências","gerar mesmo com pendencias","pode gerar mesmo faltando","proceed anyway","continue anyway","generate anyway"],
  "explicitNegativeAnswers":{"next_steps":["não existem próximos passos","não há próximos passos","nenhum próximo passo"],"responsavel_tecnico":["não houve responsável técnico","não havia responsável técnico","sem responsável técnico"]},
  "valueAliases":{"visit_nature":{"comercial técnica":"Técnica Comercial"}}
}
```

- [ ] **Step 4: Update workflow rules 3, 5, and 6**

Replace rule 3 with:

```markdown
3. Accept `visit_nature` only as canonical `Comercial`, `Técnica`, or `Técnica Comercial`; accept `Comercial Técnica` as an alias and normalize it to `Técnica Comercial`. Accept `visit_type` only as `corretiva`, `preventiva`, `desenvolvimento`, or `negociação` after normalization.
```

Replace rules 5 and 6 with:

```markdown
5. Negative answers complete no field except the configured explicit-none values for next steps and technical representative.
6. Resolve relative meeting and next-step deadline dates from the conversation date. Show every interpreted calendar date and wait for confirmation or correction.
```

No workflow rule may mention follow up.

- [ ] **Step 5: Replace PARTIAL_EXAMPLE**

Use the same synthetic prompt and this required response:

```markdown
User:

`Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).`

Required response:

Para completar o relatório, informe:

- Natureza da Visita;
- Tipo de Visita;
- Objetivo da visita;
- Responsável comercial;
- Responsável técnico;
- Assuntos discutidos;
- Próximos Passos, com responsável e prazo de cada ação;
- Elaborado por.

Do not ask for generic notes. Do not request decisions. Do not repeat Cliente, Data, or Participantes because the user already supplied them.
```

- [ ] **Step 6: Replace REPORT_TEMPLATE**

Use exactly:

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

Update the Report Output prose so the table section is called `Próximos Passos`. Keep report-only, override, description, participant, and deadline rules unchanged.

- [ ] **Step 7: Check for removed contract text**

Run:

```bash
grep -n -E "follow_up_date|Data para follow up|Não haverá follow up|Empresa \(cliente\)|Data da reunião/visita|Tipo de reunião/visita|## Próximos passos" skills/relatorio-reuniao/SKILL.md
```

Expected: no output. `grep -n "follow up"` may still find the Common Mistake about external systems only if unrelated; no required field, workflow, intake, or template reference may remain.

- [ ] **Step 8: Run the harness and observe the expected transitional failure**

Run: `python3 scripts/test_flow.py 2>&1 | tail -5`

Expected: a packaging assertion fails because `scripts/test_flow.py` still requires old follow-up concepts/placeholders. JSON parsing must succeed; fix SKILL.md if the failure is invalid JSON or broken markers.

- [ ] **Step 9: Commit**

```bash
git add skills/relatorio-reuniao/SKILL.md
git commit -m "feat: add visit nature and remove follow-up contract"
```

---

### Task 2: Canonicalize nature and update the deterministic harness

**Files:**
- Modify: `scripts/test_flow.py`

- [ ] **Step 1: Add top-level enum canonicalization**

Insert after `normalize`:

```python
def canonicalize_field_value(field_id: str, value: Any) -> Any:
    if not isinstance(value, str):
        return value
    field = next(
        (
            candidate
            for candidate in FIELD_SCHEMA["fields"]
            if candidate["id"] == field_id
        ),
        None,
    )
    if field is None:
        return value
    canonical_values = {
        normalize(option): option for option in field.get("allowedValues", [])
    }
    aliases = VALIDATION_RULES.get("valueAliases", {}).get(field_id, {})
    canonical_values.update(
        {normalize(alias): canonical for alias, canonical in aliases.items()}
    )
    return canonical_values.get(normalize(value), value)
```

Change `merge_record` to canonicalize every incoming top-level field:

```python
def merge_record(record: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(record)
    for field_id, value in incoming.items():
        merged[field_id] = canonicalize_field_value(field_id, value)
    return merged
```

This also canonicalizes existing top-level enum values such as `Negociação` to their schema spelling without changing non-enum strings or collection items.

- [ ] **Step 2: Update report rendering**

In the `values` mapping inside `render_report`:

- insert `"visit_nature": value_or_missing("visit_nature")` immediately before `visit_type`;
- remove `"follow_up_date": value_or_missing("follow_up_date")`.

- [ ] **Step 3: Update validation metadata assertions**

Add `valueAliases` to `required_validation_keys`.

After loading `validation_rules`, assert the nature contract:

```python
    nature_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "visit_nature"
    )
    if nature_field.get("allowedValues") != [
        "Comercial",
        "Técnica",
        "Técnica Comercial",
    ]:
        raise AssertionError("visit_nature must expose the three canonical values")
    if validation_rules.get("valueAliases", {}).get("visit_nature") != {
        "comercial técnica": "Técnica Comercial"
    }:
        raise AssertionError("visit_nature must normalize the reversed alias")
    if any(field["id"] == "follow_up_date" for field in FIELD_SCHEMA["fields"]):
        raise AssertionError("follow_up_date must be removed from the schema")
```

- [ ] **Step 4: Update skill-concept assertions**

In `required_skill_concepts`:

- remove `não haverá follow up`;
- add `comercial técnica`, `técnica comercial`, and `natureza da visita`;
- keep every other concept unchanged.

- [ ] **Step 5: Replace intake assertions**

Use:

```python
    required_intake_labels = (
        "cliente",
        "data",
        "natureza da visita",
        "comercial, técnica ou técnica comercial",
        "tipo de visita",
        "corretiva, preventiva, desenvolvimento ou negociação",
        "objetivo da visita",
        "responsável comercial",
        "responsável técnico",
        "participantes",
        "assuntos discutidos",
        "responsável e o prazo de cada ação",
        "elaborado por",
    )
```

Also assert `"follow up" not in intake.casefold()`.

- [ ] **Step 6: Replace partial-example assertions**

Use:

```python
    required_partial_content = (
        "Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).",
        "Natureza da Visita",
        "Tipo de Visita",
        "Objetivo da visita",
        "Responsável comercial",
        "Responsável técnico",
        "Assuntos discutidos",
        "Próximos Passos, com responsável e prazo de cada ação",
        "Elaborado por",
        "Do not ask for generic notes",
        "Do not request decisions",
    )
```

Assert the extracted partial example contains neither `Data para follow up` nor `Tipo de reunião/visita`.

- [ ] **Step 7: Replace required template placeholders**

Use:

```python
    required_placeholders = (
        "{{company}}",
        "{{meeting_date}}",
        "{{visit_nature}}",
        "{{visit_type}}",
        "{{objetivo_visita}}",
        "{{responsavel_comercial}}",
        "{{responsavel_tecnico}}",
        "{{participantes}}",
        "{{descricao_section}}",
        "{{next_steps}}",
        "{{elaborado_por}}",
    )
```

Assert `{{follow_up_date}}` is absent. Assert the template contains the exact lines `**Cliente:**`, `**Data:**`, `**Natureza da Visita:**`, `**Tipo de Visita:**`, and `## Próximos Passos` in that order.

- [ ] **Step 8: Run the harness and verify only fixture failures remain**

Run: `python3 scripts/test_flow.py 2>&1 | tail -10`

Expected: packaging checks pass; scenario failures remain because fixtures still omit `visit_nature`, contain `follow_up_date`, and expect old labels. No `AssertionError` from `check_packaging` is allowed.

- [ ] **Step 9: Commit**

```bash
git add scripts/test_flow.py
git commit -m "feat: canonicalize visit nature in report harness"
```

---

### Task 3: Migrate fixtures and add nature scenarios

**Files:**
- Modify: `tests/scenarios.json`

- [ ] **Step 1: Apply the mechanical migration to all existing cases**

For every complete extracted record:

- add `"visit_nature": "Comercial"` immediately before `visit_type`;
- use `"Técnica"` instead in technical maintenance/failure cases when it improves fixture readability;
- remove every `follow_up_date` key;
- remove `follow_up_date` from every `missing`, `inferredDates`, and `confirmedDates` array;
- remove output assertions containing `Data para follow up` or `Não haverá follow up`;
- update label assertions: `Empresa (cliente)` → `Cliente`, `Data da reunião/visita` → `Data`, `Tipo de reunião/visita` → `Tipo de Visita`, and `Próximos passos` → `Próximos Passos`.

For records intentionally missing many fields, insert `visit_nature` in schema order immediately before `visit_type` in expected `missing` arrays. Do not add `visit_nature` to the incoming fields in those cases.

- [ ] **Step 2: Adapt follow-up-specific cases**

Apply these exact semantic changes:

| Old id | New id / behavior |
| --- | --- |
| `ambiguous-follow-up-is-not-override` | Rename to `ambiguous-request-is-not-override`; keep the ambiguous text and expect every missing field except `company`, with `visit_nature` before `visit_type` and no follow up. |
| `explicit-none-completes-next-steps-and-follow-up` | Rename to `explicit-none-completes-next-steps`; text becomes `Não existem próximos passos.`; assert only `Nenhum próximo passo definido` and no pending section. |
| `relative-dates-require-confirmation` | Rename to `relative-meeting-date-requires-confirmation`; infer and confirm only `meeting_date`; expect missing/confirmation only for `meeting_date`. |
| `ambiguous-conflict-asks-only-for-conflicting-field` | Replace the follow-up retraction with `objetivo_visita: "não informado"`; after clarifying `company`, ask only for `Objetivo da visita`, then supply a corrected objective and generate. |
| `negative-answer-does-not-complete-unrelated-field` | Use `company: "Nenhum próximo passo definido"` to prove a next-step negative cannot complete Cliente. |
| `negative-answers-inside-collections-are-invalid` | Use `Nenhum próximo passo` inside participant/topic/next-step values; expect the same three collection fields missing. |

Every existing relative next-step deadline case remains unchanged except for the added nature and removed follow-up field.

- [ ] **Step 3: Add the alias-normalization scenario**

Append this case before the closing `cases` bracket, using the same synthetic complete-record values as neighboring Acme scenarios:

```json
{
  "id": "commercial-technical-alias-normalizes-to-canonical",
  "invoked": true,
  "turns": [
    {
      "text": "A natureza foi comercial técnica.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-15",
        "visit_nature": "comercial técnica",
        "visit_type": "preventiva",
        "objetivo_visita": "Revisar o equipamento",
        "responsavel_comercial": "Bruna",
        "responsavel_tecnico": "Caio",
        "participantes": [
          {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
          {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
        ],
        "topics_discussed": ["Revisão"],
        "next_steps": "Nenhum próximo passo definido",
        "elaborado_por": "Bruna"
      }
    }
  ],
  "expectations": [
    {
      "action": "generate",
      "state": "DONE",
      "missing": [],
      "outputContains": ["**Natureza da Visita:** Técnica Comercial"],
      "outputNotContains": ["Comercial Técnica", "comercial técnica", "Pendências de informação"]
    }
  ]
}
```

- [ ] **Step 4: Add the invalid-nature scenario**

Append:

```json
{
  "id": "invalid-visit-nature-asks-only-for-nature",
  "invoked": true,
  "turns": [
    {
      "text": "A natureza extraída foi administrativa.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-15",
        "visit_nature": "administrativa",
        "visit_type": "preventiva",
        "objetivo_visita": "Revisar o equipamento",
        "responsavel_comercial": "Bruna",
        "responsavel_tecnico": "Caio",
        "participantes": [
          {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
          {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
        ],
        "topics_discussed": ["Revisão"],
        "next_steps": "Nenhum próximo passo definido",
        "elaborado_por": "Bruna"
      }
    }
  ],
  "expectations": [
    {
      "action": "ask_missing",
      "state": "WAITING_FOR_MISSING",
      "missing": ["visit_nature"],
      "outputContains": ["Natureza da Visita"],
      "outputNotContains": ["Cliente", "Data", "Tipo de Visita", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Participantes", "Assuntos discutidos", "Próximos Passos", "Elaborado por"]
    }
  ]
}
```

- [ ] **Step 5: Verify fixture shape before running**

Run:

```bash
python3 -m json.tool tests/scenarios.json >/dev/null
grep -c '^      "id":' tests/scenarios.json
grep -n -E 'follow_up_date|Data para follow up|Não haverá follow up|"contacts"' tests/scenarios.json
```

Expected: valid JSON; count `41`; grep produces no output.

- [ ] **Step 6: Run the harness**

Run: `python3 scripts/test_flow.py 2>&1 | tail -5`

Expected final line: `All 41 conversational flow scenarios passed.`

- [ ] **Step 7: Commit**

```bash
git add tests/scenarios.json
git commit -m "test: migrate fixtures to visit nature contract"
```

---

### Task 4: Update release documentation and metadata

**Files:**
- Modify: `README.md`
- Modify: `INSTRUCOES_DE_USO.md`
- Modify: `docs/public-submission.md`
- Modify: `tests/chatgpt-acceptance.md`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `scripts/test_flow.py`

- [ ] **Step 1: Update README.md**

In `Campos obrigatórios`:

- replace `empresa (cliente)` with `cliente`;
- replace `data da reunião ou visita` with `data`;
- insert `natureza da visita: Comercial, Técnica ou Técnica Comercial` immediately before `tipo de visita`;
- remove `data para follow up`;
- retain eleven required items total.

Remove the sentence that explains `Não haverá follow up`. Keep only the next-step explicit-none explanation. Change the archive name to `dist/documentar-reuniao-0.5.0.zip`.

- [ ] **Step 2: Update INSTRUCOES_DE_USO.md**

Revise the collection list to mirror the eleven intake items and remove follow up. Update the complete example to include `Natureza da visita: Comercial` and omit follow up. Replace the explicit-negative section with next steps only. Remove follow up from the report-content list.

- [ ] **Step 3: Update marketplace cases**

In `docs/public-submission.md`:

- release notes begin with `Version 0.5.0 delivers` and describe Natureza da Visita, shorter labels, and follow-up removal;
- P1 still expects eleven categories and explicitly says no follow-up category;
- P2 supplies `Natureza: Comercial`, contains every required field and a next-step deadline, and contains no follow up;
- P3 expects both `Natureza da Visita` and `Tipo de Visita` among the missing labels, with no follow up;
- P4 uses `ontem` for `Data` and `sexta que vem` for a next-step deadline, with all other required fields supplied;
- P5 supplies `Natureza: Técnica Comercial` and contains no follow up;
- N1 supplies a valid nature and every other required field, including a next-step deadline, so only invalid `Tipo de Visita` remains;
- N2/N3 stay behaviorally unchanged and contain no follow-up assertion.

Keep exactly five P headings and three N headings.

- [ ] **Step 4: Update manual acceptance**

In `tests/chatgpt-acceptance.md`:

- current baseline/version/procedure becomes `0.5.0` and source verification `41/41`;
- Start checklist expects eleven categories with no follow-up field;
- Complete first turn includes a nature and no follow up;
- Missing-field follow-up is renamed to `Missing-field collection`, expects nature/type and no follow up;
- Relative-date confirmation uses meeting date plus a next-step deadline;
- `Explicit no next steps/follow up` becomes `Explicit no next steps` and asserts only `Nenhum próximo passo definido`;
- Detailed-note fidelity supplies a nature and no follow up;
- add acceptance steps for reversed nature alias and invalid nature.

Leave versioned historical evidence rows unchanged.

- [ ] **Step 5: Update manifests**

Set both manifest versions to `0.5.0`. Use the identical long description in both:

```text
Cole ou dite as anotações de uma visita comercial. O workflow coleta natureza, tipo, objetivo, responsáveis, participantes e demais campos obrigatórios, confirma datas inferidas, pergunta somente o que faltar e gera um relatório estruturado.
```

Keep display name, short description, URLs, icons, and starter prompts unchanged.

- [ ] **Step 6: Update release assertions in test_flow.py**

Change:

- `expected_version` to `0.5.0`;
- submission release-note checks to `Version 0.5.0` / `Version 0.5.0 delivers`;
- README archive assertion to `dist/documentar-reuniao-0.5.0.zip`.

Add a packaging assertion that current public docs do not contain `Data para follow up` or `Não haverá follow up`; do not scan historical specs/plans or versioned evidence rows.

- [ ] **Step 7: Run the full harness**

Run: `python3 scripts/test_flow.py 2>&1 | tail -3`

Expected: `All 41 conversational flow scenarios passed.`

- [ ] **Step 8: Commit**

```bash
git add README.md INSTRUCOES_DE_USO.md docs/public-submission.md tests/chatgpt-acceptance.md plugin.json .codex-plugin/plugin.json scripts/test_flow.py
git commit -m "chore: prepare visit report version 0.5.0"
```

---

### Task 5: Build, audit, and finalize

**Files:**
- Create (ignored): `dist/documentar-reuniao-0.5.0.zip`

- [ ] **Step 1: Run the complete deterministic suite**

Run: `python3 scripts/test_flow.py`

Expected: 41 PASS lines and `All 41 conversational flow scenarios passed.`

- [ ] **Step 2: Build the public archive**

Run: `./scripts/build_public_zip.sh`

Expected: integrity success and final path ending in `dist/documentar-reuniao-0.5.0.zip`.

- [ ] **Step 3: Verify archive members and contract**

```bash
unzip -Z1 dist/documentar-reuniao-0.5.0.zip
unzip -p dist/documentar-reuniao-0.5.0.zip plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.5.0"; print("manifest ok")'
unzip -p dist/documentar-reuniao-0.5.0.zip skills/relatorio-reuniao/SKILL.md | python3 -c 'import sys; t=sys.stdin.read(); assert "**Natureza da Visita:** {{visit_nature}}" in t; assert "**Tipo de Visita:** {{visit_type}}" in t; assert "## Próximos Passos" in t; assert "follow_up_date" not in t; assert "Data para follow up" not in t; print("contract ok")'
```

Expected members, in order:

```text
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

- [ ] **Step 4: Run the confidential history and worktree sweep**

Use the confidential keyword list supplied at execution time; never write that list into a tracked file. Expected: no matches in reachable history or working tree outside ignored build artifacts.

- [ ] **Step 5: Verify final Git state**

Run:

```bash
git status --short
git log --oneline -10
```

Expected: clean tracked worktree; no dist archive staged; one focused commit per implementation task.

---

## Verification Summary

- `SKILL.md` contains the exact public labels and no follow-up field.
- `comercial técnica` canonicalizes to `Técnica Comercial` before validation/rendering.
- Invalid nature asks only for `Natureza da Visita` when all other fields are complete.
- `python3 scripts/test_flow.py` passes 41 scenarios.
- `dist/documentar-reuniao-0.5.0.zip` contains only the four approved members.
- Confidential audit finds no production-report data in reachable history or working tree.
