# Partial Collection Stability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make partial meeting inputs consistently produce a question containing only unresolved required fields in ChatGPT Work.

**Architecture:** Add one marked, literal partial-collection example to the single-file `SKILL.md` contract and verify its exact content from the deterministic harness. Release the instruction-only change as `0.3.1` and require three consecutive Work passes for the same Beta prompt.

**Tech Stack:** Agent Skills Markdown, Python 3 standard library tests, Agent Plugins JSON manifests, ChatGPT Work manual acceptance.

---

## File Map

- Modify: `skills/relatorio-reuniao/SKILL.md` - mandatory partial-collection format and example.
- Modify: `scripts/test_flow.py` - marked-section and exact-content checks.
- Modify: `plugin.json` - version `0.3.1`.
- Modify: `.codex-plugin/plugin.json` - version `0.3.1`.
- Modify: `tests/chatgpt-acceptance.md` - three-run stability record.

## Task 1: Add The Partial-Collection Contract

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add a failing section requirement**

Add `"PARTIAL_EXAMPLE"` to the marked-section tuple in `check_packaging`:

```python
for section in (
    "INTAKE",
    "FIELD_SCHEMA",
    "VALIDATION_RULES",
    "PARTIAL_EXAMPLE",
    "REPORT_TEMPLATE",
    "COMPLETE_GUIDANCE",
    "INCOMPLETE_GUIDANCE",
):
    extract_skill_section(section)
```

After extracting the intake, validate the example:

```python
partial_example = extract_skill_section("PARTIAL_EXAMPLE")
required_partial_content = (
    "Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.",
    "Tipo de reunião/visita",
    "Assuntos discutidos",
    "Próximos passos, com responsável por cada ação",
    "Data para follow up",
    "Do not ask for generic notes",
    "Do not request decisions",
)
missing_partial_content = [
    phrase for phrase in required_partial_content if phrase not in partial_example
]
if missing_partial_content:
    raise AssertionError(
        "partial example is missing required content: "
        + ", ".join(missing_partial_content)
    )
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL with `SKILL.md must contain one marked section: PARTIAL_EXAMPLE`.

- [ ] **Step 3: Add the mandatory response format and example**

Insert this section after the numbered workflow and before `## Report Output`:

```markdown
## Missing-Field Response

When validation finds unresolved fields, enumerate every unresolved required label and no completed or optional field. Do not ask for generic notes or say only “tell me the rest.” Do not request decisions, time, duration, objectives, success criteria, or unrelated deadlines.

<!-- PARTIAL_EXAMPLE_START -->
User:

`Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.`

Required response:

Para completar o relatório, informe:

- Tipo de reunião/visita;
- Assuntos discutidos;
- Próximos passos, com responsável por cada ação;
- Data para follow up.

Do not ask for generic notes. Do not request decisions. Do not repeat Empresa, Data da reunião/visita, or Pessoa(s) de contato because the user already supplied them.
<!-- PARTIAL_EXAMPLE_END -->
```

- [ ] **Step 4: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all 29 conversational flow scenarios pass.

- [ ] **Step 5: Do not commit**

The user explicitly requested no commits.

## Task 2: Package Version 0.3.1

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `tests/chatgpt-acceptance.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Change the exact-version assertion to create RED**

Replace the version assertion with:

```python
if portable_manifest["version"] != "0.3.1":
    raise AssertionError("partial-collection stability must ship as version 0.3.1")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because both manifests still declare `0.3.0`.

- [ ] **Step 3: Update both manifests**

Set `version` to `0.3.1` in `plugin.json` and `.codex-plugin/plugin.json`. Preserve all other metadata.

- [ ] **Step 4: Prepare the acceptance record**

Set the build and procedure versions to `0.3.1`. Change the current `Missing-field follow-up` row to:

```markdown
| Missing-field follow-up | Pending | Stability gate: 0/3 consecutive Work passes on 0.3.1. |
```

Under historical evidence, retain both `0.3.0` outcomes: one generic invalid response and one correct response for the same Beta prompt.

- [ ] **Step 5: Run package verification**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); YAML.safe_load_file("skills/relatorio-reuniao/SKILL.md", aliases: false); puts "Skill and YAML OK"'
```

Expected: 29/29 scenarios pass, JSON commands exit 0, and output includes `Skill and YAML OK`.

- [ ] **Step 6: Do not commit**

The user explicitly requested no commits.

## Task 3: Install And Run The Stability Gate

**Files:**
- Modify after each observed run: `tests/chatgpt-acceptance.md`
- Verify: `~/.codex/plugins/cache/personal/gpt-workflows/0.3.1/`

- [ ] **Step 1: Refresh the local package**

Run:

```bash
codex plugin remove gpt-workflows@personal
codex plugin add gpt-workflows@personal
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.1
```

Expected: installed root ends in `0.3.1`; diff produces no output.

- [ ] **Step 2: Install 0.3.1 through ChatGPT**

Remove the old version in the Personal Plugins Directory, refresh Personal, install `0.3.1`, quit ChatGPT completely, and reopen it.

- [ ] **Step 3: Run three isolated Work conversations**

In each new Work conversation, select **Documentar Reunião** and send exactly:

```text
Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.
```

Every response must request exactly visit type, topics, next steps with a responsible person, and follow-up date. It must not request company, meeting date, contact, generic notes, decisions, time, duration, objectives, success criteria, or unrelated deadlines.

- [ ] **Step 4: Record each result immediately**

After each run, update the evidence to `1/3`, `2/3`, or `3/3 consecutive Work passes`, with its screenshot or conversation reference. Any failure resets the count to `0/3` and remains recorded.

- [ ] **Step 5: Complete acceptance after the third pass**

Mark `Missing-field follow-up` as `Passed` only after `3/3`. Keep the other five scenarios passed based on their unchanged contracts and existing Work evidence.

- [ ] **Step 6: Run final verification**

Run:

```bash
python3 scripts/test_flow.py
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.1
git status --short
```

Expected: all 29 scenarios pass, cache diff is empty, and Git shows only intended uncommitted files.

- [ ] **Step 7: Do not commit**

The user explicitly requested no commits.
