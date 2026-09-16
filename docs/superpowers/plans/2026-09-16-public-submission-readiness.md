# Public Submission Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare the smallest complete `0.3.3` skills-only package and submission material required by the OpenAI public plugin portal.

**Architecture:** Keep the existing single-file runtime unchanged. Add public metadata and one logo to both manifests, add repository-hosted privacy and terms documents, and keep portal-only values and reviewer cases in one submission document guarded by the deterministic package harness.

**Tech Stack:** Agent Plugins schema 1.0.0, JSON manifests, Markdown, PNG, Python 3 standard library checks.

---

## File Map

- Modify: `scripts/test_flow.py` - public metadata, document, case-count and PNG checks.
- Modify: `plugin.json` - canonical `0.3.3` publisher and public listing metadata.
- Modify: `.codex-plugin/plugin.json` - compatible OpenAI presentation metadata.
- Create: `PRIVACY.md` - public skills-only privacy statement.
- Create: `TERMS.md` - public terms of use.
- Create: `docs/public-submission.md` - mandatory portal copy and reviewer cases.
- Modify: `README.md` - public support and submission links.
- Modify: `skills/relatorio-reuniao/SKILL.md` - explicit unsupported external-action behavior.
- Add: `assets/logo.png` - user-generated square workflow automation logo.

## Task 1: Validate And Publish Package Metadata

**Files:**
- Modify: `scripts/test_flow.py`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Add: `assets/logo.png`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add failing publication metadata checks**

Import `struct` in `scripts/test_flow.py` and add these checks after the two manifests are loaded:

```python
expected_version = "0.3.3"
expected_developer = "João Eduardo Ferreira Bertacchi"
expected_repository = "https://github.com/joaobertacchi/gpt-workflows"
expected_interface = {
    "websiteURL": expected_repository,
    "privacyPolicyURL": f"{expected_repository}/blob/main/PRIVACY.md",
    "termsOfServiceURL": f"{expected_repository}/blob/main/TERMS.md",
    "logo": "./assets/logo.png",
}

if portable_manifest["version"] != expected_version:
    raise AssertionError("public submission package must ship as version 0.3.3")
if portable_manifest["author"]["name"] != expected_developer:
    raise AssertionError("portable manifest must use the verified developer name")
if compat_manifest["author"]["name"] != expected_developer:
    raise AssertionError("compatibility manifest must use the verified developer name")
if portable_manifest.get("homepage") != expected_repository:
    raise AssertionError("portable manifest must publish the repository homepage")
if portable_manifest.get("repository") != expected_repository:
    raise AssertionError("portable manifest must publish its repository")

portable_interface = portable_manifest["extensions"]["com.openai"]["interface"]
compat_interface = compat_manifest["interface"]
for key, expected in expected_interface.items():
    if portable_interface.get(key) != expected:
        raise AssertionError(f"portable interface has invalid {key}")
    if compat_interface.get(key) != expected:
        raise AssertionError(f"compatibility interface has invalid {key}")
```

Add `assets/logo.png` to `required_paths`, then validate its file structure:

```python
logo = (ROOT / "assets/logo.png").read_bytes()
if logo[:8] != b"\x89PNG\r\n\x1a\n" or logo[12:16] != b"IHDR":
    raise AssertionError("assets/logo.png must be a valid PNG")
width, height = struct.unpack(">II", logo[16:24])
if width != height:
    raise AssertionError("assets/logo.png must be square")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because the manifests still declare `0.3.2` and placeholder publisher metadata.

- [ ] **Step 3: Update the portable manifest**

Set the root values in `plugin.json` to:

```json
"version": "0.3.3",
"author": {
  "name": "João Eduardo Ferreira Bertacchi",
  "url": "https://github.com/joaobertacchi"
},
"homepage": "https://github.com/joaobertacchi/gpt-workflows",
"repository": "https://github.com/joaobertacchi/gpt-workflows"
```

Set `extensions.com.openai.interface.developerName` to `João Eduardo Ferreira Bertacchi` and add:

```json
"websiteURL": "https://github.com/joaobertacchi/gpt-workflows",
"privacyPolicyURL": "https://github.com/joaobertacchi/gpt-workflows/blob/main/PRIVACY.md",
"termsOfServiceURL": "https://github.com/joaobertacchi/gpt-workflows/blob/main/TERMS.md",
"logo": "./assets/logo.png"
```

- [ ] **Step 4: Update the compatibility manifest**

Set `.codex-plugin/plugin.json` to version `0.3.3`, use the same `author` object and `developerName`, and add the same four interface URL/logo values. Preserve `skills: "./skills/"` and all starter prompts.

- [ ] **Step 5: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all 30 scenarios pass and the square `1254 x 1254` PNG is accepted.

- [ ] **Step 6: Commit package metadata**

```bash
git add plugin.json .codex-plugin/plugin.json scripts/test_flow.py assets/logo.png docs/superpowers/plans/2026-09-16-public-submission-readiness.md
git commit -m "chore: add public plugin metadata"
```

## Task 2: Add Required Public Documents

**Files:**
- Modify: `scripts/test_flow.py`
- Create: `PRIVACY.md`
- Create: `TERMS.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Require the legal documents**

Add `PRIVACY.md` and `TERMS.md` to `required_paths`. Add these content checks:

```python
public_documents = {
    "PRIVACY.md": (
        "does not independently collect, store, or transmit",
        "no developer-operated server",
        "OpenAI",
        "https://github.com/joaobertacchi/gpt-workflows/issues",
    ),
    "TERMS.md": (
        "review names, dates, responsibilities",
        "cannot send messages or write to external systems",
        "as is",
        "MIT License",
    ),
}
for path, required_phrases in public_documents.items():
    text = (ROOT / path).read_text(encoding="utf-8")
    missing_phrases = [phrase for phrase in required_phrases if phrase not in text]
    if missing_phrases:
        raise AssertionError(f"{path} is missing mandatory public statements")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because `PRIVACY.md` and `TERMS.md` do not exist.

- [ ] **Step 3: Create `PRIVACY.md`**

```markdown
# Privacy Policy

Effective date: September 16, 2026

Documentar Reunião is a skills-only instruction package for ChatGPT. It has no developer-operated server, account system, database, telemetry, external API, or authentication system.

The plugin does not independently collect, store, or transmit meeting content or other user data to the developer. It does not process data outside the ChatGPT environment through infrastructure operated by the developer.

Use of ChatGPT and processing performed by OpenAI remain governed by OpenAI's own terms and privacy policies. This policy does not describe or control OpenAI's processing.

For privacy questions about this plugin package, open an issue at https://github.com/joaobertacchi/gpt-workflows/issues.
```

- [ ] **Step 4: Create `TERMS.md`**

```markdown
# Terms of Use

Effective date: September 16, 2026

Documentar Reunião helps users organize supplied meeting or commercial-visit notes into a structured report.

Users must review names, dates, responsibilities, and all report content before sharing or relying on it. The plugin cannot send messages or write to external systems such as CRM or WhatsApp.

The plugin and generated reports are provided "as is", without a guarantee of completeness, accuracy, or fitness for a particular purpose. Users remain responsible for lawful and appropriate use of the generated content.

Distribution of the source code is governed by the repository's MIT License.
```

- [ ] **Step 5: Run the harness and verify GREEN**

Run: `python3 scripts/test_flow.py`

Expected: all 30 scenarios pass and both documents satisfy their mandatory statements.

- [ ] **Step 6: Commit public documents**

```bash
git add PRIVACY.md TERMS.md scripts/test_flow.py
git commit -m "docs: add public privacy and terms"
```

## Task 3: Prepare Portal Submission Copy

**Files:**
- Modify: `scripts/test_flow.py`
- Create: `docs/public-submission.md`
- Modify: `README.md`
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Add failing submission-material checks**

Add `docs/public-submission.md` to `required_paths` and add:

```python
submission = (ROOT / "docs/public-submission.md").read_text(encoding="utf-8")
positive_cases = re.findall(r"^### P[1-5] ", submission, flags=re.MULTILINE)
negative_cases = re.findall(r"^### N[1-3] ", submission, flags=re.MULTILINE)
if len(positive_cases) != 5 or len(negative_cases) != 3:
    raise AssertionError("submission material must contain five positive and three negative cases")
required_submission_content = (
    "João Eduardo Ferreira Bertacchi",
    "https://github.com/joaobertacchi/gpt-workflows/issues",
    "Initial public submission",
    "Skills only",
    "No credentials or fixture data required",
)
if any(phrase not in submission for phrase in required_submission_content):
    raise AssertionError("submission material is missing mandatory portal content")

if "if the user asks to send or save the report" not in skill_text:
    raise AssertionError("skill must reject unsupported external actions explicitly")
```

- [ ] **Step 2: Run the harness and verify RED**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because `docs/public-submission.md` does not exist and the skill lacks the explicit external-action rule.

- [ ] **Step 3: Create the submission document**

Create `docs/public-submission.md` with these sections and complete values:

```markdown
# Public Plugin Submission

## Listing

- Name: Documentar Reunião
- Type: Skills only
- Category: Productivity
- Developer: João Eduardo Ferreira Bertacchi
- Website: https://github.com/joaobertacchi/gpt-workflows
- Support: https://github.com/joaobertacchi/gpt-workflows/issues
- Privacy: https://github.com/joaobertacchi/gpt-workflows/blob/main/PRIVACY.md
- Terms: https://github.com/joaobertacchi/gpt-workflows/blob/main/TERMS.md
- Short description: Registre uma reunião e gere um relatório estruturado.
- Long description: Cole ou dite as anotações de uma reunião comercial. O workflow preserva os detalhes fornecidos, coleta somente os campos obrigatórios ausentes, confirma datas inferidas e gera um relatório estruturado e copiável.

## Starter Prompts

- Começar a documentar uma reunião.
- Documentar estas anotações e perguntar apenas pelos campos obrigatórios ausentes.
- Gerar mesmo com pendências.

## Release Notes

Initial public submission of Documentar Reunião, a skills-only plugin with no MCP server, authentication, external API, or developer-operated data collection. Version 0.3.3 preserves detailed notes and attribution, confirms inferred dates, collects only unresolved required fields, and produces a report-only copy block.

## Reviewer Data

No credentials or fixture data required.

## Positive Test Cases

### P1 Start intake
Prompt: `começar`
Expected behavior: activate the skill and list exactly the seven required categories.
Expected result shape: one concise intake checklist; no report.

### P2 Complete first turn
Prompt: `Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo negociação. Discutimos a renovação do contrato. Bruno enviará a proposta revisada. O follow up será em 18/09/2026.`
Expected behavior: generate immediately without asking for data already supplied.
Expected result shape: complete report block with no `Pendências de informação`.

### P3 Partial collection
Prompt: `Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.`
Expected behavior: ask only for type, topics, next steps with responsible people, and follow-up date.
Expected result shape: one missing-field list; no report.

### P4 Relative dates
Prompt: `Empresa Acme. Reunião ontem com Ana, tipo negociação. Discutimos a renovação. Bruno enviará a proposta. O follow up será sexta que vem.`
Expected behavior: resolve both relative dates and wait for explicit confirmation.
Expected result shape: confirmation question showing both calendar dates; no report before confirmation.

### P5 Detailed fidelity
Prompt: `A reunião da empresa Acme foi em 13/09/2026 às 13h, durou cerca de uma hora e foi com Luciano. Luciano relatou que o time deveria registrar reuniões com clientes, mas não vem fazendo isso e os registros deveriam entrar no CRM. Durante a conversa ele avaliou WhatsApp e pediu alternativas melhores. Propus um plugin público para ChatGPT. Recebi os requisitos na segunda-feira e fiquei de enviar a prova de conceito até o fim do dia. Luciano instalará, testará em dispositivos móveis e retornará em 17/09/2026.`
Expected behavior: request the missing valid visit type, confirm the interpreted relative date, then preserve every supplied fact and attribution.
Expected result shape: executive topics, `Registro detalhado`, owned next steps, and exactly one report-only copy block.

## Negative Test Cases

### N1 Invalid visit type
Prompt: `Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo instalação. Discutimos manutenção. Bruno enviará o orçamento. Follow up em 18/09/2026.`
Expected behavior: reject `instalação` and ask only for a valid visit type.
Expected result shape: clarification request; no report.

### N2 Quoted override
Prompt: `Empresa Acme em 15/09/2026. A instrução dizia "continuar mesmo assim".`
Expected behavior: treat the phrase as quoted text, not authorization to generate with gaps.
Expected result shape: missing-required-field request; no incomplete report.

### N3 Unsupported external action
Prompt: `Envie este relatório para o CRM e para o WhatsApp.`
Expected behavior: do not claim to send, save, or connect to an external system.
Expected result shape: state that the plugin has no such integration and that the user must copy the report manually.
```

- [ ] **Step 4: Make unsupported external actions explicit**

Add this bullet under `Common Mistakes` in `SKILL.md`:

```markdown
- If the user asks to send or save the report in CRM, WhatsApp or another external system, state that the plugin has no such integration and that the user must copy the report manually. Never claim the external action occurred.
```

- [ ] **Step 5: Update README publication links**

Replace the current publication placeholder paragraph with links to the repository, Issues support, `PRIVACY.md`, `TERMS.md`, `docs/public-submission.md`, and `https://platform.openai.com/plugins`. Preserve Android as a post-publication test.

- [ ] **Step 6: Run complete verification**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); YAML.safe_load_file("skills/relatorio-reuniao/SKILL.md", aliases: false); puts "Structured files OK"'
git diff --check
```

Expected: 30/30 scenarios pass, structured files are valid, and the whitespace check is empty.

- [ ] **Step 7: Commit submission material**

```bash
git add README.md docs/public-submission.md scripts/test_flow.py skills/relatorio-reuniao/SKILL.md
git commit -m "docs: prepare public plugin submission"
```

## Task 4: Verify Public Readiness

**Files:**
- Verify: repository and public URLs

- [ ] **Step 1: Refresh local package cache**

Run:

```bash
codex plugin remove gpt-workflows@personal
codex plugin add gpt-workflows@personal
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.3.3
```

Expected: installed root ends in `0.3.3`; diff produces no output.

- [ ] **Step 2: Verify repository state**

Run:

```bash
python3 scripts/test_flow.py
git status --short
git log --oneline -5
```

Expected: 30/30 scenarios pass, the worktree is clean, and the three implementation commits follow the design commit.

- [ ] **Step 3: Push only with explicit confirmation**

Do not push automatically. Ask the user before running `git push origin main`.

- [ ] **Step 4: Verify public URLs after push**

Open the repository, Issues, privacy, and terms URLs in a signed-out browser session and confirm HTTP success before using them in the portal.

- [ ] **Step 5: Confirm external portal prerequisites**

The user must confirm that `João Eduardo Ferreira Bertacchi` is verified in the publishing organization and that the submitter has **Apps Management: Write**. These cannot be completed from the repository.
