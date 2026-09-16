# Meeting Report Plugin Corrections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a submission-ready, installable ChatGPT plugin that collects every required meeting field, asks only for unresolved required information, confirms inferred dates, and generates the configured report.

**Architecture:** Make `skills/relatorio-reuniao/` a self-contained Agent Skill with its own `references/` and `assets/`. Keep the runtime model-driven and dependency-free; use the root Python harness for deterministic contract and package checks, Codex only as an auxiliary installed-package check, and ChatGPT local installation as the pre-submission acceptance surface.

**Tech Stack:** Agent Skills (`SKILL.md`), OpenAI skill metadata (`agents/openai.yaml`), Agent Plugins manifests (JSON), Markdown resources, Python 3 standard library tests, ChatGPT local marketplace.

---

## File Map

**Runtime skill files:**

- Modify: `skills/relatorio-reuniao/SKILL.md`
- Modify: `skills/relatorio-reuniao/agents/openai.yaml`
- Move: `references/workflow.md` to `skills/relatorio-reuniao/references/workflow.md`
- Move: `references/field-schema.json` to `skills/relatorio-reuniao/references/field-schema.json`
- Move: `references/validation-rules.json` to `skills/relatorio-reuniao/references/validation-rules.json`
- Move: `assets/intake-message.md` to `skills/relatorio-reuniao/assets/intake-message.md`
- Move: `assets/meeting-report-template.md` to `skills/relatorio-reuniao/assets/meeting-report-template.md`
- Move: `assets/report-delivery-guidance.md` to `skills/relatorio-reuniao/assets/report-delivery-guidance.md`

**Package and verification files:**

- Modify: `scripts/test_flow.py`
- Modify: `tests/scenarios.json`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `README.md`
- Create: `tests/chatgpt-acceptance.md`

Do not add MCP configuration, dependencies, network calls, a backend, storage, CRM integration, or natural-language parsing code.

## Task 1: Make Runtime Resources Resolve From The Skill Root

**Files:**

- Modify: `scripts/test_flow.py:14-18,128-147,217-220`
- Move: `references/*.json`, `references/workflow.md`
- Move: `assets/*.md`

- [ ] **Step 1: Add a failing package-layout check**

Define the skill root and replace the runtime entries in `required_paths` with skill-relative locations:

```python
ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills/relatorio-reuniao"


def load_skill_json(relative_path: str) -> dict[str, Any]:
    return json.loads((SKILL_ROOT / relative_path).read_text(encoding="utf-8"))
```

```python
required_paths = [
    "plugin.json",
    ".codex-plugin/plugin.json",
    "skills/relatorio-reuniao/SKILL.md",
    "skills/relatorio-reuniao/agents/openai.yaml",
    "skills/relatorio-reuniao/references/workflow.md",
    "skills/relatorio-reuniao/references/field-schema.json",
    "skills/relatorio-reuniao/references/validation-rules.json",
    "skills/relatorio-reuniao/assets/intake-message.md",
    "skills/relatorio-reuniao/assets/meeting-report-template.md",
    "skills/relatorio-reuniao/assets/report-delivery-guidance.md",
    "tests/scenarios.json",
]
```

Add checks that the old canonical directories no longer exist:

```python
for obsolete in (ROOT / "assets", ROOT / "references"):
    if obsolete.exists():
        raise AssertionError(f"runtime resources must live inside the skill: {obsolete.relative_to(ROOT)}")
```

Change schema loads to:

```python
FIELD_SCHEMA = load_skill_json("references/field-schema.json")
VALIDATION_RULES = load_skill_json("references/validation-rules.json")
```

- [ ] **Step 2: Run the test and verify the intended failure**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because `skills/relatorio-reuniao/references/*` and `skills/relatorio-reuniao/assets/*` do not exist yet.

- [ ] **Step 3: Move each runtime resource without retaining duplicates**

Run:

```bash
mkdir -p skills/relatorio-reuniao/references skills/relatorio-reuniao/assets
mv references/workflow.md skills/relatorio-reuniao/references/workflow.md
mv references/field-schema.json skills/relatorio-reuniao/references/field-schema.json
mv references/validation-rules.json skills/relatorio-reuniao/references/validation-rules.json
mv assets/intake-message.md skills/relatorio-reuniao/assets/intake-message.md
mv assets/meeting-report-template.md skills/relatorio-reuniao/assets/meeting-report-template.md
mv assets/report-delivery-guidance.md skills/relatorio-reuniao/assets/report-delivery-guidance.md
rmdir references assets
```

- [ ] **Step 4: Update package checks to read the new resource locations**

Use `SKILL_ROOT` for guidance and skill-resource reads:

```python
guidance = (SKILL_ROOT / "assets/report-delivery-guidance.md").read_text(encoding="utf-8")
validation_rule_ids = {
    rule["id"]
    for rule in load_skill_json("references/validation-rules.json")["rules"]
}
```

- [ ] **Step 5: Run the package and flow checks**

Run: `python3 scripts/test_flow.py`

Expected: all existing scenarios PASS and no missing-resource error.

- [ ] **Step 6: Commit only if the user explicitly requests a commit**

If authorized:

```bash
git add scripts/test_flow.py skills/relatorio-reuniao
git commit -m "fix: colocate meeting skill resources"
```

## Task 2: Enforce Field Types And Field-Specific Negative Answers

**Files:**

- Modify: `skills/relatorio-reuniao/references/field-schema.json`
- Modify: `skills/relatorio-reuniao/references/validation-rules.json`
- Modify: `scripts/test_flow.py:28-80`
- Modify: `tests/scenarios.json`

- [ ] **Step 1: Add failing scenarios for invalid types and valid explicit absence**

Append these cases:

```json
{
  "id": "string-does-not-satisfy-contacts-list",
  "invoked": true,
  "turns": [{
    "text": "O contato foi informado em formato inválido no registro extraído.",
    "fields": {
      "company": "Acme",
      "meeting_date": "2026-09-15",
      "contacts": "Ana",
      "visit_type": "preventiva",
      "topics_discussed": ["Revisão"],
      "next_steps": "Nenhum próximo passo definido",
      "follow_up_date": "Não haverá follow up"
    }
  }],
  "expectations": [{
    "action": "ask_missing",
    "state": "WAITING_FOR_MISSING",
    "missing": ["contacts"]
  }]
}
```

Also replace the text in `explicit-mention-treats-suffix-as-first-turn` with text that actually contains every supplied fixture field:

```text
@Documentar Reunião Empresa Acme, reunião em 10/09/2026 com Ana, tipo negociação. Discutimos a renovação do contrato. Bruno enviará a proposta e o follow up será em 16/09/2026.
```

```json
{
  "id": "explicit-none-completes-next-steps-and-follow-up",
  "invoked": true,
  "turns": [{
    "text": "Não existem próximos passos e não haverá follow up.",
    "fields": {
      "company": "Acme",
      "meeting_date": "2026-09-15",
      "contacts": ["Ana"],
      "visit_type": "preventiva",
      "topics_discussed": ["Revisão"],
      "next_steps": "Nenhum próximo passo definido",
      "follow_up_date": "Não haverá follow up"
    }
  }],
  "expectations": [{"action": "generate", "state": "DONE", "missing": []}]
}
```

- [ ] **Step 2: Run the scenarios and verify they fail**

Run: `python3 scripts/test_flow.py`

Expected: at least the invalid `contacts` case fails because the current harness accepts a substantive string for `array<string>`; the explicit-none case fails until the schema defines the allowed negative values.

- [ ] **Step 3: Make explicit absence part of the two applicable field definitions**

Add to `next_steps`:

```json
"allowExplicitNone": true,
"explicitNoneValue": "Nenhum próximo passo definido"
```

Add to `follow_up_date`:

```json
"allowExplicitNone": true,
"explicitNoneValue": "Não haverá follow up"
```

Replace global negative-answer semantics in `validation-rules.json`:

```json
"explicitNegativeAnswers": {
  "next_steps": [
    "não existem próximos passos",
    "não há próximos passos",
    "nenhum próximo passo"
  ],
  "follow_up_date": [
    "não haverá follow up",
    "não será feito follow up",
    "sem follow up"
  ]
}
```

Remove `explicitNegativeAnswersAreValid` so negative answers cannot accidentally satisfy company, meeting date, contacts, type, or topics.

- [ ] **Step 4: Enforce every declared field type in the harness**

Replace `field_is_complete` with:

```python
def field_is_complete(field: dict[str, Any], value: Any) -> bool:
    explicit_none = field.get("explicitNoneValue")
    if field.get("allowExplicitNone") and isinstance(value, str):
        return normalize(value) == normalize(explicit_none)

    if not is_substantive(value, MISSING_SENTINELS):
        return False

    allowed_values = field.get("allowedValues")
    if allowed_values:
        return isinstance(value, str) and normalize(value) in {
            normalize(option) for option in allowed_values
        }

    field_type = field.get("type")
    if field_type == "string":
        return isinstance(value, str)
    if field_type == "array<string>":
        return (
            isinstance(value, list)
            and bool(value)
            and all(isinstance(item, str) and is_substantive(item, MISSING_SENTINELS) for item in value)
        )
    if field_type == "array<object>":
        item_fields = field.get("itemFields", [])
        return (
            isinstance(value, list)
            and bool(value)
            and bool(item_fields)
            and all(
                isinstance(item, dict)
                and all(is_substantive(item.get(key), MISSING_SENTINELS) for key in item_fields)
                for item in value
            )
        )
    raise AssertionError(f"unsupported field type: {field_type}")
```

- [ ] **Step 5: Run all scenarios**

Run: `python3 scripts/test_flow.py`

Expected: all scenarios PASS, including invalid types and explicit absence.

- [ ] **Step 6: Commit only if explicitly authorized**

If authorized:

```bash
git add scripts/test_flow.py tests/scenarios.json skills/relatorio-reuniao/references
git commit -m "fix: validate meeting fields strictly"
```

## Task 3: Model Inferred-Date Confirmation And Safe Overrides

**Files:**

- Modify: `tests/scenarios.json`
- Modify: `scripts/test_flow.py:69-125`
- Modify: `skills/relatorio-reuniao/references/validation-rules.json`

- [ ] **Step 1: Add failing date-confirmation scenarios**

Use turn metadata to distinguish extracted values from confirmation state:

```json
{
  "id": "relative-dates-require-confirmation",
  "invoked": true,
  "turns": [
    {
      "text": "A reunião foi ontem e o follow up será sexta que vem.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-14",
        "contacts": ["Ana"],
        "visit_type": "negociação",
        "topics_discussed": ["Contrato"],
        "next_steps": [{"action": "Enviar proposta", "responsible": "Bruno"}],
        "follow_up_date": "2026-09-18"
      },
      "inferredDates": ["meeting_date", "follow_up_date"]
    },
    {
      "text": "Sim, as duas datas estão corretas.",
      "confirmedDates": ["meeting_date", "follow_up_date"],
      "fields": {}
    }
  ],
  "expectations": [
    {
      "action": "confirm_dates",
      "state": "WAITING_FOR_CONFIRMATION",
      "missing": ["meeting_date", "follow_up_date"]
    },
    {"action": "generate", "state": "DONE", "missing": []}
  ]
}
```

Add this correction case:

```json
{
  "id": "relative-date-can-be-corrected",
  "invoked": true,
  "turns": [
    {
      "text": "A reunião foi ontem.",
      "fields": {
        "company": "Acme",
        "meeting_date": "2026-09-14",
        "contacts": ["Ana"],
        "visit_type": "negociação",
        "topics_discussed": ["Contrato"],
        "next_steps": "Nenhum próximo passo definido",
        "follow_up_date": "Não haverá follow up"
      },
      "inferredDates": ["meeting_date"]
    },
    {
      "text": "Não. A data correta foi 13/09/2026.",
      "fields": {"meeting_date": "2026-09-13"},
      "confirmedDates": ["meeting_date"]
    }
  ],
  "expectations": [
    {
      "action": "confirm_dates",
      "state": "WAITING_FOR_CONFIRMATION",
      "missing": ["meeting_date"]
    },
    {"action": "generate", "state": "DONE", "missing": []}
  ]
}
```

- [ ] **Step 2: Add a failing negated-override scenario**

```json
{
  "id": "negated-override-phrase-does-not-generate",
  "invoked": true,
  "turns": [{
    "text": "Não quero continuar mesmo assim.",
    "fields": {"company": "Acme"}
  }],
  "expectations": [{
    "action": "ask_missing",
    "state": "WAITING_FOR_MISSING",
    "missing": ["meeting_date", "contacts", "visit_type", "topics_discussed", "next_steps", "follow_up_date"]
  }]
}
```

- [ ] **Step 3: Run the tests and verify both behaviors fail**

Run: `python3 scripts/test_flow.py`

Expected: the date case generates before confirmation and the negated phrase incorrectly enters `DONE_WITH_GAPS`.

- [ ] **Step 4: Track pending inferred dates in `simulate`**

Change `missing_fields` to accept pending confirmations:

```python
def missing_fields(record: dict[str, Any], unconfirmed_dates: set[str]) -> list[str]:
    return [
        field["id"]
        for field in FIELD_SCHEMA["fields"]
        if field["required"]
        and (
            field["id"] in unconfirmed_dates
            or not field_is_complete(field, record.get(field["id"]))
        )
    ]
```

Initialize and update confirmation state in `simulate`:

```python
unconfirmed_dates: set[str] = set()

for turn in case["turns"]:
    record = merge_record(record, turn.get("fields", {}))
    unconfirmed_dates.update(turn.get("inferredDates", []))
    unconfirmed_dates.difference_update(turn.get("confirmedDates", []))
    missing = missing_fields(record, unconfirmed_dates)

    if missing and contains_override(turn.get("text", "")):
        action = "generate"
        state = "DONE_WITH_GAPS"
    elif unconfirmed_dates:
        action = "confirm_dates"
        state = "WAITING_FOR_CONFIRMATION"
    elif missing:
        action = "ask_missing"
        state = "WAITING_FOR_MISSING"
    else:
        action = "generate"
        state = "DONE"
```

An override never turns an inferred date into a confirmed fact. A valid override may generate `DONE_WITH_GAPS`, but the unconfirmed date must remain in the missing-field list and must not be rendered as confirmed.

- [ ] **Step 5: Reject explicit negation near an override phrase**

Replace `contains_override` with:

```python
def contains_override(text: str) -> bool:
    normalized_text = normalize(text)
    words = normalized_text.split()
    for phrase in OVERRIDE_PHRASES:
        phrase_words = phrase.split()
        width = len(phrase_words)
        for index in range(len(words) - width + 1):
            if words[index:index + width] != phrase_words:
                continue
            nearby_prefix = words[max(0, index - 4):index]
            if "nao" in nearby_prefix or "nunca" in nearby_prefix:
                continue
            return True
    return False
```

Keep scenario phrases free of trailing punctuation inside configured values; tokenization of the user message should strip surrounding punctuation before comparison. Extend `normalize` with:

```python
value = re.sub(r"[^\w\s]", " ", value)
return re.sub(r"\s+", " ", value).strip()
```

- [ ] **Step 6: Run the complete harness**

Run: `python3 scripts/test_flow.py`

Expected: all scenarios PASS, including confirmation, correction, affirmative override, ambiguous consent, and negated override.

- [ ] **Step 7: Commit only if explicitly authorized**

If authorized:

```bash
git add scripts/test_flow.py tests/scenarios.json skills/relatorio-reuniao/references/validation-rules.json
git commit -m "fix: confirm inferred dates before reporting"
```

## Task 4: Align Skill Instructions, State Machine, Intake, And Report Template

**Files:**

- Modify: `scripts/test_flow.py:128-214`
- Modify: `skills/relatorio-reuniao/SKILL.md`
- Modify: `skills/relatorio-reuniao/references/workflow.md`
- Modify: `skills/relatorio-reuniao/assets/intake-message.md`
- Modify: `skills/relatorio-reuniao/assets/meeting-report-template.md`
- Modify: `skills/relatorio-reuniao/assets/report-delivery-guidance.md`

- [ ] **Step 1: Add failing static and rendered-output checks**

Extend the existing `required_skill_concepts` tuple with these entries; retain the existing generation-gate and active-record assertions:

```python
required_skill_concepts = (
    "@documentar reunião",
    "active report record",
    "assets/intake-message.md",
    "references/field-schema.json",
    "confirm",
    "nenhum próximo passo definido",
    "não haverá follow up",
    "in the same turn",
)
```

Add exact intake checks:

```python
intake = (SKILL_ROOT / "assets/intake-message.md").read_text(encoding="utf-8")
required_intake_labels = (
    "empresa (cliente)",
    "data da reunião/visita",
    "pessoa(s) de contato",
    "corretiva, preventiva, desenvolvimento ou negociação",
    "assuntos discutidos",
    "responsável por cada ação",
    "data para follow up",
)
for label in required_intake_labels:
    if label.casefold() not in intake.casefold():
        raise AssertionError(f"intake is missing required content: {label}")
```

Add template checks:

```python
template = (SKILL_ROOT / "assets/meeting-report-template.md").read_text(encoding="utf-8")
required_placeholders = (
    "{{company}}",
    "{{meeting_date}}",
    "{{contacts}}",
    "{{visit_type}}",
    "{{follow_up_date}}",
    "{{topics_discussed}}",
    "{{next_steps}}",
)
for placeholder in required_placeholders:
    if placeholder not in template:
        raise AssertionError(f"report template is missing {placeholder}")
if "Pendências de informação" in template:
    raise AssertionError("complete report template must not contain an unconditional pending section")
```

Add dependency-free rendering helpers so the harness checks user-facing output rather than actions alone:

```python
def render_intake() -> str:
    return (SKILL_ROOT / "assets/intake-message.md").read_text(encoding="utf-8").strip()


def render_report(record: dict[str, Any], missing: list[str]) -> str:
    template = (SKILL_ROOT / "assets/meeting-report-template.md").read_text(encoding="utf-8")
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}

    def value_or_missing(field_id: str) -> Any:
        if field_id in missing:
            return FIELD_SCHEMA["missingValue"]
        return record.get(field_id, FIELD_SCHEMA["missingValue"])

    contact_values = value_or_missing("contacts")
    contacts = ", ".join(contact_values) if isinstance(contact_values, list) else contact_values
    topic_values = value_or_missing("topics_discussed")
    topics = (
        "\n".join(f"- {item}" for item in topic_values)
        if isinstance(topic_values, list)
        else topic_values
    )
    next_steps = value_or_missing("next_steps")
    if isinstance(next_steps, list):
        rows = ["| Ação | Responsável |", "| --- | --- |"]
        rows.extend(f"| {item['action']} | {item['responsible']} |" for item in next_steps)
        rendered_steps = "\n".join(rows)
    else:
        rendered_steps = next_steps or FIELD_SCHEMA["missingValue"]

    values = {
        "company": value_or_missing("company"),
        "meeting_date": value_or_missing("meeting_date"),
        "contacts": contacts or FIELD_SCHEMA["missingValue"],
        "visit_type": value_or_missing("visit_type"),
        "follow_up_date": value_or_missing("follow_up_date"),
        "topics_discussed": topics or FIELD_SCHEMA["missingValue"],
        "next_steps": rendered_steps,
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))

    if missing:
        pending = "\n".join(f"- {labels[field_id]}" for field_id in missing)
        template += f"\n\n## Pendências de informação\n\n{pending}\n"
    return template.strip()
```

Have intake branches return:

```python
return [{
    "action": "send_intake",
    "state": "INTAKE",
    "missing": [],
    "output": render_intake(),
}]
```

Before appending each collection result, render output only for generation:

```python
output = render_report(record, missing) if action == "generate" else ""
results.append({
    "action": action,
    "state": state,
    "missing": missing,
    "output": output,
})
```

Replace exact whole-dictionary comparison with an expectation matcher that checks existing keys and optional output fragments:

```python
def expectation_matches(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    required = expected.get("outputContains", [])
    forbidden = expected.get("outputNotContains", [])
    core = {
        key: value
        for key, value in expected.items()
        if key not in {"outputContains", "outputNotContains"}
    }
    output = actual.get("output", "")
    return (
        all(actual.get(key) == value for key, value in core.items())
        and all(fragment in output for fragment in required)
        and all(fragment not in output for fragment in forbidden)
    )
```

For both intake scenarios, add all seven labels under `outputContains`. For the explicit-none scenario, require `Nenhum próximo passo definido` and `Não haverá follow up`. For the override scenario, require `Pendências de informação` and every missing field label. For a normal complete-report scenario, put `Pendências de informação` under `outputNotContains`.

- [ ] **Step 2: Run the harness and verify it fails for missing new behavior**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because the current skill preserves relative dates instead of requiring confirmation, lacks the two canonical negative outputs, and the template contains an unconditional pending section and `{{next_steps_table}}`.

- [ ] **Step 3: Update `SKILL.md` without duplicating resource contents**

Keep the orchestration concise and make these rules explicit:

```markdown
Before the first workflow response, read `references/workflow.md`,
`references/field-schema.json`, `references/validation-rules.json`,
`assets/intake-message.md`, `assets/meeting-report-template.md`, and
`assets/report-delivery-guidance.md` relative to this skill directory.

Resolve relative meeting and follow-up dates from the conversation date, show
the resolved calendar dates, and wait for confirmation before generation.
Never infer companies, contacts, visit types, topics, actions, or owners.

Treat an explicit statement that no next steps exist as the canonical value
`Nenhum próximo passo definido`. Treat an explicit statement that no follow up
will occur as `Não haverá follow up`. These exceptions apply only to those two
fields.
```

Remove the instruction that relative dates may simply be preserved without confirmation.

- [ ] **Step 4: Add date confirmation to the state machine**

Add this state to `workflow.md`:

```markdown
| `WAITING_FOR_CONFIRMATION` | A relative date was resolved but not confirmed. | Show each resolved date and ask whether it is correct. |
```

Add transitions:

```text
VALIDATING -- inferred date --> WAITING_FOR_CONFIRMATION
WAITING_FOR_CONFIRMATION -- confirmed or corrected dates --> COLLECTING
```

State that pending date confirmation blocks complete generation and cannot be silently converted into a confirmed fact.

- [ ] **Step 5: Make the report template complete-only**

Use:

```markdown
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
```

In `SKILL.md`, instruct the model to append `## Pendências de informação` only on `DONE_WITH_GAPS` and list every missing required label there.

- [ ] **Step 6: Update intake and delivery guidance**

Keep all seven intake categories. Add one concise sentence:

```markdown
Se você usar datas relativas, como “ontem” ou “sexta que vem”, eu mostrarei as datas interpretadas para sua confirmação.
```

Update delivery guidance so complete reports never mention pending information and overridden reports always do.

Use this body:

```markdown
# Orientação após o relatório

## Relatório completo

✅ **Todas as informações necessárias foram preenchidas.**

O relatório está pronto para ser revisado e compartilhado. Revise nomes,
datas e responsáveis antes de copiar o conteúdo para um e-mail, WhatsApp,
CRM ou registro interno.

## Relatório com pendências

⚠️ **O relatório foi gerado como rascunho com informações pendentes.**

Liste todas as pendências depois do relatório. O rascunho deve ser completado
e revisado antes de ser compartilhado como versão final.

O plugin não envia mensagens nem grava o relatório em outros sistemas.
```

- [ ] **Step 7: Run the complete harness**

Run: `python3 scripts/test_flow.py`

Expected: all package, content, and flow checks PASS.

- [ ] **Step 8: Commit only if explicitly authorized**

If authorized:

```bash
git add scripts/test_flow.py skills/relatorio-reuniao
git commit -m "fix: align meeting workflow and report output"
```

## Task 5: Align Metadata, Manifests, And Documentation

**Files:**

- Modify: `scripts/test_flow.py`
- Modify: `plugin.json`
- Modify: `.codex-plugin/plugin.json`
- Modify: `skills/relatorio-reuniao/agents/openai.yaml`
- Modify: `README.md`

- [ ] **Step 1: Add failing manifest consistency checks**

Add:

```python
portable_manifest = load_json("plugin.json")
compat_manifest = load_json(".codex-plugin/plugin.json")

if portable_manifest["name"] != compat_manifest["name"]:
    raise AssertionError("plugin manifests must use the same name")
if portable_manifest["version"] != compat_manifest["version"]:
    raise AssertionError("plugin manifests must use the same version")

portable_interface = portable_manifest["extensions"]["com.openai"]["interface"]
compat_interface = compat_manifest["interface"]
for key in ("displayName", "shortDescription", "longDescription"):
    if portable_interface[key] != compat_interface[key]:
        raise AssertionError(f"plugin manifests disagree on interface.{key}")
```

- [ ] **Step 2: Run the harness and verify the version mismatch fails**

Run: `python3 scripts/test_flow.py`

Expected: FAIL because root `plugin.json` is `0.1.1` and `.codex-plugin/plugin.json` has a different compatibility version.

- [ ] **Step 3: Set one new version in both manifests**

Use `0.2.0` in both manifests because the package structure and workflow contract change. Keep technical name `gpt-workflows` and displayed name `Documentar Reunião`.

Set `description` in both manifests to this exact text:

```text
Registre reuniões e visitas comerciais, complete os campos obrigatórios e gere um relatório estruturado.
```

Set `interface.longDescription` in both manifests to:

```text
Cole ou dite as anotações de uma reunião comercial. O workflow coleta os campos obrigatórios, confirma datas inferidas, pergunta somente o que faltar e gera um relatório estruturado.
```

The compatibility manifest keeps `"skills": "./skills/"`. The portable manifest continues standard `skills/` discovery and does not add this legacy field.

- [ ] **Step 4: Simplify the starter prompt in `openai.yaml`**

Use a direct activation prompt:

```yaml
interface:
  display_name: "Documentar Reunião"
  short_description: "Registre uma reunião e gere um relatório estruturado."
  default_prompt: "Começar a documentar uma reunião."

policy:
  allow_implicit_invocation: true
```

The starter prompt should not attempt to reproduce the complete workflow; `SKILL.md` and its resources own that behavior.

- [ ] **Step 5: Update README paths and acceptance boundaries**

Replace the package tree and testing guidance so they include this exact structure and acceptance boundary:

```text
skills/relatorio-reuniao/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── workflow.md
│   ├── field-schema.json
│   └── validation-rules.json
└── assets/
    ├── intake-message.md
    ├── meeting-report-template.md
    └── report-delivery-guidance.md
```

```markdown
## Acceptance surfaces

ChatGPT is the primary acceptance surface. Select the real
`@Documentar Reunião` entry from the composer menu when testing explicit
invocation. Codex `$relatorio-reuniao` is an auxiliary package-loading check.

Before submission, validate the local marketplace installation in a new
ChatGPT conversation. Android testing occurs only after the plugin is publicly
listed and the customer installs that public listing.

Explicitly stating that there are no next steps or that no follow up will
occur completes only those respective fields. Relative dates are resolved from
conversation context and must be confirmed before report generation.
```

Ensure the surrounding README also reflects:

- self-contained skill paths;
- ChatGPT `@` selection as the primary explicit path;
- Codex `$relatorio-reuniao` as secondary development validation;
- local ChatGPT acceptance before submission;
- Android testing only after public marketplace publication and customer installation;
- field-specific explicit absence for next steps and follow up;
- confirmation of inferred dates.

Remove statements that resources live at root or that a literal plain-text `@Documentar Reunião` is guaranteed to carry the same host representation as selecting the skill from the `@` menu.

- [ ] **Step 6: Run syntax and contract checks**

Run:

```bash
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 scripts/test_flow.py
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); puts "YAML OK"'
```

Expected: JSON commands exit 0, all flow scenarios PASS, and output contains `YAML OK`.

- [ ] **Step 7: Commit only if explicitly authorized**

If authorized:

```bash
git add plugin.json .codex-plugin/plugin.json skills/relatorio-reuniao/agents/openai.yaml README.md scripts/test_flow.py
git commit -m "docs: align plugin metadata and testing guidance"
```

## Task 6: Verify The Installed Package And Direct Skill Loading

**Files:**

- Create: `tests/chatgpt-acceptance.md`
- Verify only: installed cache under `~/.codex/plugins/cache/personal/gpt-workflows/0.2.0/`

- [ ] **Step 1: Create the acceptance record before reinstalling**

Create `tests/chatgpt-acceptance.md` with:

```markdown
# ChatGPT Acceptance Record

## Build

- Plugin version: 0.2.0
- Marketplace: personal
- Source verification: pending
- Installed-cache verification: pending

## Local ChatGPT Scenarios

| Scenario | Result | Evidence |
| --- | --- | --- |
| Start checklist | Pending | |
| Complete first turn | Pending | |
| Missing-field follow-up | Pending | |
| Relative-date confirmation | Pending | |
| Explicit no next steps/follow up | Pending | |
| Explicit incomplete override | Pending | |

## Post-Publication Android

Not executed before public marketplace publication. Record separately after the customer installs the public listing.
```

- [ ] **Step 2: Remove and reinstall the local plugin version**

Run:

```bash
codex plugin remove gpt-workflows@personal
codex plugin add gpt-workflows@personal
codex plugin list
```

Expected: `gpt-workflows@personal` is `installed, enabled` at version `0.2.0`.

- [ ] **Step 3: Verify cache identity**

Run:

```bash
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.2.0
```

Expected: no output and exit code 0.

- [ ] **Step 4: Run the auxiliary Codex invocation outside the repository**

Run from a directory that cannot expose the source tree as an accidental fallback:

```bash
codex exec --ephemeral --skip-git-repo-check --sandbox read-only \
  -C /var/folders/d0/5f_2fp6n7hggyyd8p50mgcq00000gn/T/opencode \
  '$relatorio-reuniao começar'
```

Expected:

- the skill reads `skills/relatorio-reuniao/SKILL.md` from the installed cache;
- every resource read targets `skills/relatorio-reuniao/assets/` or `skills/relatorio-reuniao/references/`;
- no `No such file or directory`, recovery search, or generic opener appears;
- the final answer contains all seven intake categories.

- [ ] **Step 5: Record installed-package evidence**

Replace the two `pending` values under `Build` in `tests/chatgpt-acceptance.md` with `passed` only after the corresponding commands succeed. Do not mark the ChatGPT scenario table yet.

- [ ] **Step 6: Commit only if explicitly authorized**

If authorized:

```bash
git add tests/chatgpt-acceptance.md
git commit -m "test: add ChatGPT acceptance record"
```

## Task 7: Execute Pre-Submission ChatGPT Acceptance

**Files:**

- Modify: `tests/chatgpt-acceptance.md`

- [ ] **Step 1: Restart ChatGPT and refresh the local plugin**

Quit ChatGPT completely, reopen it, refresh the Plugins Directory, and confirm that installed plugin version `0.2.0` is selected from marketplace `personal`.

- [ ] **Step 2: Verify the actual `@` selection**

In a new conversation, type `@`, select `Documentar Reunião` from the menu, append `começar`, and send. Do not use manually typed plain text as the only evidence of explicit selection.

Expected first response includes:

```text
empresa (cliente)
data da reunião/visita
pessoa(s) de contato
corretiva, preventiva, desenvolvimento ou negociação
assuntos discutidos
próximos passos, com o responsável por cada ação
data para follow up
```

- [ ] **Step 3: Test complete notes in a new conversation**

Select the skill and send:

```text
Empresa Acme. Reunião em 15/09/2026 com Ana. Tipo negociação.
Discutimos a renovação do contrato. Bruno enviará a proposta revisada.
O follow up será em 18/09/2026.
```

Expected: complete report in the same response, including action `Enviar a proposta revisada` and responsible person `Bruno`, with no pending-information section.

- [ ] **Step 4: Test missing-field collection in a new conversation**

Select the skill and send:

```text
Reunião com a empresa Beta em 15/09/2026. O contato foi Carla.
```

Expected: asks only for type, topics, next steps with responsible people, and follow-up date. After supplying them, generates the report without asking again for company, meeting date, or contact.

- [ ] **Step 5: Test relative-date confirmation in a new conversation**

Select the skill and provide otherwise complete notes using `ontem` for the meeting date and `sexta que vem` for follow up.

Expected: shows both inferred calendar dates and waits for confirmation. It generates only after confirmation or correction.

- [ ] **Step 6: Test valid explicit absence in a new conversation**

Provide all other required fields and state:

```text
Não existem próximos passos e não haverá follow up.
```

Expected: complete report containing `Nenhum próximo passo definido` and `Não haverá follow up`.

- [ ] **Step 7: Test incomplete override in a new conversation**

Provide only company and meeting date, then send:

```text
Gerar mesmo com pendências.
```

Expected: visibly incomplete draft containing a `Pendências de informação` section with every unresolved required field.

- [ ] **Step 8: Update acceptance evidence**

For each scenario, replace `Pending` only after observing the expected behavior and add the conversation identifier, transcript path, or screenshot reference in the evidence column. Any failure remains recorded as `Failed` with the exact observed response.

- [ ] **Step 9: Run the final local verification suite**

Run:

```bash
python3 scripts/test_flow.py
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
ruby -e 'require "yaml"; YAML.safe_load_file("skills/relatorio-reuniao/agents/openai.yaml", aliases: false); puts "YAML OK"'
diff -rq --exclude=.git . ~/.codex/plugins/cache/personal/gpt-workflows/0.2.0
git status --short
```

Expected: all scenarios PASS, JSON and YAML syntax checks exit 0, cache diff is empty, and `git status` shows only intended project files.

- [ ] **Step 10: Review submission readiness**

Confirm that the public listing has real publisher identity, website, support, privacy, and terms information required by the current submission portal. Do not invent URLs or mark the plugin ready while required publisher fields are absent.

The implementation milestone ends at `ready for submission`. Do not mark Android testing complete.

- [ ] **Step 11: Commit only if explicitly authorized**

If authorized:

```bash
git add tests/chatgpt-acceptance.md
git commit -m "test: record local ChatGPT acceptance"
```

## Post-Publication Android Smoke Test

This is not part of pre-submission implementation and must not be executed or marked complete before public marketplace publication.

After the plugin is publicly listed and the customer installs that public listing in ChatGPT for Android:

1. Select `@Documentar Reunião` and send `começar`; verify the complete checklist.
2. Run one partial-information flow; verify that only missing fields are requested.
3. Run one complete flow; verify the structured report.
4. Record the public plugin version, Android ChatGPT version, transcript, and result.
5. If Android differs from local ChatGPT, diagnose mention selection, installed version, and host representation before changing the skill.
