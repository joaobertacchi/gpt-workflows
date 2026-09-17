# Report-Only Message Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver every generated meeting report as the entire chat message — rendered Markdown, no guidance, no fences — so the message copy button copies exactly the report.

**Architecture:** Replace the artifact-plus-fallback delivery with a single inline contract: `render_report` returns only the report string; the harness asserts every `generate` message starts with the report heading and contains no fences or operational phrases; SKILL.md drops the artifact paragraphs, the fenced fallback, and both guidance sections. Version bumps to `0.3.7`.

**Tech Stack:** Python 3 stdlib harness (`scripts/test_flow.py`), JSON fixtures (`tests/scenarios.json`), Markdown skill contract (`skills/relatorio-reuniao/SKILL.md`), POSIX packaging script.

**Spec:** `docs/superpowers/specs/2026-09-16-report-only-message-design.md`

---

### Task 1: Inline delivery contract in the harness

Switch the offline model to report-only messages: pure output, no artifact machinery, no fallback scenario.

**Files:**
- Modify: `scripts/test_flow.py` (assertion, `render_report`, `simulate`, `expectation_matches`, `main`)
- Modify: `tests/scenarios.json` (delete the artifact-fallback case)

- [ ] **Step 1: Replace the delivery assertion and its call site (failing)**

In `scripts/test_flow.py`, replace the whole `assert_report_delivery` function (lines 362-404):

```python
def assert_report_delivery(
    turn: dict[str, Any], artifact_supported: bool
) -> None:
    output = turn["output"]
    artifact_name = turn.get("artifactName")
    artifact_content = turn.get("artifactContent")
    operational_phrases = (
        "Todas as informações necessárias foram preenchidas",
        "O relatório está pronto para ser revisado e compartilhado",
        "O relatório foi gerado como rascunho com informações pendentes",
        "O rascunho deve ser completado e revisado",
    )

    if artifact_supported:
        if artifact_name != "relatorio-reuniao.md":
            raise AssertionError("report artifact must use the approved filename")
        if not artifact_content or not artifact_content.startswith(
            "# Relatório de reunião/visita"
        ):
            raise AssertionError("artifact must contain only the Markdown report")
        if "```" in output or "```" in artifact_content:
            raise AssertionError("artifact delivery must not use Markdown fences")
        if "# Relatório de reunião/visita" in output:
            raise AssertionError("artifact delivery must not duplicate the report inline")
        if any(phrase in artifact_content for phrase in operational_phrases):
            raise AssertionError("operational guidance must remain outside the artifact")
        return

    if artifact_name is not None or artifact_content is not None:
        raise AssertionError("unsupported surfaces must not expose an artifact")
    if output.count("```markdown") != 1 or output.count("```") != 2:
        raise AssertionError("fallback must contain exactly one Markdown fence")
    opening = output.index("```markdown")
    closing = output.index("```", opening + len("```markdown"))
    if not output[:opening].strip():
        raise AssertionError("delivery guidance must precede the fallback block")
    report = output[opening + len("```markdown") : closing].strip()
    if not report.startswith("# Relatório de reunião/visita"):
        raise AssertionError("only the report may occupy the fallback block")
    if any(phrase in report for phrase in operational_phrases):
        raise AssertionError("operational guidance must remain outside the fallback block")
    if output[closing + len("```") :].strip():
        raise AssertionError("nothing may follow the fallback block")
```

with:

```python
def assert_inline_report_delivery(turn: dict[str, Any]) -> None:
    output = turn["output"]
    operational_phrases = (
        "Todas as informações necessárias foram preenchidas",
        "O relatório está pronto para ser revisado e compartilhado",
        "O relatório foi gerado como rascunho com informações pendentes",
        "O rascunho deve ser completado e revisado",
    )
    if not output.startswith("# Relatório de reunião/visita"):
        raise AssertionError("the entire message must be exactly the report")
    if "```" in output:
        raise AssertionError("report message must not use Markdown fences")
    if any(phrase in output for phrase in operational_phrases):
        raise AssertionError("report message must not contain operational guidance")
```

and in `main()`, replace:

```python
                if turn["action"] == "generate":
                    assert_report_delivery(
                        turn, case.get("artifactSupported", True)
                    )
```

with:

```python
                if turn["action"] == "generate":
                    assert_inline_report_delivery(turn)
```

- [ ] **Step 2: Run harness to verify it fails**

Run: `python3 scripts/test_flow.py > /dev/null 2>&1; echo "exit=$?"`
Expected: `exit=1` — every case with a `generate` turn fails with `the entire message must be exactly the report` (current output is only the guidance text). Cases without `generate` turns still PASS.

- [ ] **Step 3: Make `render_report` return only the report**

In `scripts/test_flow.py`:

3a. Delete the `render_delivery_guidance` function (lines 259-261):

```python
def render_delivery_guidance(incomplete: bool) -> str:
    section = "INCOMPLETE_GUIDANCE" if incomplete else "COMPLETE_GUIDANCE"
    return extract_skill_section(section)
```

3b. Change the signature (line 301-303):

```python
def render_report(
    record: dict[str, Any], missing: list[str], artifact_supported: bool
) -> dict[str, Any]:
```

to:

```python
def render_report(record: dict[str, Any], missing: list[str]) -> str:
```

3c. Replace the return tail (lines 344-359):

```python
    if missing:
        pending = "\n".join(f"- {labels[field_id]}" for field_id in missing)
        template += f"\n\n## Pendências de informação\n\n{pending}\n"
    guidance = render_delivery_guidance(bool(missing))
    report = template.strip()
    if artifact_supported:
        return {
            "output": guidance,
            "artifactName": "relatorio-reuniao.md",
            "artifactContent": report,
        }
    return {
        "output": f"{guidance}\n\n```markdown\n{report}\n```",
        "artifactName": None,
        "artifactContent": None,
    }
```

with:

```python
    if missing:
        pending = "\n".join(f"- {labels[field_id]}" for field_id in missing)
        template += f"\n\n## Pendências de informação\n\n{pending}\n"
    return template.strip()
```

- [ ] **Step 4: Simplify `simulate` and `expectation_matches`**

In `scripts/test_flow.py`:

4a. Delete (line 472):

```python
    artifact_supported = case.get("artifactSupported", True)
```

4b. Replace (lines 522-525):

```python
        delivery: dict[str, Any] | None = None
        if action == "generate":
            delivery = render_report(record, missing, artifact_supported)
            output = delivery["output"]
```

with:

```python
        if action == "generate":
            output = render_report(record, missing)
```

4c. Replace (lines 537-543):

```python
        result = {"action": action, "state": state, "missing": missing, "output": output}
        if delivery is not None:
            result.update(
                artifactName=delivery["artifactName"],
                artifactContent=delivery["artifactContent"],
            )
        results.append(result)
```

with:

```python
        results.append(
            {"action": action, "state": state, "missing": missing, "output": output}
        )
```

4d. In `expectation_matches` (lines 417-426), replace:

```python
    searchable_output = "\n".join(
        value
        for value in (actual.get("output"), actual.get("artifactContent"))
        if value
    )
    return (
        all(actual.get(key) == value for key, value in core.items())
        and all(fragment in searchable_output for fragment in required)
        and all(fragment not in searchable_output for fragment in forbidden)
    )
```

with:

```python
    output = actual.get("output", "")
    return (
        all(actual.get(key) == value for key, value in core.items())
        and all(fragment in output for fragment in required)
        and all(fragment not in output for fragment in forbidden)
    )
```

- [ ] **Step 5: Delete the artifact-fallback scenario**

In `tests/scenarios.json`, delete the whole `artifact-unavailable-uses-markdown-fallback` case object, including its trailing comma — the object starting:

```json
    {
      "id": "artifact-unavailable-uses-markdown-fallback",
      "activation": "plugin_selected",
      "artifactSupported": false,
```

through the closing:

```json
      ]
    },
```

immediately before `    {` for `"next-step-deadline-asks-only-for-deadline"`. The `next_steps` item in that case contains `"deadline": "18/09/2026"` — the object is removed entirely.

Also in `tests/scenarios.json`, remove the guidance phrase from the `explicit-override-generates-with-gaps` expectation (line 132) — the warning phrase was part of the deleted `INCOMPLETE_GUIDANCE` and no longer appears in any message. Replace:

```json
          "outputContains": ["rascunho com informações pendentes", "Pendências de informação", "Próximos passos", "Data para follow up", "Registro detalhado", "retrabalho manual"]
```

with:

```json
          "outputContains": ["Pendências de informação", "Próximos passos", "Data para follow up", "Registro detalhado", "retrabalho manual"]
```

- [ ] **Step 6: Run harness to verify all cases pass**

Run: `python3 scripts/test_flow.py 2>&1 | tail -2`
Expected: `All 33 conversational flow scenarios passed.` (34 minus the deleted fallback case)

- [ ] **Step 7: Commit**

```bash
git add scripts/test_flow.py tests/scenarios.json
git commit -m "test: model report-only message delivery"
```

---

### Task 2: Report-only runtime contract

Rewrite the SKILL.md delivery paragraphs and align the packaging checks.

**Files:**
- Modify: `scripts/test_flow.py` (packaging checks)
- Modify: `skills/relatorio-reuniao/SKILL.md` (Report Output section)

- [ ] **Step 1: Update packaging checks first (failing)**

In `scripts/test_flow.py` `check_packaging`:

1. In the required-sections tuple (lines 548-557), delete:

```python
        "COMPLETE_GUIDANCE",
        "INCOMPLETE_GUIDANCE",
```

leaving:

```python
    for section in (
        "INTAKE",
        "FIELD_SCHEMA",
        "VALIDATION_RULES",
        "PARTIAL_EXAMPLE",
        "DETAIL_FIDELITY_EXAMPLE",
        "REPORT_TEMPLATE",
    ):
        extract_skill_section(section)
```

2. Delete the whole guidance check block (lines 712-729), from:

```python
    guidance = "\n".join(
        (
            extract_skill_section("COMPLETE_GUIDANCE"),
            extract_skill_section("INCOMPLETE_GUIDANCE"),
        )
    )
```

through:

```python
        raise AssertionError(
            "SKILL.md is missing required delivery guidance: "
            + ", ".join(missing_guidance)
        )
```

3. In `required_skill_concepts` (lines 774-794), replace the four artifact concepts:

```python
        "create or update a native markdown file artifact",
        "relatorio-reuniao.md",
        "do not repeat the complete report inline",
        "if the active surface cannot create or expose a markdown artifact",
```

with the report-only concepts:

```python
        "the entire message must be exactly the report",
        "beginning with `# relatório de reunião/visita`",
        "no code fences",
        "the conversation copy button must copy only the report",
        "a complete report contains no `pendências de informação` section",
```

- [ ] **Step 2: Run harness to verify it fails**

Run: `python3 scripts/test_flow.py 2>&1 | tail -2`
Expected: FAIL — `check_packaging` raises `SKILL.md is missing strict generation behavior:` listing the new report-only concepts (the guidance sections still exist in SKILL.md but are no longer checked, and the artifact prose is still present).

- [ ] **Step 3: Rewrite SKILL.md Report Output**

In `skills/relatorio-reuniao/SKILL.md`:

3a. Replace the two artifact paragraphs (lines 133-135):

```markdown
For every complete, overridden or regenerated report, place status and operational guidance before the report delivery. Create or update a native Markdown file artifact named `relatorio-reuniao.md`. Put only the report in that artifact, beginning with `# Relatório de reunião/visita`; do not put status or operational guidance in it, and do not repeat the complete report inline when artifact creation succeeds. Regenerated reports should update or replace the same artifact instead of intentionally creating duplicate report files.

If the active surface cannot create or expose a Markdown artifact, output the status and operational guidance followed by exactly one fenced `markdown` block. Put only the report inside that fallback block and emit nothing after its closing fence. `Pendências de informação`, when applicable, belongs inside the artifact or fallback report.
```

with:

```markdown
For every complete, overridden or regenerated report, the entire message must be exactly the report, beginning with `# Relatório de reunião/visita`. Render it as Markdown with no code fences. Do not output status, operational guidance, or any text before or after the report: the conversation copy button must copy only the report.
```

3b. Replace the complete-guidance paragraph, both marked guidance sections, and the overridden-report paragraph (lines 157-171, from `Before a complete report block, output this guidance.` through `<!-- INCOMPLETE_GUIDANCE_END -->`) with:

```markdown
For an overridden report, use `Não informado` for every unresolved field and append `## Pendências de informação` with every unresolved label inside the report. A complete report contains no `Pendências de informação` section and no missing placeholder.
```

- [ ] **Step 4: Run harness to verify all cases pass**

Run: `python3 scripts/test_flow.py 2>&1 | tail -2`
Expected: `All 33 conversational flow scenarios passed.`

- [ ] **Step 5: Commit**

```bash
git add skills/relatorio-reuniao/SKILL.md scripts/test_flow.py
git commit -m "feat: deliver the report as the entire message"
```

---

### Task 3: Version 0.3.7 metadata

Bump both manifests, release notes, README, and the acceptance baseline. Packaging checks first (red), then metadata (green).

**Files:**
- Modify: `scripts/test_flow.py` (expected version + submission phrases)
- Modify: `plugin.json`, `.codex-plugin/plugin.json`
- Modify: `docs/public-submission.md`, `README.md`, `tests/chatgpt-acceptance.md`

- [ ] **Step 1: Update packaging expectations first (failing)**

In `scripts/test_flow.py` `check_packaging`:

1. Replace `expected_version = "0.3.6"` with `expected_version = "0.3.7"` (around line 637).
2. Replace (around line 805):

```python
    if "Version 0.3.6" not in submission:
        raise AssertionError("submission release notes must name version 0.3.6")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "dist/documentar-reuniao-0.3.6.zip" not in readme:
        raise AssertionError("README must name the current public archive")
```

with:

```python
    if "Version 0.3.7" not in submission:
        raise AssertionError("submission release notes must name version 0.3.7")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "dist/documentar-reuniao-0.3.7.zip" not in readme:
        raise AssertionError("README must name the current public archive")
```

3. In `required_submission_content` (around line 819), replace
   `"Version 0.3.6 adds next-step deadlines",`
   with
   `"Version 0.3.7 delivers the report",`

- [ ] **Step 2: Run harness to verify it fails**

Run: `python3 scripts/test_flow.py 2>&1 | tail -2`
Expected: FAIL — `check_packaging` raises `public submission package must ship as version 0.3.7` before scenarios execute.

- [ ] **Step 3: Bump manifests and documents**

1. `plugin.json` and `.codex-plugin/plugin.json`: replace `"version": "0.3.6"` with `"version": "0.3.7"` in both.
2. `docs/public-submission.md` (line 24): replace the paragraph beginning `Version 0.3.6 adds next-step deadlines...` with:

```markdown
Version 0.3.7 delivers the report as the entire chat message: ChatGPT renders the Markdown report inline with no code fences and no guidance, so the message copy button copies exactly the report; overridden drafts carry `Pendências de informação` inside the report.
```

3. `README.md`: replace `documentar-reuniao-0.3.6.zip` with `documentar-reuniao-0.3.7.zip` (line 98), and replace the artifact sentence (line 100):

```markdown
Em superfícies compatíveis, o relatório é entregue como o artefato renderizado `relatorio-reuniao.md`; o bloco Markdown bruto é usado somente como fallback.
```

with:

```markdown
O relatório é entregue como a mensagem inteira da conversa, renderizado em Markdown, sem orientações ou cercas de código; o botão de cópia da mensagem copia apenas o relatório.
```

4. `tests/chatgpt-acceptance.md`:
   - Build section: `- Plugin version: 0.3.6` → `- Plugin version: 0.3.7`
   - Build section: `passed (\`python3 scripts/test_flow.py\`, 34/34)` → `passed (\`python3 scripts/test_flow.py\`, 33/33)`
   - Build section: both `- Installed-cache verification: pending for 0.3.6` and `- Auxiliary Codex loading: pending for 0.3.6` → `pending for 0.3.7`
   - Local ChatGPT Scenarios table: replace the `Rendered Markdown artifact` row with:

```markdown
| Report-only message | Pending on 0.3.7 | Verify the entire message is exactly the report rendered as Markdown: no status, no guidance, no code fences; the message copy button copies only the report; a draft report contains `Pendências de informação` inside the report. |
```

   - Procedure section: `after installing version \`0.3.6\`` → `after installing version \`0.3.7\``
   - Report-scenario `Expected:` paragraph (line 132): replace the whole paragraph with:

```markdown
Expected: a readable executive topic summary and a `Registro detalhado` section preserve every supplied fact without invention. Attribution and chronology remain intact. The entire message must be exactly the rendered report: no status, no guidance, no code fences. The message copy button copies only the report. The next-steps table must include the `Prazo` column with a calendar date per action. A draft report carries `Pendências de informação` inside the report.
```

- [ ] **Step 4: Run harness to verify everything passes**

Run: `python3 scripts/test_flow.py 2>&1 | tail -2`
Expected: `All 33 conversational flow scenarios passed.` and no packaging assertion.

- [ ] **Step 5: Commit**

```bash
git add plugin.json .codex-plugin/plugin.json docs/public-submission.md README.md tests/chatgpt-acceptance.md scripts/test_flow.py
git commit -m "chore: prepare version 0.3.7"
```

---

### Task 4: Build and inspect the public ZIP

**Files:**
- Create (ignored): `dist/documentar-reuniao-0.3.7.zip`

- [ ] **Step 1: Build the archive**

Run: `./scripts/build_public_zip.sh`
Expected: 33 scenario PASS lines, `All 33 conversational flow scenarios passed.`, integrity line `No errors detected in compressed data ...`, final line ending in `dist/documentar-reuniao-0.3.7.zip`

- [ ] **Step 2: Inspect the archive**

Run:

```bash
unzip -Z1 "dist/documentar-reuniao-0.3.7.zip"
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
unzip -p "dist/documentar-reuniao-0.3.7.zip" plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.3.7"'
```

Expected: exit 0.

Run:

```bash
python3 -c 'import zipfile; archive = zipfile.ZipFile("dist/documentar-reuniao-0.3.7.zip"); skill = archive.read("skills/relatorio-reuniao/SKILL.md").decode(); assert "the entire message must be exactly the report" in skill; assert "relatorio-reuniao.md" not in skill; assert "COMPLETE_GUIDANCE" not in skill'
```

Expected: exit 0.

- [ ] **Step 3: Final repository verification**

Run:

```bash
grep -rn "relatorio-reuniao.md\|artifactSupported" README.md docs/public-submission.md tests/chatgpt-acceptance.md tests/scenarios.json skills/relatorio-reuniao/SKILL.md scripts/test_flow.py plugin.json .codex-plugin/plugin.json || echo CLEAN
```

Expected: `CLEAN` (no artifact references remain in shipped files).

Run:

```bash
git diff --check && git status --short --branch && git log --oneline origin/main..HEAD
```

Expected: no whitespace errors; clean working tree (`dist/` ignored); `main` ahead of `origin/main` by this plan's commits.

---

### Task 5: Manual ChatGPT Work acceptance (user-executed)

Offline checks cannot prove live rendering. After this plan is merged and published:

1. Upload `dist/documentar-reuniao-0.3.7.zip` in the portal (Create plugin → Skills only).
2. In ChatGPT Work, select **Documentar Reunião** and generate a complete report.
3. Verify: the entire message is the rendered report alone — no status, no guidance, no code fences; the message copy button copies only the report; a draft report carries `Pendências de informação` inside the report.
4. Record evidence in `tests/chatgpt-acceptance.md` (row `Report-only message`), then commit `test: record report-only acceptance` after user approval.
