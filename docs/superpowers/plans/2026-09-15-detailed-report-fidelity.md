# Detailed Report Fidelity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve all relevant user-supplied meeting facts in a structured detailed section and isolate each generated report in one copyable Markdown block.

**Architecture:** Keep the seven required fields unchanged and add one optional `provided_details` fact collection to the single-file runtime contract. Render that collection conditionally between the topic summary and next steps, then wrap only the report in one terminal Markdown fence while keeping operational guidance before it.

**Tech Stack:** Agent Skills Markdown, Python 3 standard library harness, JSON fixtures and manifests, ChatGPT Work manual acceptance.

---

## File Map

- Modify: `skills/relatorio-reuniao/SKILL.md` - optional detail contract, conditional section, and copy boundary.
- Modify: `scripts/test_flow.py` - optional detail rendering and generated-response boundary assertions.
- Modify: `tests/scenarios.json` - rich, minimal, incomplete, and corrected detail fixtures.
- Modify: `tests/chatgpt-acceptance.md` - fidelity and copy-boundary acceptance evidence.
- Modify: `plugin.json` - patch version `0.3.2`.
- Modify: `.codex-plugin/plugin.json` - patch version `0.3.2`.

## Task 1: Preserve Supplied Details

**Files:**
- Modify: `tests/scenarios.json`
- Modify: `scripts/test_flow.py`
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add the rich complete fixture**

Append this case before the closing case-array bracket in `tests/scenarios.json`:

```json
{
  "id": "rich-notes-preserve-all-relevant-details",
  "invoked": true,
  "turns": [
    {
      "text": "A reunião da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-13",
        "contacts": ["Luciano"],
        "visit_type": "desenvolvimento",
        "topics_discussed": ["Adoção do registro de reuniões no CRM", "Alternativas ao WhatsApp", "Plugin público para ChatGPT"],
        "provided_details": [
          "A reunião ocorreu às 13h e durou aproximadamente uma hora.",
          "Luciano relatou que o time de vendas deveria registrar reuniões com clientes, mas não vem fazendo isso de forma consistente.",
          "Os registros das reuniões deveriam estar entrando no CRM.",
          "Durante a conversa, Luciano avaliou uma solução baseada em WhatsApp e pediu alternativas melhores.",
          "Foi proposto um plugin público para ChatGPT que Luciano e o time dele poderão instalar.",
          "Os requisitos foram recebidos na segunda-feira, antes da preparação da prova de conceito.",
          "O teste será realizado em dispositivos móveis."
        ],
        "next_steps": [
          {"action": "Preparar e enviar a prova de conceito até o fim do dia", "responsible": "eu"},
          {"action": "Instalar, testar em dispositivos móveis e enviar retorno até 17/09/2026", "responsible": "Luciano"}
        ],
        "follow_up_date": "2026-09-17"
      }
    }
  ],
  "expectations": [
    {
      "action": "generate",
      "state": "DONE",
      "missing": [],
      "outputContains": ["Registro detalhado", "13h", "aproximadamente uma hora", "Luciano relatou", "CRM", "WhatsApp", "plugin público", "segunda-feira", "dispositivos móveis", "fim do dia", "17/09/2026"]
    }
  ]
}
```

- [ ] **Step 2: Extend existing fixtures for omission, override, and correction**

In `complete-on-first-turn`, add `"outputNotContains": ["Registro detalhado"]` to its generated expectation.

In `explicit-override-generates-with-gaps`, add this extracted field:

```json
"provided_details": ["Diego explicou que a solução atual exige retrabalho manual."]
```

Add `"Registro detalhado"` and `"retrabalho manual"` to that case's `outputContains` list.

In the first turn of `correction-after-generation-regenerates-report`, add:

```json
"provided_details": ["Ana relatou que o processo era manual."]
```

In its correction turn, use:

```json
"fields": {
  "topics_discussed": ["Renovação"],
  "provided_details": ["Ana esclareceu que o processo já era automatizado."]
}
```

Require the second output to contain `"processo já era automatizado"` and not contain `"processo era manual"`.

- [ ] **Step 3: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: the rich, override, and correction expectations fail because `provided_details` is not rendered.

- [ ] **Step 4: Add the optional field to the embedded schema**

In `FIELD_SCHEMA`, add this non-required field after `topics_discussed`:

```json
{"id":"provided_details","label":"Detalhes fornecidos","required":false,"type":"array<string>","validation":{"kind":"non_empty_list"}}
```

Keep the prose statement that only the original seven fields are required. State explicitly that `provided_details` must never be requested when absent.

- [ ] **Step 5: Add the fidelity contract to the workflow**

Add these rules to `SKILL.md`:

```markdown
- Preserve every relevant user-supplied fact. Store context and specificity behind topic labels in `provided_details`; a concise topic does not replace its supporting facts.
- Relevant supplied facts include context, chronology, problems, evidence, current processes, alternatives, decisions, restrictions, channels, deadlines, times, durations and expectations.
- Improve grammar and remove repetition or speech disfluencies, but preserve names, attribution, dates, times, quantities, relationships and temporal order. Never replace distinct facts with a lossy generalization or invent an interpretation.
- Do not ask for `provided_details`. When absent, continue using only the seven required fields.
- A correction replaces affected detail facts while preserving unrelated facts.
```

- [ ] **Step 6: Add conditional detail rendering**

Insert `{{provided_details_section}}` between `{{topics_discussed}}` and `## Próximos passos` in `REPORT_TEMPLATE`.

In `render_report`, build the replacement:

```python
provided_details = record.get("provided_details")
provided_details_section = ""
if isinstance(provided_details, list) and provided_details:
    rendered_details = "\n".join(f"- {item}" for item in provided_details)
    provided_details_section = f"\n\n## Registro detalhado\n\n{rendered_details}"
```

Add it to `values`:

```python
"provided_details_section": provided_details_section,
```

Add `"{{provided_details_section}}"` to `required_placeholders` in `check_packaging`.

- [ ] **Step 7: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all scenarios, including the new rich case, pass; the scenario total increases from 29 to 30.

- [ ] **Step 8: Do not commit**

The user explicitly requested no commits.

## Task 2: Enforce The Copy Boundary

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add a generated-output boundary assertion**

Add this helper after `render_report`:

```python
def assert_copy_boundary(output: str) -> None:
    if output.count("```markdown") != 1 or output.count("```") != 2:
        raise AssertionError("generated response must contain exactly one Markdown fence")
    opening = output.index("```markdown")
    closing = output.index("```", opening + len("```markdown"))
    if not output[:opening].strip():
        raise AssertionError("delivery guidance must precede the report block")
    report = output[opening + len("```markdown") : closing].strip()
    if not report.startswith("# Relatório de reunião/visita"):
        raise AssertionError("only the report may occupy the Markdown fence")
    operational_phrases = (
        "Todas as informações necessárias foram preenchidas",
        "O relatório está pronto para ser revisado e compartilhado",
        "O relatório foi gerado como rascunho com informações pendentes",
        "O rascunho deve ser completado e revisado",
    )
    if any(phrase in report for phrase in operational_phrases):
        raise AssertionError("operational guidance must remain outside the report block")
    if output[closing + len("```") :].strip():
        raise AssertionError("nothing may follow the report block")
```

In `main`, immediately after `actual = simulate(case)`, validate every generated response:

```python
try:
    for turn in actual:
        if turn["action"] == "generate":
            assert_copy_boundary(turn["output"])
except AssertionError as error:
    failures.append(f"{case['id']}: {error}")
    continue
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: generated scenarios fail with `generated response must contain exactly one Markdown fence`.

- [ ] **Step 3: Wrap only the report**

Replace the final return in `render_report` with:

```python
guidance = render_delivery_guidance(bool(missing))
return f"{guidance}\n\n```markdown\n{template.strip()}\n```"
```

- [ ] **Step 4: Make the boundary mandatory in the skill**

Add this instruction immediately before `REPORT_TEMPLATE`:

```markdown
For every complete, overridden or regenerated report, place status and operational guidance before exactly one fenced `markdown` block. Put only the report inside that block and emit nothing after its closing fence. `Pendências de informação`, when applicable, belongs inside the report block.
```

Change the complete and incomplete guidance prose so both explicitly precede the report instead of being appended to it.

- [ ] **Step 5: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all 30 scenarios pass and every generated output satisfies the copy-boundary assertion.

- [ ] **Step 6: Do not commit**

The user explicitly requested no commits.

## Task 3: Release And Acceptance

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `tests/chatgpt-acceptance.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Make the release assertion fail**

Change the exact version assertion to:

```python
if portable_manifest["version"] != "0.3.2":
    raise AssertionError("detailed-report fidelity must ship as version 0.3.2")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because the manifests still declare `0.3.1`.

- [ ] **Step 3: Update both manifests**

Set `version` to `0.3.2` in `plugin.json` and `.codex-plugin/plugin.json`. Preserve all other metadata.

- [ ] **Step 4: Prepare acceptance documentation**

Set the build and procedure versions in `tests/chatgpt-acceptance.md` to `0.3.2`. Preserve all prior `0.3.0` and `0.3.1` evidence in historical sections. Add these pending rows:

```markdown
| Detailed-note fidelity | Pending | Verify every relevant fact from the rich Work prompt appears without invention. |
| Copyable report boundary | Pending | Verify one Markdown copy block contains only the report and nothing follows it. |
```

Document the exact rich prompt from the Task 1 fixture as the manual procedure.

- [ ] **Step 5: Run package verification**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); YAML.safe_load_file("skills/relatorio-reuniao/SKILL.md", aliases: false); puts "Structured files OK"'
git diff --check
```

Expected: 30/30 scenarios pass, structured files are valid, and `git diff --check` exits 0.

- [ ] **Step 6: Refresh and compare the local package**

Run:

```bash
codex plugin remove gpt-workflows@personal
codex plugin add gpt-workflows@personal
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.2
```

Expected: installed root ends in `0.3.2`; diff produces no output.

- [ ] **Step 7: Execute ChatGPT Work acceptance**

Install `0.3.2`, restart ChatGPT, open a new Work conversation, select **Documentar Reunião**, and submit the exact rich prompt from Task 1. Record evidence only if every supplied fact is present, no unsupported fact appears, the topic summary remains readable, attribution and chronology remain intact, and the copy button copies only the report.

- [ ] **Step 8: Final verification**

After recording acceptance evidence, refresh the local package again and run:

```bash
python3 scripts/test_flow.py
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.2
git diff --check
git status --short
```

Expected: 30/30 scenarios pass, cache diff and whitespace checks are empty, and Git shows only intended uncommitted files.

- [ ] **Step 9: Do not commit**

The user explicitly requested no commits.
