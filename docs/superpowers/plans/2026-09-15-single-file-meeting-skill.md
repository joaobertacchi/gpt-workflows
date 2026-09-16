# Single-File Meeting Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ChatGPT execute the complete meeting-report contract from `SKILL.md` without depending on supporting runtime files.

**Architecture:** Move intake, schema, validation rules, workflow, report template, and delivery guidance into marked sections of `skills/relatorio-reuniao/SKILL.md`. Keep `agents/openai.yaml` only for discovery metadata, teach the deterministic harness to read the marked sections, and remove runtime `assets/` and `references/`.

**Tech Stack:** Agent Skills Markdown, OpenAI skill metadata YAML, Agent Plugins manifests JSON, Python 3 standard library tests.

---

## File Map

- Modify: `skills/relatorio-reuniao/SKILL.md` - sole runtime workflow contract.
- Modify: `scripts/test_flow.py` - extract and validate marked sections in `SKILL.md`.
- Modify: `tests/scenarios.json` - retain behavioral fixtures; add single-file intake assertions if needed.
- Delete: `skills/relatorio-reuniao/assets/` - no runtime asset dependency.
- Delete: `skills/relatorio-reuniao/references/` - no runtime reference dependency.
- Modify: `plugin.json` - version `0.3.0`.
- Modify: `.codex-plugin/plugin.json` - version `0.3.0`.
- Modify: `README.md` - document the single-file runtime layout.
- Modify: `tests/chatgpt-acceptance.md` - record version and preserve failed attempts.

## Task 1: Specify The Embedded Contract

**Files:**
- Modify: `scripts/test_flow.py`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add a failing marked-section check**

Add these helpers after `load_json`:

```python
SKILL_PATH = SKILL_ROOT / "SKILL.md"


def load_skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def extract_skill_section(name: str) -> str:
    text = load_skill_text()
    start = f"<!-- {name}_START -->"
    end = f"<!-- {name}_END -->"
    if start not in text or end not in text:
        raise AssertionError(f"SKILL.md is missing marked section: {name}")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def load_embedded_json(name: str) -> dict[str, Any]:
    section = extract_skill_section(name)
    if section.startswith("```json") and section.endswith("```"):
        section = section[len("```json") : -len("```")].strip()
    return json.loads(section)
```

In `check_packaging`, require these sections:

```python
for section in (
    "INTAKE",
    "FIELD_SCHEMA",
    "VALIDATION_RULES",
    "REPORT_TEMPLATE",
    "COMPLETE_GUIDANCE",
    "INCOMPLETE_GUIDANCE",
):
    extract_skill_section(section)
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL with `SKILL.md is missing marked section: INTAKE`.

- [ ] **Step 3: Do not commit**

The user explicitly requested no commits. Leave the tested RED change in the working tree.

## Task 2: Make SKILL.md The Runtime Source

**Files:**
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Modify: `scripts/test_flow.py`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Replace SKILL.md with the complete inline contract**

Use this structure and literal runtime content:

````markdown
---
name: relatorio-reuniao
description: Use when the user selects @Documentar Reunião, invokes relatorio-reuniao, or asks to documentar, registrar or gerar relatório de reunião or visita comercial from text or voice notes.
---

# Documentar Reunião

Create one structured commercial meeting or visit report from facts supplied by the user. Ask only for unresolved required information. Never invent business facts or request fields outside this contract.

## Activation

Selecting `Documentar Reunião`, invoking `$relatorio-reuniao`, or making a matching explicit request starts a new active report. Text after activation is the first payload.

If the payload is empty or only `começar`, `iniciar`, or `start`, respond with exactly the intake below and stop. Do not paraphrase it or add fields.

<!-- INTAKE_START -->
Vamos montar o relatório da reunião/visita.

Você pode falar naturalmente, usar a entrada de voz ou colar suas anotações — não precisa seguir uma ordem. Inclua:

- empresa (cliente);
- data da reunião/visita;
- pessoa(s) de contato;
- tipo de reunião/visita: corretiva, preventiva, desenvolvimento ou negociação;
- assuntos discutidos;
- próximos passos, com o responsável por cada ação;
- data para follow up.

Depois eu verifico o que estiver faltando e pergunto somente pelos campos ausentes. Se preferir gerar o relatório mesmo com informações pendentes, diga explicitamente: “continuar mesmo assim”.

Se você usar datas relativas, como “ontem” ou “sexta que vem”, eu mostrarei as datas interpretadas para sua confirmação.
<!-- INTAKE_END -->

## Required Record

Only these seven fields are required. Time, duration, objective, decisions, success criteria, and unrelated deadlines are not required and must not be requested.

<!-- FIELD_SCHEMA_START -->
```json
{
  "missingValue": "Não informado",
  "fields": [
    {"id":"company","label":"Empresa (cliente)","required":true,"type":"string","validation":{"kind":"non_empty"}},
    {"id":"meeting_date","label":"Data da reunião/visita","required":true,"type":"string","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}},
    {"id":"contacts","label":"Pessoa(s) de contato","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"visit_type","label":"Tipo de reunião/visita","required":true,"type":"string","allowedValues":["corretiva","preventiva","desenvolvimento","negociação"],"validation":{"kind":"enum","caseInsensitive":true}},
    {"id":"topics_discussed","label":"Assuntos discutidos","required":true,"type":"array<string>","validation":{"kind":"non_empty_list"}},
    {"id":"next_steps","label":"Próximos passos","required":true,"type":"array<object>","itemFields":["action","responsible"],"itemFieldTypes":{"action":"string","responsible":"string"},"allowExplicitNone":true,"explicitNoneValue":"Nenhum próximo passo definido","validation":{"kind":"non_empty_list"}},
    {"id":"follow_up_date","label":"Data para follow up","required":true,"type":"string","allowExplicitNone":true,"explicitNoneValue":"Não haverá follow up","validation":{"kind":"absolute_date","formats":["YYYY-MM-DD","DD/MM/YYYY"]}}
  ]
}
```
<!-- FIELD_SCHEMA_END -->

<!-- VALIDATION_RULES_START -->
```json
{
  "missingSentinels":["não informado","nao informado","não sei","nao sei","desconhecido","unknown","n/a","não disponível","nao disponivel","omitido"],
  "explicitOverridePhrases":["continuar mesmo assim","continuar com pendências","continuar com pendencias","gerar mesmo com pendências","gerar mesmo com pendencias","pode gerar mesmo faltando","proceed anyway","continue anyway","generate anyway"],
  "explicitNegativeAnswers":{"next_steps":["não existem próximos passos","não há próximos passos","nenhum próximo passo"],"follow_up_date":["não haverá follow up","não será feito follow up","sem follow up"]}
}
```
<!-- VALIDATION_RULES_END -->

## Workflow

1. Extract only user-provided facts into the active record. Merge later answers. A clear correction replaces the prior value; an ambiguous conflict triggers one question about only that field.
2. Validate all seven fields after every turn. Ask one concise question containing only missing, invalid, conflicting, or unconfirmed required labels.
3. Accept `visit_type` only as `corretiva`, `preventiva`, `desenvolvimento`, or `negociação` after normalization.
4. Require every next-step action to have a responsible person. A direct statement that no next steps exist becomes `Nenhum próximo passo definido`.
5. A direct statement that no follow up will occur becomes `Não haverá follow up`. Negative answers complete no other field.
6. Resolve relative meeting and follow-up dates from the conversation date. Show every calendar date and wait for confirmation or correction.
7. Generate immediately when all fields are valid and inferred dates are confirmed. Do not ask for permission.
8. Generate with gaps only after affirmative use of a configured override phrase. Quoted, hypothetical, ambiguous, or negated mentions are not overrides.
9. A correction after generation reopens validation and regenerates without repeating intake.

## Report Output

Render this template in order. Render contacts as comma-separated names, topics as bullets, and action-based next steps as a table with `Ação` and `Responsável` columns.

<!-- REPORT_TEMPLATE_START -->
# Relatório de reunião/visita

**Empresa (cliente):** {{company}}  
**Data da reunião/visita:** {{meeting_date}}  
**Pessoa(s) de contato:** {{contacts}}  
**Tipo de reunião/visita:** {{visit_type}}  
**Data para follow up:** {{follow_up_date}}

## Assuntos discutidos

{{topics_discussed}}

## Próximos passos

{{next_steps}}
<!-- REPORT_TEMPLATE_END -->

For a complete report, announce and append this guidance. Do not include a pending section or missing placeholder.

<!-- COMPLETE_GUIDANCE_START -->
✅ **Todas as informações necessárias foram preenchidas.**

O relatório está pronto para ser revisado e compartilhado. Revise nomes, datas e responsáveis; depois, copie o conteúdo do relatório para um e-mail, WhatsApp, CRM ou registro interno.
<!-- COMPLETE_GUIDANCE_END -->

For an overridden report, use `Não informado` for every unresolved field, append `## Pendências de informação` with every unresolved label, and include this guidance:

<!-- INCOMPLETE_GUIDANCE_START -->
⚠️ **O relatório foi gerado como rascunho com informações pendentes.**

O rascunho deve ser completado e revisado antes de ser compartilhado como versão final. O plugin não envia mensagens nem grava o relatório em outros sistemas.
<!-- INCOMPLETE_GUIDANCE_END -->

## Common Mistakes

- Do not replace the intake with a generic meeting questionnaire.
- Do not request time, duration, decisions, success criteria, or unrelated deadlines.
- Do not preserve a relative date as final without confirmation.
- Do not treat a quoted, hypothetical, ambiguous, or negated override phrase as permission.
- Do not show `Pendências de informação` in a complete report.

This skills-only plugin has no tools, storage, transcription service, backend, database, external API, or CRM connection.
````

- [ ] **Step 2: Point the harness at embedded JSON**

Replace the global resource loads with:

```python
FIELD_SCHEMA = load_embedded_json("FIELD_SCHEMA")
VALIDATION_RULES = load_embedded_json("VALIDATION_RULES")
```

Replace `render_intake` with:

```python
def render_intake() -> str:
    return extract_skill_section("INTAKE")
```

Replace the template read in `render_report` with:

```python
template = extract_skill_section("REPORT_TEMPLATE")
```

Replace `render_delivery_guidance` with:

```python
def render_delivery_guidance(incomplete: bool) -> str:
    section = "INCOMPLETE_GUIDANCE" if incomplete else "COMPLETE_GUIDANCE"
    return extract_skill_section(section)
```

Remove `load_skill_json` because no runtime JSON file remains.

- [ ] **Step 3: Point static checks at SKILL.md**

In `check_packaging`, remove runtime asset/reference paths from `required_paths`. Replace separate intake, template, guidance, and validation-rule reads with `extract_skill_section(...)` and `load_embedded_json(...)`.

Keep exact checks for all seven intake labels, every report placeholder, delivery phrases, invocation metadata, and required validation semantics.

- [ ] **Step 4: Run the harness and verify GREEN before deletion**

Run: `python3 scripts/test_flow.py`

Expected: all 29 conversational flow scenarios pass while both old resource directories still exist.

- [ ] **Step 5: Do not commit**

The user explicitly requested no commits.

## Task 3: Remove Runtime Resource Dependencies

**Files:**
- Modify: `scripts/test_flow.py`
- Delete: `skills/relatorio-reuniao/assets/intake-message.md`
- Delete: `skills/relatorio-reuniao/assets/meeting-report-template.md`
- Delete: `skills/relatorio-reuniao/assets/report-delivery-guidance.md`
- Delete: `skills/relatorio-reuniao/references/workflow.md`
- Delete: `skills/relatorio-reuniao/references/field-schema.json`
- Delete: `skills/relatorio-reuniao/references/validation-rules.json`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add a failing single-runtime-file check**

Replace the old root-only duplicate check with:

```python
for obsolete in (
    ROOT / "assets",
    ROOT / "references",
    SKILL_ROOT / "assets",
    SKILL_ROOT / "references",
):
    if obsolete.exists():
        raise AssertionError(
            "runtime contract must live only in SKILL.md: "
            + str(obsolete.relative_to(ROOT))
        )
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because `skills/relatorio-reuniao/assets` still exists.

- [ ] **Step 3: Delete the six obsolete runtime resource files**

Delete exactly the files listed in this task, then remove the empty `assets/` and `references/` directories. Do not remove root tests, scripts, specs, or plans.

- [ ] **Step 4: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all 29 scenarios pass and no runtime-resource directory error appears.

- [ ] **Step 5: Do not commit**

The user explicitly requested no commits.

## Task 4: Align Package Metadata And Documentation

**Files:**
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `README.md`
- Modify: `tests/chatgpt-acceptance.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add a failing exact-version check**

In `check_packaging`, after comparing manifest versions, add:

```python
if portable_manifest["version"] != "0.3.0":
    raise AssertionError("single-file runtime must ship as version 0.3.0")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because the manifests still declare `0.2.2`.

- [ ] **Step 3: Set version 0.3.0 in both manifests**

Change only the `version` value in `plugin.json` and `.codex-plugin/plugin.json` to `0.3.0`. Preserve names, descriptions, prompts, and interface metadata.

- [ ] **Step 4: Update README structure and ownership**

Replace the skill subtree with:

```text
skills/
└── relatorio-reuniao/
    ├── SKILL.md
    └── agents/
        └── openai.yaml
```

State that `SKILL.md` contains the complete runtime contract and that `tests/` and `scripts/` are development-only. Remove customization rows for deleted resources and map intake, fields, validation, workflow, and output to `SKILL.md`.

- [ ] **Step 5: Update the acceptance build version**

Set `Plugin version` and the procedure version in `tests/chatgpt-acceptance.md` to `0.3.0`. Preserve all failed `0.2.x` evidence.

- [ ] **Step 6: Run source verification**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); YAML.safe_load_file("skills/relatorio-reuniao/SKILL.md", aliases: false); puts "Skill and YAML OK"'
```

Expected: 29/29 scenarios pass, JSON commands exit 0, and output includes `Skill and YAML OK`.

- [ ] **Step 7: Do not commit**

The user explicitly requested no commits.

## Task 5: Install And Gate ChatGPT Acceptance

**Files:**
- Modify only after observed results: `tests/chatgpt-acceptance.md`
- Verify: `~/.codex/plugins/cache/personal/gpt-workflows/0.3.0/`

- [ ] **Step 1: Reinstall the CLI copy**

Run:

```bash
codex plugin remove gpt-workflows@personal
codex plugin add gpt-workflows@personal
```

Expected: installed root ends in `gpt-workflows/0.3.0`.

- [ ] **Step 2: Verify installed identity**

Run:

```bash
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.0
```

Expected: no output and exit code 0.

- [ ] **Step 3: Reinstall through ChatGPT**

In the ChatGPT Plugins Directory, remove the current plugin, refresh the `Personal` source, install version `0.3.0`, quit the app completely, and reopen it.

- [ ] **Step 4: Run only the intake gate**

In a new conversation, select the real **Documentar Reunião** entry from the `@` menu and send `começar`.

Expected: the response begins `Vamos montar o relatório da reunião/visita.`, contains exactly the seven categories from the marked intake, and does not request time, duration, decisions, success criteria, or unrelated deadlines.

- [ ] **Step 5: Stop on intake failure**

If the intake gate fails, record the exact response and version in `tests/chatgpt-acceptance.md`. Do not run the remaining scenarios or make another code change without a new root-cause investigation.

- [ ] **Step 6: Continue acceptance only after intake passes**

Run complete-first-turn, missing-field, relative-date, explicit-none, and incomplete-override scenarios from `tests/chatgpt-acceptance.md`. Record `Passed` only with a conversation identifier, transcript, or screenshot.

- [ ] **Step 7: Run final verification**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); YAML.safe_load_file("skills/relatorio-reuniao/SKILL.md", aliases: false); puts "Skill and YAML OK"'
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.0
git status --short
```

Expected: all 29 scenarios pass, syntax checks exit 0, cache diff is empty, and Git shows only intended uncommitted project files.

- [ ] **Step 8: Do not commit**

The user explicitly requested no commits.
