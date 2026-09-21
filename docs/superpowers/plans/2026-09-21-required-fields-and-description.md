# Required Fields And Unified Description Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the report contract from seven to eleven required fields (commercial representative, technical representative, visit objective, participants with side and role, report author), remove `contacts`, and render one unified `Descrição` section grouped by topic under the new heading `Relatório de Visita`, releasing as `0.4.0`.

**Architecture:** Single-file skill (`SKILL.md`) holds the runtime contract in marker-delimited sections. The deterministic harness (`scripts/test_flow.py`) parses those sections, drives a state machine over JSON fixtures (`tests/scenarios.json`), and renders reports from the same template. Every change flows: spec amendment → SKILL.md sections → harness → fixtures → docs/manifests → rebuild.

**Tech Stack:** Python 3 (stdlib only), JSON fixtures, Bash packaging script, Markdown skill contract.

**Confidentiality rule (applies to every task):** no real client, company, participant, product, or logistics data from observed production reports may enter the repo. Use only the synthetic fixtures defined here (Acme/Beta, Ana/Bruna/Carla/Diego/Eva/João/Luciano-pattern). Before the final commit, grep the history for leak vectors.

**Spec:** `docs/superpowers/specs/2026-09-21-required-fields-and-description-design.md`

---

## File Structure

| File | Responsibility | Change |
| --- | --- | --- |
| `docs/superpowers/specs/2026-09-21-required-fields-and-description-design.md` | Approved design | Amend `provided_details` to structured objects (done before this plan, uncommitted) |
| `skills/relatorio-reuniao/SKILL.md` | Entire runtime contract | Rewrite intake, FIELD_SCHEMA, VALIDATION_RULES, workflow, Detail Fidelity, PARTIAL_EXAMPLE, REPORT_TEMPLATE, Common Mistakes |
| `scripts/test_flow.py` | Deterministic harness | `item_value_is_complete` enum support, optional item fields, `render_report` rewrite, heading assertion, packaging checks |
| `tests/scenarios.json` | Conversation fixtures | Migrate 33 cases to the new schema, add 6 new cases |
| `tests/chatgpt-acceptance.md` | Work-mode acceptance record | Baseline `0.4.0`, updated scenarios |
| `README.md` | Public docs | Field list, archive name |
| `INSTRUCOES_DE_USO.md` | User guide | Intake list, report contents |
| `docs/public-submission.md` | Portal material | Long description, P2/P3/P5, release notes |
| `plugin.json`, `.codex-plugin/plugin.json` | Manifests | Version `0.4.0`, long description |
| `scripts/build_public_zip.sh` | Packaging | No change (derives version from `plugin.json`) |

New fixture data uses only synthetic names: companies `Acme`, `Beta`, `Gamma`, `Delta`, `Epsilon`; people `Ana`, `Bruno`, `Bruna`, `Carla`, `Caio`, `Diego`, `Eva`, `João`; the pre-existing `Luciano` fixture stays as-is (already public in this repo).

---

### Task 1: Commit the spec amendment

`provided_details` must carry the topic association so the deterministic harness can group `Descrição` by topic. This edit was already applied to the spec file in the working tree.

**Files:**
- Modify: `docs/superpowers/specs/2026-09-21-required-fields-and-description-design.md`

- [ ] **Step 1: Verify the amended data-model line**

Run: `grep -n "array of objects, optional, never requested" docs/superpowers/specs/2026-09-21-required-fields-and-description-design.md`

Expected output contains: `9. `provided_details` — array of objects, optional, never requested. Each item carries `texto` ...`

- [ ] **Step 2: Run the full test suite to confirm a clean baseline**

Run: `python3 scripts/test_flow.py`
Expected: `All 33 conversational flow scenarios passed.` (SKILL.md untouched so far.)

- [ ] **Step 3: Commit the spec amendment**

```bash
git add docs/superpowers/specs/2026-09-21-required-fields-and-description-design.md
git commit -m "docs: model provided_details as topic-linked facts"
```

---

### Task 2: Rewrite the SKILL.md runtime contract

**Files:**
- Modify: `skills/relatorio-reuniao/SKILL.md`

- [ ] **Step 1: Replace the Required Record intro paragraph**

Replace:

```markdown
Only these seven fields are required. Time, duration, objective, decisions, success criteria, and unrelated deadlines are not required and must not be requested.
```

with:

```markdown
Only these eleven fields are required. Time, duration, decisions, success criteria, and unrelated deadlines are not required and must not be requested.
```

- [ ] **Step 2: Replace the FIELD_SCHEMA block**

Replace the entire `<!-- FIELD_SCHEMA_START -->` ... `<!-- FIELD_SCHEMA_END -->` JSON with:

```json
{
  "missingValue": "Não informado",
  "itemDateFormats":["YYYY-MM-DD","DD/MM/YYYY"],
  "fields": [
    {"id":"company","label":"Empresa (cliente)","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"meeting_date","label":"Data da reunião/visita","required":true,"type":"string","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}},
    {"id":"visit_type","label":"Tipo de reunião/visita","required":true,"type":"string","allowedValues":["corretiva","preventiva","desenvolvimento","negociação"],"validation":{"kind":"enum","caseInsensitive":true}},
    {"id":"objetivo_visita","label":"Objetivo da visita","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"responsavel_comercial","label":"Responsável comercial","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"responsavel_tecnico","label":"Responsável técnico","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não houve responsável técnico","validation":{"kind":"non_empty"}},
    {"id":"participantes","label":"Participantes","required":true,"type":"array<object>","itemFields":["nome","lado","funcao"],"itemFieldTypes":{"nome":"string","lado":"enum","funcao":"string"},"itemAllowedValues":{"lado":["cliente","empresa"]},"validation":{"kind":"non_empty_list"}},
    {"id":"topics_discussed","label":"Assuntos discutidos","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"provided_details","label":"Fatos fornecidos","required":false,"type":"array<object>","itemFields":["texto"],"itemOptionalFields":["topico"],"itemFieldTypes":{"topico":"string","texto":"string"}},
    {"id":"next_steps","label":"Próximos passos","required":true,"type":"array<object>","itemFields":["action","responsible","deadline"],"itemFieldTypes":{"action":"string","responsible":"string","deadline":"date"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
    {"id":"follow_up_date","label":"Data para follow up","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não haverá follow up","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}},
    {"id":"elaborado_por","label":"Elaborado por","required":true,"type":"string","validation":{"kind":"non_empty"}}
  ]
}
```

- [ ] **Step 3: Replace the VALIDATION_RULES block**

Replace the entire `<!-- VALIDATION_RULES_START -->` ... `<!-- VALIDATION_RULES_END -->` JSON with:

```json
{
  "missingSentinels":["não informado","nao informado","não sei","nao sei","desconhecido","unknown","n/a","não disponível","nao disponivel","omitido"],
  "explicitOverridePhrases":["continuar mesmo assim","continuar com pendências","continuar com pendencias","gerar mesmo com pendências","gerar mesmo com pendencias","pode gerar mesmo faltando","proceed anyway","continue anyway","generate anyway"],
  "explicitNegativeAnswers":{"next_steps":["não existem próximos passos","não há próximos passos","nenhum próximo passo"],"follow_up_date":["não haverá follow up","não será feito follow up","sem follow up"],"responsavel_tecnico":["não houve responsável técnico","não havia responsável técnico","sem responsável técnico"]}
}
```

- [ ] **Step 4: Replace the INTAKE collection list**

Replace the bullet list inside `<!-- INTAKE_START -->` ... `<!-- INTAKE_END -->` with:

```markdown
- empresa (cliente);
- data da reunião/visita;
- objetivo da visita;
- responsável comercial;
- responsável técnico, ou a declaração de que não houve;
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- tipo de reunião/visita: corretiva, preventiva, desenvolvimento ou negociação;
- assuntos discutidos;
- próximos passos, com o responsável e o prazo de cada ação;
- data para follow up;
- elaborado por.
```

Keep the surrounding intake sentences unchanged, including the sentence stating that details are never requested.

- [ ] **Step 5: Update the Workflow**

In the `## Workflow` list:

Replace step 2:

```markdown
2. Validate all seven fields after every turn. Ask one concise question containing only missing, invalid, conflicting, or unconfirmed required labels.
```

with:

```markdown
2. Validate all eleven fields after every turn. Ask one concise question containing only missing, invalid, conflicting, or unconfirmed required labels.
```

Replace step 4:

```markdown
4. Require every next-step action to have a responsible person and a deadline date. A direct statement that no next steps exist becomes `Nenhum próximo passo definido`.
```

with:

```markdown
4. Require every next-step action to have a responsible person and a deadline date. A direct statement that no next steps exist becomes `Nenhum próximo passo definido`. A direct statement that there was no technical representative becomes `Não houve responsável técnico`. Require every participant item to carry a name, a side (`cliente` or `empresa`) and a function; the explicit value `função não informada` completes only that participant's function, and a participant without name or side leaves `Participantes` unresolved.
```

- [ ] **Step 6: Update the Detail Fidelity section**

Replace the first bullet:

```markdown
- Fidelity applies to facts, not wording. Preserve every relevant user-supplied fact and store context and specificity behind topic labels in `provided_details`; a concise topic does not replace its supporting facts.
```

with:

```markdown
- Fidelity applies to facts, not wording. Preserve every relevant user-supplied fact and store it in `provided_details` with the `topico` of the informed topic it belongs to; a concise topic does not replace its supporting facts.
```

Replace the rendering bullet:

```markdown
- Rewriting is required, not optional. Render the detailed record as polished professional prose in a formal commercial register, connecting facts into clear sentences or short narrative paragraphs. Use bullets only for discrete parallel facts. A near-verbatim reproduction of the user's spoken phrasing is a fidelity failure.
```

with:

```markdown
- Rewriting is required, not optional. Render the unified `Descrição` section as polished professional prose in a formal commercial register, with each supplied topic as a bold label followed by the facts that belong to it. A near-verbatim reproduction of the user's spoken phrasing is a fidelity failure.
```

Replace the rich-notes paragraph:

```markdown
For rich notes, use the exact `Registro detalhado` heading and retain the actor attached to every attributed fact, including the reporter's own first-person actions. Do not rename the section from the field label or turn attributed statements into actorless summaries.
```

with:

```markdown
For rich notes, use the exact `Descrição` heading, render each supplied topic label in bold followed by its supporting facts as professional prose, retain the actor attached to every attributed fact including the reporter's own first-person actions, and render facts that fit no informed topic in a final unlabeled paragraph. Do not rename the section or turn attributed statements into actorless summaries.
```

- [ ] **Step 7: Update the DETAIL_FIDELITY_EXAMPLE**

Replace the section between `<!-- DETAIL_FIDELITY_EXAMPLE_START -->` and `<!-- DETAIL_FIDELITY_EXAMPLE_END -->` with:

```markdown
User facts (dictated by voice):

`então o Luciano falou que tipo o time de vendas devia registrar as reuniões no CRM mas que na real nunca faz isso, e ele tinha avaliado WhatsApp mas não resolveu, e pediu pra eu ver alternativa melhor, e aí eu falei que ia propor um plugin público pro ChatGPT`

Required section excerpt:

## Descrição

**Registro das reuniões no CRM** — Luciano relatou que o time de vendas deveria registrar as reuniões no CRM, mas que na prática isso não acontece. Luciano avaliou o WhatsApp como alternativa para esses registros. Luciano pediu alternativas melhores para o registro das reuniões.

**Plugin público para ChatGPT** — Eu propus um plugin público para ChatGPT.

The dictated sentences were rewritten as professional prose and grouped under the supplied topic labels. Every fact and its actor are retained, but none of the user's spoken phrasing survives as-is: do not echo dictated sentences near-verbatim.
```

- [ ] **Step 8: Update the Missing-Field Response section**

Replace:

```markdown
When validation finds unresolved fields, enumerate every unresolved required label and no completed or optional field. Do not ask for generic notes or say only “tell me the rest.” Do not request decisions, time, duration, objectives, success criteria, or unrelated deadlines.
```

with:

```markdown
When validation finds unresolved fields, enumerate every unresolved required label and no completed or optional field. Do not ask for generic notes or say only “tell me the rest.” Do not request decisions, time, duration, success criteria, or unrelated deadlines.
```

- [ ] **Step 9: Replace the PARTIAL_EXAMPLE**

Replace the section between `<!-- PARTIAL_EXAMPLE_START -->` and `<!-- PARTIAL_EXAMPLE_END -->` with:

```markdown
User:

`Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).`

Required response:

Para completar o relatório, informe:

- Tipo de reunião/visita;
- Objetivo da visita;
- Responsável comercial;
- Responsável técnico;
- Assuntos discutidos;
- Próximos passos, com responsável e prazo de cada ação;
- Data para follow up;
- Elaborado por.

Do not ask for generic notes. Do not request decisions. Do not repeat Empresa, Data da reunião/visita, or Participantes because the user already supplied them.
```

- [ ] **Step 10: Replace the Report Output section**

Replace the paragraph:

```markdown
Render this template in order. Render contacts as comma-separated names, topics as bullets, and action-based next steps as a table with `Ação`, `Responsável` and `Prazo` columns.
```

with:

```markdown
Render this template in order. Render participants as one `Nome — Lado — Função` line each with `Cliente` or `Empresa` capitalized, render the unified `Descrição` section with each supplied topic as a bold label followed by its supporting facts as professional prose, and render action-based next steps as a table with `Ação`, `Responsável` and `Prazo` columns.
```

Replace:

```markdown
For every complete, overridden or regenerated report, the entire message must be exactly the report, beginning with `# Relatório de reunião/visita`.
```

with:

```markdown
For every complete, overridden or regenerated report, the entire message must be exactly the report, beginning with `# Relatório de Visita`.
```

- [ ] **Step 11: Replace the REPORT_TEMPLATE block**

Replace the section between `<!-- REPORT_TEMPLATE_START -->` and `<!-- REPORT_TEMPLATE_END -->` with:

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

{{participantes}}

## Descrição

{{descricao_section}}

## Próximos passos

{{next_steps}}

**Elaborado por:** {{elaborado_por}}
```

Keep the two trailing spaces after each header line so Markdown renders the line breaks.

- [ ] **Step 12: Update Common Mistakes**

Replace:

```markdown
- Do not request time, duration, decisions, success criteria, or unrelated deadlines.
```

with:

```markdown
- Do not request time, duration, decisions, success criteria, or unrelated deadlines.
- Do not render `Assuntos discutidos` and `Registro detalhado` as separate sections; the unified `Descrição` section is the only narrative section.
```

(Keep every other bullet unchanged.)

- [ ] **Step 13: Run the harness and verify the expected failure**

Run: `python3 scripts/test_flow.py 2>&1 | tail -3`
Expected: FAIL — `SKILL.md is missing strict generation behavior: only these seven fields are required, beginning with `# relatório de reunião/visita`` (packaging checks pin the old concepts until Task 3).

- [ ] **Step 14: Commit**

```bash
git add skills/relatorio-reuniao/SKILL.md
git commit -m "feat: require team fields and unified description in runtime contract"
```

---

### Task 3: Update the deterministic harness

**Files:**
- Modify: `scripts/test_flow.py`

- [ ] **Step 1: Extend `item_value_is_complete` with enum support and the field reference**

Replace the function (currently around line 101):

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

with:

```python
def item_value_is_complete(
    field: dict[str, Any], item_field: str, value: Any
) -> bool:
    kind = field.get("itemFieldTypes", {}).get(item_field)
    if kind == "string":
        return isinstance(value, str) and is_substantive(value, MISSING_SENTINELS)
    if kind == "date":
        return is_absolute_date(value, ITEM_DATE_FORMATS)
    if kind == "enum":
        allowed = field.get("itemAllowedValues", {}).get(item_field, [])
        return isinstance(value, str) and normalize(value) in {
            normalize(option) for option in allowed
        }
    return False
```

- [ ] **Step 2: Honor optional item fields in `field_is_complete`**

Replace the `array<object>` branch (currently around line 146):

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

with:

```python
    if field_type == "array<object>":
        item_fields = field.get("itemFields", [])
        optional_fields = set(field.get("itemOptionalFields", []))
        required_item_fields = [
            item_field for item_field in item_fields if item_field not in optional_fields
        ]
        return (
            isinstance(value, list)
            and bool(value)
            and bool(required_item_fields)
            and all(
                isinstance(item, dict)
                and all(
                    item_value_is_complete(field, item_field, item.get(item_field))
                    for item_field in required_item_fields
                )
                for item in value
            )
        )
```

- [ ] **Step 3: Replace `render_report`**

Replace the function (currently around line 296) with:

```python
def render_participants(record: dict[str, Any], missing: list[str]) -> str:
    if "participantes" in missing:
        return FIELD_SCHEMA["missingValue"]
    value = record.get("participantes")
    if not isinstance(value, list) or not value:
        return FIELD_SCHEMA["missingValue"]
    lines = []
    for item in value:
        if not isinstance(item, dict):
            continue
        nome = next_step_cell(item.get("nome"))
        lado_value = item.get("lado")
        lado = (
            {"cliente": "Cliente", "empresa": "Empresa"}.get(normalize(str(lado_value)), lado_value)
            if isinstance(lado_value, str)
            else FIELD_SCHEMA["missingValue"]
        )
        funcao = item.get("funcao")
        if isinstance(funcao, str) and normalize(funcao) == normalize("função não informada"):
            funcao_value = "(função não informada)"
        else:
            funcao_value = next_step_cell(funcao)
        lines.append(f"- {nome} — {lado} — {funcao_value}")
    return "\n".join(lines)


def render_description(record: dict[str, Any], missing: list[str]) -> str:
    topics = record.get("topics_discussed")
    if "topics_discussed" in missing or not isinstance(topics, list):
        topics = []
    topic_details: dict[int, list[str]] = {}
    trailing: list[str] = []
    details = record.get("provided_details")
    if isinstance(details, list):
        for item in details:
            if not isinstance(item, dict):
                continue
            texto = item.get("texto")
            if not isinstance(texto, str) or not is_substantive(texto, MISSING_SENTINELS):
                continue
            topico = item.get("topico")
            match = None
            if isinstance(topico, str) and is_substantive(topico, MISSING_SENTINELS):
                topico_norm = normalize(topico)
                for index, topic in enumerate(topics):
                    if isinstance(topic, str) and normalize(topic) == topico_norm:
                        match = index
                        break
            if match is None:
                trailing.append(texto)
            else:
                topic_details.setdefault(match, []).append(texto)
    if not topics and not trailing:
        return FIELD_SCHEMA["missingValue"]
    if not topics:
        return " ".join(trailing)
    lines = []
    for index, topic in enumerate(topics):
        prose = " ".join(topic_details.get(index, []))
        lines.append(f"**{topic}** — {prose}" if prose else f"**{topic}**")
    if trailing:
        lines.append(" ".join(trailing))
    return "\n\n".join(lines)


def render_report(record: dict[str, Any], missing: list[str]) -> str:
    template = extract_skill_section("REPORT_TEMPLATE")
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}

    def value_or_missing(field_id: str) -> Any:
        if field_id in missing:
            return FIELD_SCHEMA["missingValue"]
        return record.get(field_id, FIELD_SCHEMA["missingValue"])

    values = {
        "company": value_or_missing("company"),
        "meeting_date": value_or_missing("meeting_date"),
        "visit_type": value_or_missing("visit_type"),
        "objetivo_visita": value_or_missing("objetivo_visita"),
        "responsavel_comercial": value_or_missing("responsavel_comercial"),
        "responsavel_tecnico": value_or_missing("responsavel_tecnico"),
        "follow_up_date": value_or_missing("follow_up_date"),
        "participantes": render_participants(record, missing),
        "descricao_section": render_description(record, missing),
        "next_steps": render_next_steps(record),
        "elaborado_por": value_or_missing("elaborado_por"),
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))

    if missing:
        pending = "\n".join(f"- {labels[field_id]}" for field_id in missing)
        template += f"\n\n## Pendências de informação\n\n{pending}\n"
    return template.strip()
```

- [ ] **Step 4: Update the report heading assertion**

In `assert_inline_report_delivery`, replace:

```python
    if not output.startswith("# Relatório de reunião/visita"):
        raise AssertionError("the entire message must be exactly the report")
```

with:

```python
    if not output.startswith("# Relatório de Visita"):
        raise AssertionError("the entire message must be exactly the report")
```

- [ ] **Step 5: Update the pinned version and packaging content**

In `check_packaging`:

Replace `expected_version = "0.3.8"` with `expected_version = "0.4.0"`.

Replace both submission assertions:

```python
    if "Version 0.3.8" not in submission:
        raise AssertionError("submission release notes must name version 0.3.8")
```
→
```python
    if "Version 0.4.0" not in submission:
        raise AssertionError("submission release notes must name version 0.4.0")
```

```python
    if "dist/documentar-reuniao-0.3.8.zip" not in readme:
```
→
```python
    if "dist/documentar-reuniao-0.4.0.zip" not in readme:
```

Replace `"Version 0.3.8 delivers the report",` with `"Version 0.4.0 delivers the report",` in `required_submission_content`.

- [ ] **Step 6: Update `required_skill_concepts`**

Replace the two stale concepts and add the new ones:

```python
        "only these seven fields are required",
```
→
```python
        "only these eleven fields are required",
```

```python
        "time, duration, objective, decisions, success criteria",
```
→
```python
        "time, duration, decisions, success criteria",
        "não houve responsável técnico",
        "função não informada",
        "## descrição",
```

```python
        "beginning with `# relatório de reunião/visita`",
```
→
```python
        "beginning with `# relatório de visita`",
```

- [ ] **Step 7: Replace the provided_details label check with schema checks**

Replace (currently around line 683):

```python
    provided_details_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "provided_details"
    )
    if provided_details_field["label"] != "Registro detalhado":
        raise AssertionError(
            "provided_details label must match the required report heading"
        )
```

with:

```python
    participantes_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "participantes"
    )
    if participantes_field.get("itemFields") != ["nome", "lado", "funcao"]:
        raise AssertionError("participantes items must carry nome, lado and funcao")
    if participantes_field.get("itemAllowedValues", {}).get("lado") != [
        "cliente",
        "empresa",
    ]:
        raise AssertionError("participantes lado must be cliente or empresa")
    tecnico_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "responsavel_tecnico"
    )
    if tecnico_field.get("explicitNoneValue") != "Não houve responsável técnico":
        raise AssertionError("responsavel_tecnico must allow its explicit none value")
    details_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "provided_details"
    )
    if details_field.get("itemFields") != ["texto"] or details_field.get(
        "itemOptionalFields"
    ) != ["topico"]:
        raise AssertionError("provided_details items must carry texto and optional topico")
```

- [ ] **Step 8: Update the required intake labels**

Replace the tuple (currently around line 748):

```python
    required_intake_labels = (
        "empresa (cliente)",
        "data da reunião/visita",
        "pessoa(s) de contato",
        "corretiva, preventiva, desenvolvimento ou negociação",
        "assuntos discutidos",
        "responsável e o prazo de cada ação",
        "data para follow up",
    )
```

with:

```python
    required_intake_labels = (
        "empresa (cliente)",
        "data da reunião/visita",
        "objetivo da visita",
        "responsável comercial",
        "responsável técnico",
        "participantes",
        "corretiva, preventiva, desenvolvimento ou negociação",
        "assuntos discutidos",
        "responsável e o prazo de cada ação",
        "data para follow up",
        "elaborado por",
    )
```

- [ ] **Step 9: Update the partial example assertions**

Replace the prompt/content tuple (currently around line 766):

```python
    required_partial_content = (
        "Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.",
        "Tipo de reunião/visita",
        "Assuntos discutidos",
        "Próximos passos, com responsável e prazo de cada ação",
        "Data para follow up",
        "Do not ask for generic notes",
        "Do not request decisions",
    )
```

with:

```python
    required_partial_content = (
        "Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).",
        "Tipo de reunião/visita",
        "Objetivo da visita",
        "Responsável comercial",
        "Responsável técnico",
        "Assuntos discutidos",
        "Próximos passos, com responsável e prazo de cada ação",
        "Data para follow up",
        "Elaborado por",
        "Do not ask for generic notes",
        "Do not request decisions",
    )
```

- [ ] **Step 10: Update the detail example assertions**

Replace the tuple (currently around line 785):

```python
    required_detail_content = (
        "## Registro detalhado",
        "Luciano relatou",
        "Luciano avaliou",
        "Luciano pediu",
        "Eu propus",
    )
```

with:

```python
    required_detail_content = (
        "## Descrição",
        "**Registro das reuniões no CRM**",
        "**Plugin público para ChatGPT**",
        "Luciano relatou",
        "Luciano avaliou",
        "Luciano pediu",
        "Eu propus",
    )
```

- [ ] **Step 11: Update the template placeholders**

Replace the tuple (currently around line 802):

```python
    required_placeholders = (
        "{{company}}",
        "{{meeting_date}}",
        "{{contacts}}",
        "{{visit_type}}",
        "{{follow_up_date}}",
        "{{topics_discussed}}",
        "{{provided_details_section}}",
        "{{next_steps}}",
    )
```

with:

```python
    required_placeholders = (
        "{{company}}",
        "{{meeting_date}}",
        "{{visit_type}}",
        "{{objetivo_visita}}",
        "{{responsavel_comercial}}",
        "{{responsavel_tecnico}}",
        "{{follow_up_date}}",
        "{{participantes}}",
        "{{descricao_section}}",
        "{{next_steps}}",
        "{{elaborado_por}}",
    )
```

- [ ] **Step 12: Run the harness and verify the expected failure**

Run: `python3 scripts/test_flow.py 2>&1 | tail -3`
Expected: FAIL on scenario fixtures only (they still use `contacts`), e.g. `ask-only-for-missing-then-merge: ...` — packaging checks now pass. If a packaging assertion still fails, fix it before proceeding.

- [ ] **Step 13: Commit**

```bash
git add scripts/test_flow.py
git commit -m "test: render extended report contract in harness"
```

---

### Task 4: Migrate fixtures and add new scenarios

**Files:**
- Modify: `tests/scenarios.json`

Replace the entire `cases` array with the content below. Every migrated case gains the five new fields (values shown per case); `contacts` becomes `participantes`; label strings in `outputContains`/`outputNotContains`/`missing` update accordingly. New cases come last.

- [ ] **Step 1: Write the migrated and new fixtures**

Replace the whole `tests/scenarios.json` with:

```json
{
  "scenariosVersion": "0.2.0",
  "description": "Offline state-machine fixtures. `fields` represent facts already extracted from a user turn; the harness does not pretend to parse natural language.",
  "cases": [
    {
      "id": "selected-plugin-starts-intake",
      "activation": "plugin_selected",
      "turns": [],
      "expectations": [
        {
          "action": "send_intake",
          "state": "INTAKE",
          "missing": [],
          "outputContains": ["empresa (cliente)", "data da reunião/visita", "objetivo da visita", "responsável comercial", "responsável técnico", "participantes", "corretiva, preventiva, desenvolvimento ou negociação", "assuntos discutidos", "responsável e o prazo de cada ação", "data para follow up", "elaborado por"]
        }
      ]
    },
    {
      "id": "explicit-mention-start-command-starts-intake",
      "activation": "explicit_mention",
      "turns": [
        {
          "text": "@Documentar Reunião começar",
          "fields": {}
        }
      ],
      "expectations": [
        {
          "action": "send_intake",
          "state": "INTAKE",
          "missing": [],
          "outputContains": ["empresa (cliente)", "data da reunião/visita", "objetivo da visita", "responsável comercial", "responsável técnico", "participantes", "corretiva, preventiva, desenvolvimento ou negociação", "assuntos discutidos", "responsável e o prazo de cada ação", "data para follow up", "elaborado por"]
        }
      ]
    },
    {
      "id": "explicit-mention-treats-suffix-as-first-turn",
      "activation": "explicit_mention",
      "turns": [
        {
          "text": "@Documentar Reunião Empresa Acme, reunião em 10/09/2026 com Ana, tipo negociação. Discutimos a renovação do contrato. Bruno enviará a proposta e o follow up será em 16/09/2026.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-10",
            "visit_type": "negociação",
            "objetivo_visita": "Renovar o contrato",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Renovação do contrato"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-12"}],
            "follow_up_date": "2026-09-16",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "generate", "state": "DONE", "missing": [], "outputNotContains": ["Pendências de informação"]}
      ]
    },
    {
      "id": "complete-on-first-turn",
      "invoked": true,
      "turns": [
        {
          "text": "Use relatorio-reuniao. Empresa Acme, reunião em 10/09/2026 com Ana, tipo negociação. Discutimos a renovação do contrato e o escopo comercial. Bruno enviará a proposta revisada e o follow up será em 16/09/2026.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-10",
            "visit_type": "negociação",
            "objetivo_visita": "Renovar o contrato",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Renovação do contrato", "Escopo comercial"],
            "next_steps": [{"action": "Enviar proposta revisada", "responsible": "Bruno", "deadline": "2026-09-12"}],
            "follow_up_date": "2026-09-16",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "generate", "state": "DONE", "missing": [], "outputContains": ["## Descrição", "- Ana — Cliente — Compras", "- Bruna — Empresa — Comercial", "**Elaborado por:** Bruna"], "outputNotContains": ["Pendências de informação", "## Registro detalhado"]}
      ]
    },
    {
      "id": "ask-only-for-missing-then-merge",
      "invoked": true,
      "turns": [
        {
          "text": "Foi uma visita à Beta em 2026-09-11.",
          "fields": {
            "company": "Beta",
            "meeting_date": "2026-09-11",
            "visit_type": "preventiva",
            "objetivo_visita": "Avaliar o processo atual",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Carla", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Processo atual"],
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "Os próximos passos são preparar a demonstração com a Carla como responsável; o follow up será em 2026-09-18.",
          "fields": {
            "next_steps": [{"action": "Preparar demonstração", "responsible": "Carla", "deadline": "2026-09-17"}],
            "follow_up_date": "2026-09-18"
          }
        }
      ],
      "expectations": [
        {
          "action": "ask_missing",
          "state": "WAITING_FOR_MISSING",
          "missing": ["next_steps", "follow_up_date"],
          "outputContains": ["Próximos passos", "Data para follow up"],
          "outputNotContains": ["Empresa (cliente)", "Data da reunião/visita", "Tipo de reunião/visita", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Participantes", "Assuntos discutidos", "Elaborado por"]
        },
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "explicit-override-generates-with-gaps",
      "invoked": true,
      "turns": [
        {
          "text": "Temos uma visita à Gamma em 2026-09-12. Pode gerar mesmo com pendências.",
          "fields": {
            "company": "Gamma",
            "meeting_date": "2026-09-12",
            "visit_type": "desenvolvimento",
            "objetivo_visita": "Apresentar a nova solução",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Diego", "lado": "cliente", "funcao": "Diretoria"}
            ],
            "topics_discussed": ["Nova solução"],
            "provided_details": [{"topico": "Nova solução", "texto": "Diego explicou que a solução atual exige retrabalho manual."}],
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE_WITH_GAPS",
          "missing": ["next_steps", "follow_up_date"],
          "outputContains": ["Pendências de informação", "Próximos passos", "Data para follow up", "## Descrição", "retrabalho manual"]
        }
      ]
    },
    {
      "id": "ambiguous-follow-up-is-not-override",
      "invoked": true,
      "turns": [
        {
          "text": "A visita foi com a Delta. Pode seguir com isso?",
          "fields": {
            "company": "Delta"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "invalid-visit-type-asks-only-for-type",
      "invoked": true,
      "turns": [
        {
          "text": "Visita à Epsilon em 2026-09-13, tipo instalação.",
          "fields": {
            "company": "Epsilon",
            "meeting_date": "2026-09-13",
            "visit_type": "instalação",
            "objetivo_visita": "Inspecionar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Eva", "lado": "cliente", "funcao": "Manutenção"}
            ],
            "topics_discussed": ["Manutenção"],
            "next_steps": [{"action": "Enviar instruções", "responsible": "Eva", "deadline": "2026-09-18"}],
            "follow_up_date": "2026-09-20",
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "Corrigindo: o tipo de visita foi corretiva.",
          "fields": {"visit_type": "corretiva"}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["visit_type"]},
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "missing-only-visit-type-asks-only-for-type",
      "invoked": true,
      "turns": [
        {
          "text": "Tenho todos os dados do registro, menos o tipo de reunião/visita.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão do equipamento"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}],
            "follow_up_date": "2026-09-22",
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "O tipo de reunião/visita foi preventiva.",
          "fields": {"visit_type": "preventiva"}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["visit_type"]},
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "planning-context-is-not-complete-report",
      "invoked": true,
      "turns": [
        {
          "text": "Atualizei os prazos e responsabilidades: até 15/09/2026 finalizo e disponibilizo o plugin para o Luciano; em 16 e 17/09 ele instala e testa no Android; até 17/09 informa o resultado e o feedback. O critério é o funcionamento no Android e a adequação do relatório.",
          "fields": {}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["company", "meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "generic-meeting-schema-does-not-satisfy-report-contract",
      "invoked": true,
      "turns": [
        {
          "text": "Eu tive a reunião em 13/09/2026, foi uma da tarde, durou aproximadamente uma hora e foi com o Luciano. Falamos sobre automatizar o registro das reuniões e elaborar uma prova de conceito. Eu fiquei de elaborar o protótipo e disponibilizar o plugin; o Luciano vai instalar, testar e dar o retorno.",
          "fields": {
            "meeting_date": "2026-09-13",
            "participantes": [{"nome": "Luciano", "lado": "cliente", "funcao": "não informada"}],
            "topics_discussed": ["Automatizar o registro das reuniões", "Elaborar uma prova de conceito"],
            "next_steps": [
              {"action": "Elaborar o protótipo e disponibilizar o plugin", "responsible": "eu", "deadline": "2026-09-14"},
              {"action": "Instalar, testar e dar o retorno", "responsible": "Luciano", "deadline": "2026-09-16"}
            ]
          }
        },
        {
          "text": "Os participantes foram só eu mesmo e o Luciano. Os campos obrigatórios ainda não foram definidos.",
          "fields": {"participantes": [{"nome": "João", "lado": "empresa", "funcao": "não informada"}, {"nome": "Luciano", "lado": "cliente", "funcao": "não informada"}]}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["company", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "follow_up_date", "elaborado_por"]},
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["company", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "string-does-not-satisfy-participants-list",
      "invoked": true,
      "turns": [
        {
          "text": "Os participantes foram informados em formato inválido no registro extraído.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": "Ana",
            "topics_discussed": ["Revisão"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["participantes"]}
      ]
    },
    {
      "id": "explicit-none-completes-next-steps-and-follow-up",
      "invoked": true,
      "turns": [
        {
          "text": "Não existem próximos passos e não haverá follow up.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE",
          "missing": [],
          "outputContains": ["Nenhum próximo passo definido", "Não haverá follow up"],
          "outputNotContains": ["Pendências de informação"]
        }
      ]
    },
    {
      "id": "relative-dates-require-confirmation",
      "invoked": true,
      "turns": [
        {
          "text": "A reunião foi ontem e o follow up será sexta que vem.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-14",
            "visit_type": "corretiva",
            "objetivo_visita": "Corrigir a falha do equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Falha no equipamento"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-17"}],
            "follow_up_date": "2026-09-18",
            "elaborado_por": "Bruna"
          },
          "inferredDates": ["meeting_date", "follow_up_date"]
        },
        {
          "text": "Confirmo as duas datas.",
          "fields": {},
          "confirmedDates": ["meeting_date", "follow_up_date"]
        }
      ],
      "expectations": [
        {"action": "confirm_dates", "state": "WAITING_FOR_CONFIRMATION", "missing": ["meeting_date", "follow_up_date"]},
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "relative-date-can-be-corrected",
      "invoked": true,
      "turns": [
        {
          "text": "A reunião foi ontem.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-14",
            "visit_type": "negociação",
            "objetivo_visita": "Renegociar o contrato",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Contrato"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          },
          "inferredDates": ["meeting_date"]
        },
        {
          "text": "Não. A data correta foi 13/09/2026.",
          "fields": {"meeting_date": "2026-09-13"}
        }
      ],
      "expectations": [
        {"action": "confirm_dates", "state": "WAITING_FOR_CONFIRMATION", "missing": ["meeting_date"]},
        {"action": "generate", "state": "DONE", "missing": []}
      ]
    },
    {
      "id": "negated-override-phrase-does-not-generate",
      "invoked": true,
      "turns": [
        {
          "text": "Não quero continuar mesmo assim.",
          "fields": {"company": "Acme"}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "invalid-absolute-date-remains-missing",
      "invoked": true,
      "turns": [
        {
          "text": "A data extraída foi inválida.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-99-99",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "ask_missing",
          "state": "WAITING_FOR_MISSING",
          "missing": ["meeting_date"],
          "outputContains": ["Data da reunião/visita"],
          "outputNotContains": ["Empresa (cliente)", "Participantes", "Assuntos discutidos", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Elaborado por"]
        }
      ]
    },
    {
      "id": "next-step-values-must-be-strings",
      "invoked": true,
      "turns": [
        {
          "text": "Os próximos passos foram extraídos com tipos inválidos.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": 123, "responsible": 456}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["next_steps"]}
      ]
    },
    {
      "id": "explicit-retraction-clears-prior-value",
      "invoked": true,
      "turns": [
        {
          "text": "Registro completo.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "Correção: os participantes anteriores estão incorretos e ainda não foram informados.",
          "fields": {"participantes": "não informado"}
        }
      ],
      "expectations": [
        {"action": "generate", "state": "DONE", "missing": []},
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["participantes"]}
      ]
    },
    {
      "id": "ambiguous-conflict-asks-only-for-conflicting-field",
      "invoked": true,
      "turns": [
        {
          "text": "Registro completo da Acme.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "A empresa foi Beta ou Gama; não tenho certeza. A data de follow up anterior também está incorreta e ainda não foi informada.",
          "fields": {"follow_up_date": "não informado"},
          "conflictingFields": ["company"]
        },
        {
          "text": "Confirmando: foi a Beta.",
          "fields": {"company": "Beta"}
        },
        {
          "text": "Não haverá follow up.",
          "fields": {"follow_up_date": "Não haverá follow up"}
        }
      ],
      "expectations": [
        {"action": "generate", "state": "DONE", "missing": []},
        {
          "action": "ask_clarification",
          "state": "WAITING_FOR_CLARIFICATION",
          "missing": ["company", "follow_up_date"],
          "outputContains": ["Empresa (cliente)"],
          "outputNotContains": ["Data da reunião/visita", "Tipo de reunião/visita", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Participantes", "Assuntos discutidos", "Data para follow up", "Elaborado por"]
        },
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["follow_up_date"]},
        {"action": "generate", "state": "DONE", "missing": [], "outputContains": ["Beta", "Não haverá follow up"]}
      ]
    },
    {
      "id": "hypothetical-override-mention-does-not-generate",
      "invoked": true,
      "turns": [
        {
          "text": "Se eu disser continuar mesmo assim, o que acontece?",
          "fields": {"company": "Acme"}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "relative-date-prompt-shows-resolved-calendar-date",
      "invoked": true,
      "turns": [
        {
          "text": "A reunião foi ontem.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-14",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          },
          "inferredDates": ["meeting_date"]
        }
      ],
      "expectations": [
        {
          "action": "confirm_dates",
          "state": "WAITING_FOR_CONFIRMATION",
          "missing": ["meeting_date"],
          "outputContains": ["Data da reunião/visita", "2026-09-14"]
        }
      ]
    },
    {
      "id": "correction-after-generation-regenerates-report",
      "invoked": true,
      "turns": [
        {
          "text": "Registro completo.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão inicial"],
            "provided_details": [{"topico": "Revisão inicial", "texto": "Ana relatou que o processo era manual."}],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        },
        {
          "text": "Correção: discutimos a renovação.",
          "fields": {
            "topics_discussed": ["Renovação"],
            "provided_details": [{"topico": "Renovação", "texto": "Ana esclareceu que o processo já era automatizado."}]
          }
        }
      ],
      "expectations": [
        {"action": "generate", "state": "DONE", "missing": []},
        {"action": "generate", "state": "DONE", "missing": [], "outputContains": ["**Renovação**", "processo já era automatizado"], "outputNotContains": ["Revisão inicial", "processo era manual", "Pendências de informação"]}
      ]
    },
    {
      "id": "negative-answer-does-not-complete-unrelated-field",
      "invoked": true,
      "turns": [
        {
          "text": "A empresa não foi informada.",
          "fields": {
            "company": "Não haverá follow up",
            "meeting_date": "2026-09-15",
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
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["company"]}
      ]
    },
    {
      "id": "action-without-responsible-remains-missing",
      "invoked": true,
      "turns": [
        {
          "text": "Há uma ação, mas o responsável não foi informado.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta"}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["next_steps"]}
      ]
    },
    {
      "id": "non-affirmative-override-mentions-do-not-generate",
      "invoked": true,
      "turns": [
        {
          "text": "Explique o que significa continuar mesmo assim.",
          "fields": {"company": "Acme"}
        },
        {
          "text": "Talvez continuar mesmo assim.",
          "fields": {}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]},
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "negative-answers-inside-collections-are-invalid",
      "invoked": true,
      "turns": [
        {
          "text": "A extração colocou respostas negativas em campos não relacionados.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [{"nome": "Não haverá follow up", "lado": "cliente", "funcao": "Compras"}],
            "topics_discussed": ["Nenhum próximo passo"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Sem follow up", "deadline": "2026-09-18"}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["participantes", "topics_discussed", "next_steps"]}
      ]
    },
    {
      "id": "override-distinguishes-confirmation-from-possibility-question",
      "invoked": true,
      "turns": [
        {
          "text": "Continuar mesmo assim seria possível?",
          "fields": {"company": "Acme"}
        },
        {
          "text": "Sim continuar mesmo assim.",
          "fields": {}
        },
        {
          "text": "Confirmo: continuar mesmo assim.",
          "fields": {}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]},
        {"action": "generate", "state": "DONE_WITH_GAPS", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]},
        {"action": "generate", "state": "DONE_WITH_GAPS", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "quoted-override-phrase-does-not-generate",
      "invoked": true,
      "turns": [
        {
          "text": "“continuar mesmo assim”",
          "fields": {"company": "Acme"}
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["meeting_date", "visit_type", "objetivo_visita", "responsavel_comercial", "responsavel_tecnico", "participantes", "topics_discussed", "next_steps", "follow_up_date", "elaborado_por"]}
      ]
    },
    {
      "id": "rich-notes-preserve-all-relevant-details",
      "invoked": true,
      "turns": [
        {
          "text": "A reunião da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-13",
            "visit_type": "desenvolvimento",
            "objetivo_visita": "Alinhar o registro de reuniões no CRM",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Luciano", "lado": "cliente", "funcao": "não informada"},
              {"nome": "João", "lado": "empresa", "funcao": "Projetos"}
            ],
            "topics_discussed": ["Adoção do registro de reuniões no CRM", "Alternativas ao WhatsApp", "Plugin público para ChatGPT"],
            "provided_details": [
              {"topico": "Adoção do registro de reuniões no CRM", "texto": "A reunião ocorreu às 13h e durou aproximadamente uma hora."},
              {"topico": "Adoção do registro de reuniões no CRM", "texto": "Luciano relatou que o time de vendas deveria registrar reuniões com clientes, mas não vem fazendo isso de forma consistente, e os registros deveriam estar entrando no CRM."},
              {"topico": "Alternativas ao WhatsApp", "texto": "Durante a conversa, Luciano avaliou uma solução baseada em WhatsApp e pediu alternativas melhores."},
              {"topico": "Plugin público para ChatGPT", "texto": "Foi proposto um plugin público para ChatGPT que Luciano e o time dele poderão instalar."},
              {"texto": "Os requisitos foram recebidos na segunda-feira, antes da preparação da prova de conceito, e o teste será realizado em dispositivos móveis."}
            ],
            "next_steps": [
              {"action": "Preparar e enviar a prova de conceito até o fim do dia", "responsible": "João", "deadline": "2026-09-13"},
              {"action": "Instalar, testar em dispositivos móveis e enviar retorno até 17/09/2026", "responsible": "Luciano", "deadline": "2026-09-17"}
            ],
            "follow_up_date": "2026-09-17",
            "elaborado_por": "João"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE",
          "missing": [],
          "outputContains": ["## Descrição", "**Adoção do registro de reuniões no CRM**", "**Alternativas ao WhatsApp**", "**Plugin público para ChatGPT**", "13h", "aproximadamente uma hora", "Luciano relatou", "CRM", "WhatsApp", "plugin público", "segunda-feira", "dispositivos móveis", "fim do dia", "17/09/2026"]
        }
      ]
    },
    {
      "id": "next-step-deadline-asks-only-for-deadline",
      "invoked": true,
      "turns": [
        {
          "text": "Bruno enviará a proposta, mas o prazo ainda não foi definido.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
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
          "outputNotContains": ["Empresa (cliente)", "Data da reunião/visita", "Tipo de reunião/visita", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Participantes", "Assuntos discutidos", "Data para follow up", "Elaborado por"]
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
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno", "deadline": "2026-09-18"}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          },
          "inferredNextStepDeadlines": [0]
        },
        {
          "text": "Confirmo o prazo do passo.",
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
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
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
    },
    {
      "id": "technical-representative-explicit-none-renders-value",
      "invoked": true,
      "turns": [
        {
          "text": "Não houve responsável técnico nesta visita.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "negociação",
            "objetivo_visita": "Renegociar o contrato",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Não houve responsável técnico",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Contrato"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE",
          "missing": [],
          "outputContains": ["Não houve responsável técnico"],
          "outputNotContains": ["Pendências de informação"]
        }
      ]
    },
    {
      "id": "participant-without-function-uses-explicit-escape",
      "invoked": true,
      "turns": [
        {
          "text": "A função de um dos participantes não foi informada.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "função não informada"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Revisão"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE",
          "missing": [],
          "outputContains": ["- Ana — Cliente — (função não informada)"],
          "outputNotContains": ["Pendências de informação"]
        }
      ]
    },
    {
      "id": "participant-missing-required-subfield-prompts-only-participantes",
      "invoked": true,
      "turns": [
        {
          "text": "Um participante foi registrado sem função e sem lado.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [{"nome": "Ana", "funcao": "Compras"}],
            "topics_discussed": ["Revisão"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "ask_missing",
          "state": "WAITING_FOR_MISSING",
          "missing": ["participantes"],
          "outputContains": ["Participantes"],
          "outputNotContains": ["Empresa (cliente)", "Data da reunião/visita", "Tipo de reunião/visita", "Objetivo da visita", "Responsável comercial", "Responsável técnico", "Assuntos discutidos", "Próximos passos", "Data para follow up", "Elaborado por"]
        }
      ]
    },
    {
      "id": "participant-invalid-lado-prompts-only-participantes",
      "invoked": true,
      "turns": [
        {
          "text": "O lado de um participante foi extraído com valor inválido.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [{"nome": "Ana", "lado": "fornecedor", "funcao": "Compras"}],
            "topics_discussed": ["Revisão"],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {"action": "ask_missing", "state": "WAITING_FOR_MISSING", "missing": ["participantes"]}
      ]
    },
    {
      "id": "descricao-groups-facts-by-topic",
      "invoked": true,
      "turns": [
        {
          "text": "Registro completo da visita à Acme.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "negociação",
            "objetivo_visita": "Renegociar o contrato",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "topics_discussed": ["Contrato", "Renovação"],
            "provided_details": [
              {"topico": "Contrato", "texto": "Bruna relatou que o contrato vence em dezembro."},
              {"topico": "Renovação", "texto": "Ana pediu a revisão dos valores."},
              {"texto": "A visita durou cerca de uma hora."}
            ],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE",
          "missing": [],
          "outputContains": ["## Descrição", "**Contrato**", "contrato vence em dezembro", "**Renovação**", "revisão dos valores", "A visita durou cerca de uma hora", "**Elaborado por:** Bruna"],
          "outputNotContains": ["## Assuntos discutidos", "## Registro detalhado"]
        }
      ]
    },
    {
      "id": "descricao-details-without-topics-render-trailing-prose",
      "invoked": true,
      "turns": [
        {
          "text": "Continuar mesmo assim.",
          "fields": {
            "company": "Acme",
            "meeting_date": "2026-09-15",
            "visit_type": "preventiva",
            "objetivo_visita": "Revisar o equipamento",
            "responsavel_comercial": "Bruna",
            "responsavel_tecnico": "Caio",
            "participantes": [
              {"nome": "Ana", "lado": "cliente", "funcao": "Compras"},
              {"nome": "Bruna", "lado": "empresa", "funcao": "Comercial"}
            ],
            "provided_details": [{"texto": "A visita durou cerca de uma hora."}],
            "next_steps": "Nenhum próximo passo definido",
            "follow_up_date": "Não haverá follow up",
            "elaborado_por": "Bruna"
          }
        }
      ],
      "expectations": [
        {
          "action": "generate",
          "state": "DONE_WITH_GAPS",
          "missing": ["topics_discussed"],
          "outputContains": ["## Descrição", "A visita durou cerca de uma hora", "Pendências de informação", "Assuntos discutidos"]
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Run the full harness**

Run: `python3 scripts/test_flow.py 2>&1 | tail -5`
Expected: `PASS` for all 39 cases and final line `All 39 conversational flow scenarios passed.`

- [ ] **Step 3: Commit**

```bash
git add tests/scenarios.json
git commit -m "test: migrate fixtures to the extended report contract"
```

---

### Task 5: Update public documentation and manifests

**Files:**
- Modify: `README.md:24-32` (field list), `README.md:103` (archive name)
- Modify: `INSTRUCOES_DE_USO.md` (sections 2 and 5)
- Modify: `docs/public-submission.md` (long description, P2/P3/P5, release notes)
- Modify: `plugin.json`, `.codex-plugin/plugin.json` (version, long description)
- Modify: `tests/chatgpt-acceptance.md` (baseline, start checklist, detailed fidelity scenario)

- [ ] **Step 1: Update README field list**

Replace:

```markdown
## Campos obrigatórios

- empresa (cliente);
- data da reunião ou visita;
- pessoa(s) de contato;
- tipo: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- assuntos discutidos;
- próximos passos, com responsável por cada ação; e
- data para follow up.
```

with:

```markdown
## Campos obrigatórios

- empresa (cliente);
- data da reunião ou visita;
- tipo: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- objetivo da visita;
- responsável comercial;
- responsável técnico (ou a declaração de que não houve);
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- assuntos discutidos;
- próximos passos, com responsável e prazo por cada ação;
- data para follow up; e
- elaborado por.
```

Replace the archive name:

```bash
dist/documentar-reuniao-0.3.8.zip → dist/documentar-reuniao-0.4.0.zip
```

- [ ] **Step 2: Update INSTRUCOES_DE_USO.md**

In section 2, replace the collection list:

```markdown
- empresa ou cliente;
- data da reunião ou visita;
- pessoas de contato;
- tipo da reunião ou visita: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- assuntos discutidos;
- próximos passos, com responsável e prazo de cada ação;
- data para follow up
```

with:

```markdown
- empresa ou cliente;
- data da reunião ou visita;
- objetivo da visita;
- responsável comercial e responsável técnico (ou a declaração de que não houve);
- participantes, com o lado (cliente ou empresa) e a função de cada um;
- tipo da reunião ou visita: `corretiva`, `preventiva`, `desenvolvimento` ou `negociação`;
- assuntos discutidos;
- próximos passos, com responsável e prazo de cada ação;
- data para follow up; e
- elaborado por.
```

In section 5, replace:

```markdown
- identificação da empresa, data, contatos e tipo da visita;
- assuntos discutidos;
- registro detalhado dos fatos fornecidos, reescrito em linguagem profissional sem inventar nenhuma informação;
- próximos passos, responsáveis e prazos;
- data para follow up.
```

with:

```markdown
- identificação da empresa, data, tipo, objetivo, responsáveis comercial e técnico, e data para follow up;
- participantes, com o lado e a função de cada um;
- descrição dos assuntos discutidos agrupada por assunto, reescrita em linguagem profissional sem inventar nenhuma informação;
- próximos passos, responsáveis e prazos; e
- linha de elaborado por.
```

- [ ] **Step 3: Update docs/public-submission.md**

Replace the long description:

```markdown
- Long description: Cole ou dite as anotações de uma reunião comercial. O workflow preserva os detalhes fornecidos, coleta somente os campos obrigatórios ausentes, confirma datas inferidas e gera um relatório estruturado e copiável.
```

with:

```markdown
- Long description: Cole ou dite as anotações de uma reunião comercial. O workflow coleta os campos obrigatórios — incluindo objetivo, responsáveis, participantes e elaborado por —, preserva os detalhes fornecidos, confirma datas inferidas e gera um relatório estruturado e copiável.
```

Replace the P2 prompt with:

```markdown
Prompt: `Empresa Acme. Visita em 15/09/2026. Tipo negociação. Objetivo: renovar o contrato. Responsável comercial: Bruno. Responsável técnico: Caio. Participantes: Ana (cliente, compras) e Bruno (empresa, comercial). Discutimos a renovação do contrato. Bruno enviará a proposta revisada. O follow up será em 18/09/2026. Elaborado por Bruno.`
```

Replace the P3 prompt with:

```markdown
Prompt: `Reunião com a empresa Beta em 15/09/2026. Participaram Carla (cliente, compras) e Bruno (empresa, comercial).`

Expected behavior: ask only for visit type, objective, commercial and technical representatives, topics, next steps with responsible people, follow-up date, and report author.

Expected result shape: one missing-field list; no report.
```

In P5, replace the prompt with:

```markdown
Prompt: `A visita da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Objetivo: alinhar o registro de reuniões no CRM. Responsável comercial: Bruno. Responsável técnico: Caio. Participantes: Luciano (cliente) e João (empresa). Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026. Elaborado por João.`
```

Replace the P5 expected behavior sentence:

```markdown
Expected behavior: request the missing valid visit type, confirm the interpreted relative date, then preserve every supplied fact and attribution.

Expected result shape: executive topics, `Registro detalhado`, owned next steps, and exactly one report-only copy block.
```

with:

```markdown
Expected behavior: request the missing valid visit type, confirm the interpreted relative date, then preserve every supplied fact and attribution.

Expected result shape: `Descrição` grouped by topic in professional prose, participants with side and function, owned next steps, and exactly one report-only copy block.
```

Replace the release notes with:

```markdown
Version 0.4.0 records the commercial representative, the technical representative, the visit objective, every participant with side and role, and the report author, and delivers the report under the heading `Relatório de Visita` with a single `Descrição` section grouping the facts by topic in professional prose; overridden drafts carry `Pendências de informação` inside the report.
```

- [ ] **Step 4: Update both manifests**

In `plugin.json` and `.codex-plugin/plugin.json`: replace `"version": "0.3.8"` with `"version": "0.4.0"` in both, and replace the `longDescription` value with:

```json
"Cole ou dite as anotações de uma reunião comercial. O workflow coleta os campos obrigatórios — incluindo objetivo, responsáveis, participantes e elaborado por —, preserva os detalhes fornecidos, confirma datas inferidas, pergunta somente o que faltar e gera um relatório estruturado."
```

Apply the identical value in both files (the harness asserts they agree).

- [ ] **Step 5: Update tests/chatgpt-acceptance.md**

Build section: replace all four version references `0.3.8` with `0.4.0` (`Plugin version`, `Installed-cache verification`, `Auxiliary Codex loading`, procedure sentence).

Replace the Start checklist expectation sentence (the one referencing "the seven required categories") with:

```markdown
Expected: the response lists the eleven required collection categories.
```

In the scenario `### Detailed-note fidelity and copy boundary`, replace the `Expected:` paragraph with:

```markdown
Expected: a `Descrição` section grouping the supplied facts under their topics as professional prose, the `Participantes` list with side and function, the extended header with objective and both representatives, and the `Elaborado por` signature. Every supplied fact is preserved without invention; reproducing dictated sentences near-verbatim records `Failed`. The entire message must be exactly the rendered report beginning with `# Relatório de Visita`: no status, no guidance, no code fences. The message copy button copies only the report. The next-steps table must include the `Prazo` column with a calendar date per action. A draft report carries `Pendências de informação` inside the report.
```

Leave every historical versioned record untouched.

- [ ] **Step 6: Run the full harness**

Run: `python3 scripts/test_flow.py 2>&1 | tail -3`
Expected: `All 39 conversational flow scenarios passed.`

- [ ] **Step 7: Commit**

```bash
git add README.md INSTRUCOES_DE_USO.md docs/public-submission.md plugin.json .codex-plugin/plugin.json tests/chatgpt-acceptance.md
git commit -m "docs: document extended report contract for 0.4.0"
```

---

### Task 6: Build, verify, and confidentiality check

**Files:**
- Create: `dist/documentar-reuniao-0.4.0.zip` (generated, gitignored)

- [ ] **Step 1: Build the public archive**

Run: `./scripts/build_public_zip.sh 2>&1 | tail -3`
Expected: `No errors detected in compressed data of .../dist/documentar-reuniao-0.4.0.zip.` followed by the archive path.

- [ ] **Step 2: Verify archive contents and new contract markers**

```bash
unzip -Z1 dist/documentar-reuniao-0.4.0.zip
unzip -p dist/documentar-reuniao-0.4.0.zip plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.4.0"'
unzip -p dist/documentar-reuniao-0.4.0.zip skills/relatorio-reuniao/SKILL.md | python3 -c 'import sys; t = sys.stdin.read(); assert "# Relatório de Visita" in t; assert "objetivo_visita" in t; assert "participantes" in t; assert "elaborado_por" in t; assert "Não houve responsável técnico" in t; print("archive contract verified")'
```

Expected: the four approved archive members and `archive contract verified`.

- [ ] **Step 3: Confidentiality check over the entire local history**

Run the confidential keyword sweep with the leak-vector keyword list supplied by the maintainer at execution time — the keyword list must never be stored in this repository. The command shape is:

```bash
if git grep -i -E "<confidential keyword list>" $(git rev-list --all) -- . 2>/dev/null; then echo "LEAK PRESENT"; else echo "history clean"; fi
```

Expected: `history clean` (the grep must find nothing; `Luciano` is a pre-existing public fixture name, not part of this check). Also run the same pattern as a working-tree sweep excluding `.git`, `dist`, and `__pycache__`.

If ANY leak is found: STOP, do not modify anything, and report BLOCKED with the exact file, commit, and line.

- [ ] **Step 4: Final commit of any remaining changes**

```bash
git status --short
git add -A
git commit -m "chore: prepare version 0.4.0" --allow-empty
git log --oneline -6
```

---

## Verification Summary

- `python3 scripts/test_flow.py` → `All 39 conversational flow scenarios passed.`
- `./scripts/build_public_zip.sh` → `dist/documentar-reuniao-0.4.0.zip` with integrity check.
- Zip contains only `plugin.json`, `assets/logo.png`, `skills/relatorio-reuniao/SKILL.md`, `skills/relatorio-reuniao/agents/openai.yaml`.
- Full-history grep for production-report terms returns nothing.
- ChatGPT Work acceptance (manual, post-build): run the `0.4.0` scenarios in `tests/chatgpt-acceptance.md`, starting with `começar` listing eleven categories.
