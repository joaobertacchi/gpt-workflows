# Rendered Markdown Artifact Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver meeting reports as native `relatorio-reuniao.md` artifacts when supported, with the current fenced Markdown block as an explicit fallback.

**Architecture:** Keep the plugin instruction-only and model delivery as separate chat-message and artifact-content channels in the offline harness. `SKILL.md` requests the native artifact first; a fixture flag exercises fallback without pretending the harness can render ChatGPT UI.

**Tech Stack:** Markdown skill instructions, Python 3 dependency-free harness, JSON scenario fixtures, Bash ZIP packaging.

---

### Task 1: Model Artifact-First Delivery

**Files:**
- Modify: `scripts/test_flow.py:242-320,321-425,801-832`
- Modify: `tests/scenarios.json`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Replace the fence-only assertion with the desired delivery assertion**

Replace `assert_copy_boundary()` with:

```python
def assert_report_delivery(turn: dict[str, Any]) -> None:
    output = turn["output"]
    artifact_name = turn.get("artifactName")
    artifact_content = turn.get("artifactContent")
    operational_phrases = (
        "Todas as informações necessárias foram preenchidas",
        "O relatório está pronto para ser revisado e compartilhado",
        "O relatório foi gerado como rascunho com informações pendentes",
        "O rascunho deve ser completado e revisado",
    )

    if artifact_name is not None:
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

Change the generated-turn validation in `main()` to call:

```python
assert_report_delivery(turn)
```

- [ ] **Step 2: Add one fallback scenario fixture**

Append a case to `tests/scenarios.json` with the same complete fields used by an existing successful report and this top-level flag:

```json
{
  "id": "artifact-unavailable-uses-markdown-fallback",
  "activation": "plugin_selected",
  "artifactSupported": false,
  "turns": [
    {
      "text": "Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo negociação. Discutimos a renovação. Bruno enviará a proposta. Follow up em 18/09/2026.",
      "fields": {
        "company": "Acme",
        "meeting_date": "15/09/2026",
        "contacts": ["Ana"],
        "visit_type": "negociação",
        "topics_discussed": ["Renovação"],
        "next_steps": [{"action": "Enviar a proposta", "responsible": "Bruno"}],
        "follow_up_date": "18/09/2026"
      }
    }
  ],
  "expectations": [
    {
      "action": "generate",
      "state": "DONE",
      "missing": [],
      "outputContains": ["```markdown", "# Relatório de reunião/visita"],
      "artifactName": null,
      "artifactContent": null
    }
  ]
}
```

- [ ] **Step 3: Run the harness to verify RED**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL because normal generated turns still have no `relatorio-reuniao.md` artifact.

- [ ] **Step 4: Separate report content from its delivery channel**

Keep the existing template substitution in `render_report()`, but change its signature and return value to:

```python
def render_report(
    record: dict[str, Any], missing: list[str], artifact_supported: bool
) -> dict[str, Any]:
```

After building `template` and `guidance`, replace the current string return with:

```python
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

In `simulate()`, read support once:

```python
artifact_supported = case.get("artifactSupported", True)
```

For generated turns, assign the delivery and merge it into the result:

```python
        delivery: dict[str, Any] | None = None
        if action == "generate":
            delivery = render_report(record, missing, artifact_supported)
            output = delivery["output"]
```

Replace the result append with:

```python
        result = {"action": action, "state": state, "missing": missing, "output": output}
        if delivery is not None:
            result.update(
                artifactName=delivery["artifactName"],
                artifactContent=delivery["artifactContent"],
            )
        results.append(result)
```

Update `expectation_matches()` so content assertions inspect both channels:

```python
    searchable_output = "\n".join(
        value
        for value in (actual.get("output"), actual.get("artifactContent"))
        if value
    )
```

Use `searchable_output` instead of `output` in required and forbidden fragment checks. Keep `artifactName` and `artifactContent` in `core` so the fallback fixture verifies both null values.

- [ ] **Step 5: Run the harness to verify GREEN**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: all 31 conversational flow scenarios pass.

- [ ] **Step 6: Commit the harness contract**

```bash
git add scripts/test_flow.py tests/scenarios.json
git commit -m "test: model markdown artifact delivery"
```

### Task 2: Instruct ChatGPT to Create the Artifact

**Files:**
- Modify: `scripts/test_flow.py:640-666`
- Modify: `skills/relatorio-reuniao/SKILL.md:126-166`
- Modify: `tests/chatgpt-acceptance.md:13-32,66-136`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add failing skill-contract checks**

Add these normalized concepts to `required_skill_concepts`:

```python
"create or update a native markdown file artifact",
"relatorio-reuniao.md",
"do not repeat the complete report inline",
"if the active surface cannot create or expose a markdown artifact",
```

- [ ] **Step 2: Run the harness to verify RED**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL with `SKILL.md is missing strict generation behavior` and the artifact-delivery phrases.

- [ ] **Step 3: Replace the fence-only output instruction**

Replace the paragraph at `SKILL.md:130` with:

```markdown
For every complete, overridden or regenerated report, place status and operational guidance before the report delivery. Create or update a native Markdown file artifact named `relatorio-reuniao.md`. Put only the report in that artifact, beginning with `# Relatório de reunião/visita`; do not put status or operational guidance in it, and do not repeat the complete report inline when artifact creation succeeds. Regenerated reports should update or replace the same artifact instead of intentionally creating duplicate report files.

If the active surface cannot create or expose a Markdown artifact, output the status and operational guidance followed by exactly one fenced `markdown` block. Put only the report inside that fallback block and emit nothing after its closing fence. `Pendências de informação`, when applicable, belongs inside the artifact or fallback report.
```

Update the complete guidance to:

```markdown
✅ **Todas as informações necessárias foram preenchidas.**

O relatório está pronto para ser revisado e compartilhado. Revise nomes, datas e responsáveis; depois, use os controles do artefato para copiar ou baixar o arquivo Markdown. Se o artefato não estiver disponível, copie o conteúdo do bloco Markdown.
```

Update the incomplete guidance to:

```markdown
⚠️ **O relatório foi gerado como rascunho com informações pendentes.**

O rascunho deve ser completado e revisado antes de ser compartilhado como versão final. Use os controles do artefato para copiar ou baixar o arquivo Markdown; se ele não estiver disponível, copie o bloco Markdown. O plugin não envia mensagens nem grava o relatório em outros sistemas.
```

- [ ] **Step 4: Update the manual acceptance contract**

Set the build version in `tests/chatgpt-acceptance.md` to `0.3.5` and mark artifact rendering as pending until tested. Replace the detailed-delivery expectation with:

```markdown
Expected: a readable executive topic summary and a `Registro detalhado` section preserve every supplied fact without invention. Attribution and chronology remain intact. Status and operational guidance stay in chat; the report opens as a rendered `relatorio-reuniao.md` artifact containing only the report. Copying or downloading the artifact preserves Markdown source. On a surface without artifact support, guidance precedes exactly one fenced Markdown fallback containing only the report.
```

Add a manual acceptance row named `Rendered Markdown artifact` with result `Pending on 0.3.5` and evidence requirements for formatted headings, labels, lists, tables, source copy/download, and absence of duplicate inline report content.

- [ ] **Step 5: Run the harness to verify GREEN**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: all 31 conversational flow scenarios pass.

- [ ] **Step 6: Commit the runtime behavior**

```bash
git add skills/relatorio-reuniao/SKILL.md scripts/test_flow.py tests/chatgpt-acceptance.md
git commit -m "feat: deliver reports as markdown artifacts"
```

### Task 3: Release Version 0.3.5

**Files:**
- Modify: `scripts/test_flow.py:515-536,675-686`
- Modify: `plugin.json:4`
- Modify: `.codex-plugin/plugin.json:3`
- Modify: `README.md:89-100`
- Modify: `docs/public-submission.md:22-24`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add failing version and documentation checks**

Change:

```python
expected_version = "0.3.5"
```

Require current documentation:

```python
if "Version 0.3.5" not in submission:
    raise AssertionError("submission release notes must name version 0.3.5")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
if "dist/documentar-reuniao-0.3.5.zip" not in readme:
    raise AssertionError("README must name the current public archive")
```

- [ ] **Step 2: Run the harness to verify RED**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL with `public submission package must ship as version 0.3.5`.

- [ ] **Step 3: Apply release metadata**

Set both manifest versions to `0.3.5`.

Change the README archive path to `dist/documentar-reuniao-0.3.5.zip` and add one sentence under publication:

```markdown
Em superfícies compatíveis, o relatório é entregue como o artefato renderizado `relatorio-reuniao.md`; o bloco Markdown bruto é usado somente como fallback.
```

Change the release notes in `docs/public-submission.md` to:

```markdown
Version 0.3.5 delivers meeting reports as rendered Markdown file artifacts on supported ChatGPT surfaces, preserves raw Markdown for copy or download, and retains a fenced Markdown fallback where artifacts are unavailable.
```

- [ ] **Step 4: Run the harness to verify GREEN**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: all 31 conversational flow scenarios pass.

- [ ] **Step 5: Commit the release metadata**

```bash
git add plugin.json .codex-plugin/plugin.json README.md docs/public-submission.md scripts/test_flow.py
git commit -m "chore: prepare version 0.3.5"
```

### Task 4: Build and Inspect the Public ZIP

**Files:**
- Generate, ignored: `dist/documentar-reuniao-0.3.5.zip`

- [ ] **Step 1: Run the packaging workflow**

```bash
./scripts/build_public_zip.sh
```

Expected: 31 scenarios pass, ZIP integrity passes, and the final path ends in `dist/documentar-reuniao-0.3.5.zip`.

- [ ] **Step 2: Verify exact archive contents**

```bash
unzip -Z1 dist/documentar-reuniao-0.3.5.zip
```

Expected exactly:

```text
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

- [ ] **Step 3: Verify packaged runtime instructions and size**

```bash
unzip -p dist/documentar-reuniao-0.3.5.zip plugin.json | python3 -c 'import json, sys; assert json.load(sys.stdin)["version"] == "0.3.5"'
python3 -c 'import zipfile; archive = zipfile.ZipFile("dist/documentar-reuniao-0.3.5.zip"); assert "relatorio-reuniao.md" in archive.read("skills/relatorio-reuniao/SKILL.md").decode()'
test "$(wc -c < dist/documentar-reuniao-0.3.5.zip | tr -d ' ')" -lt 104857600
```

Expected: version assertion succeeds, the artifact filename is present, and the size check exits successfully.

- [ ] **Step 4: Perform the final repository check**

```bash
git diff --check
git status --short --branch
```

Expected: no whitespace errors and no tracked changes.

### Task 5: Run ChatGPT Work Acceptance

**Files:**
- Modify after test: `tests/chatgpt-acceptance.md`

- [ ] **Step 1: Install version 0.3.5 and start a fresh Work conversation**

Upload `dist/documentar-reuniao-0.3.5.zip`, install that draft, restart ChatGPT, select **Work**, select **Documentar Reunião** with `@`, and start a new conversation.

- [ ] **Step 2: Run the detailed report acceptance prompt**

Use the existing prompt under `Detailed-note fidelity and copy boundary` in `tests/chatgpt-acceptance.md` and complete any required type/date confirmation.

Expected: status remains in chat and one `relatorio-reuniao.md` artifact opens with rendered headings, bold labels, bullets, and tables; the report is not duplicated inline.

- [ ] **Step 3: Verify Markdown source preservation**

Use the artifact's native source-copy or download control.

Expected: copied or downloaded content begins with `# Relatório de reunião/visita` and contains Markdown markers such as `**Empresa (cliente):**` without operational guidance.

- [ ] **Step 4: Record evidence**

Update the `Rendered Markdown artifact` row in `tests/chatgpt-acceptance.md` from `Pending on 0.3.5` to `Passed` or `Failed`, with a conversation identifier, transcript, or screenshot and the exact unexpected output on failure.

- [ ] **Step 5: Commit successful acceptance evidence**

Only after a pass:

```bash
git add tests/chatgpt-acceptance.md
git commit -m "test: record markdown artifact acceptance"
```
