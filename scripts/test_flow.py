#!/usr/bin/env python3
"""Run dependency-free offline checks for the relatorio-reuniao conversation contract."""

from __future__ import annotations

import json
import re
import struct
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills/relatorio-reuniao"
SKILL_PATH = SKILL_ROOT / "SKILL.md"


def load_json(relative_path: str) -> dict[str, Any]:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def load_skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def extract_skill_section(name: str) -> str:
    text = load_skill_text()
    start = f"<!-- {name}_START -->"
    end = f"<!-- {name}_END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise AssertionError(f"SKILL.md must contain one marked section: {name}")
    start_index = text.index(start) + len(start)
    end_index = text.index(end)
    if end_index <= start_index:
        raise AssertionError(f"SKILL.md has invalid marker order: {name}")
    return text[start_index:end_index].strip()


def load_embedded_json(name: str) -> dict[str, Any]:
    section = extract_skill_section(name)
    if section.startswith("```json") and section.endswith("```"):
        section = section[len("```json") : -len("```")].strip()
    return json.loads(section)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.casefold().strip()
    value = re.sub(r"[^\w\s]", " ", value)
    return re.sub(r"\s+", " ", value)


def is_substantive(value: Any, sentinels: set[str]) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        normalized = normalize(value)
        return bool(normalized) and normalized not in sentinels
    if isinstance(value, list):
        return any(is_substantive(item, sentinels) for item in value)
    if isinstance(value, dict):
        return any(is_substantive(item, sentinels) for item in value.values())
    return True


def contains_explicit_negative(value: Any) -> bool:
    if isinstance(value, str):
        return normalize(value) in EXPLICIT_NEGATIVE_VALUES
    if isinstance(value, list):
        return any(contains_explicit_negative(item) for item in value)
    if isinstance(value, dict):
        return any(contains_explicit_negative(item) for item in value.values())
    return False


def merge_record(record: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(record)
    for field_id, value in incoming.items():
        merged[field_id] = value
    return merged


def is_absolute_date(value: Any, date_formats: list[str]) -> bool:
    if not isinstance(value, str):
        return False
    formats = {"YYYY-MM-DD": "%Y-%m-%d", "DD/MM/YYYY": "%d/%m/%Y"}
    for date_format in date_formats:
        try:
            datetime.strptime(value, formats[date_format])
            return True
        except (KeyError, ValueError):
            continue
    return False


def field_is_complete(field: dict[str, Any], value: Any) -> bool:
    explicit_none = field.get("explicitNoneValue")
    if (
        field.get("allowExplicitNone")
        and isinstance(value, str)
        and normalize(value) == normalize(explicit_none)
    ):
        return True
    if contains_explicit_negative(value):
        return False

    if not is_substantive(value, MISSING_SENTINELS):
        return False
    validation = field.get("validation", {})
    if validation.get("kind") == "absolute_date":
        return is_absolute_date(value, validation.get("formats", []))
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
            and all(
                isinstance(item, str)
                and is_substantive(item, MISSING_SENTINELS)
                for item in value
            )
        )
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
                    item_field_types.get(item_field) == "string"
                    and isinstance(item.get(item_field), str)
                    and is_substantive(item.get(item_field), MISSING_SENTINELS)
                    for item_field in item_fields
                )
                for item in value
            )
        )
    raise AssertionError(f"unsupported field type: {field_type}")


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


def contains_override(text: str) -> bool:
    for quoted_span in (r'"[^"]*"', r"'[^']*'", r"“[^”]*”", r"‘[^’]*’"):
        text = re.sub(quoted_span, " ", text)
    affirmative_prefixes = (
        ("pode",),
        ("sim",),
        ("confirmo",),
        ("quero",),
        ("desejo",),
        ("vamos",),
        ("por", "favor"),
        ("gostaria", "de"),
    )
    non_affirmative_words = {
        "acontece",
        "explique",
        "hipoteticamente",
        "significa",
        "significado",
        "seria",
        "possivel",
        "talvez",
    }
    for raw_clause in re.split(r"[,;.!?\n]+", text):
        words = normalize(raw_clause).split()
        for phrase in OVERRIDE_PHRASES:
            phrase_words = phrase.split()
            width = len(phrase_words)
            for index in range(len(words) - width + 1):
                if words[index : index + width] != phrase_words:
                    continue
                prefix = words[:index]
                if "nao" in prefix or "nunca" in prefix:
                    continue
                if "se" in prefix or "caso" in prefix:
                    continue
                if non_affirmative_words.intersection(words):
                    continue
                if prefix and not any(
                    prefix[-len(allowed) :] == list(allowed)
                    for allowed in affirmative_prefixes
                ):
                    continue
                return True
    return False


def render_intake() -> str:
    return extract_skill_section("INTAKE")


def render_field_prompt(field_ids: list[str], clarification: bool = False) -> str:
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}
    prefix = "Preciso esclarecer" if clarification else "Por favor, informe"
    return f"{prefix}: " + "; ".join(labels[field_id] for field_id in field_ids) + "."


def render_date_confirmation(record: dict[str, Any], field_ids: set[str]) -> str:
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}
    dates = "; ".join(
        f"{labels[field_id]}: {record[field_id]}"
        for field_id in FIELD_IDS
        if field_id in field_ids
    )
    return f"Confirme as datas interpretadas: {dates}. Estão corretas?"


def render_delivery_guidance(incomplete: bool) -> str:
    section = "INCOMPLETE_GUIDANCE" if incomplete else "COMPLETE_GUIDANCE"
    return extract_skill_section(section)


def render_report(record: dict[str, Any], missing: list[str]) -> str:
    template = extract_skill_section("REPORT_TEMPLATE")
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}

    def value_or_missing(field_id: str) -> Any:
        if field_id in missing:
            return FIELD_SCHEMA["missingValue"]
        return record.get(field_id, FIELD_SCHEMA["missingValue"])

    contact_values = value_or_missing("contacts")
    contacts = (
        ", ".join(contact_values)
        if isinstance(contact_values, list)
        else contact_values
    )
    topic_values = value_or_missing("topics_discussed")
    topics = (
        "\n".join(f"- {item}" for item in topic_values)
        if isinstance(topic_values, list)
        else topic_values
    )
    provided_details = record.get("provided_details")
    provided_details_section = ""
    if isinstance(provided_details, list) and provided_details:
        rendered_details = "\n".join(f"- {item}" for item in provided_details)
        provided_details_section = f"\n\n## Registro detalhado\n\n{rendered_details}"
    next_steps = value_or_missing("next_steps")
    if isinstance(next_steps, list):
        rows = ["| Ação | Responsável |", "| --- | --- |"]
        rows.extend(
            f"| {item['action']} | {item['responsible']} |" for item in next_steps
        )
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
        "provided_details_section": provided_details_section,
        "next_steps": rendered_steps,
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", str(value))

    if missing:
        pending = "\n".join(f"- {labels[field_id]}" for field_id in missing)
        template += f"\n\n## Pendências de informação\n\n{pending}\n"
    guidance = render_delivery_guidance(bool(missing))
    return f"{guidance}\n\n```markdown\n{template.strip()}\n```"


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


def expectation_matches(
    actual: dict[str, Any], expected: dict[str, Any]
) -> bool:
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


def is_start_only_explicit_mention(text: str) -> bool:
    normalized_text = normalize(text)
    marker = normalize("@Documentar Reunião")
    if not normalized_text.startswith(marker):
        return False
    suffix = normalized_text[len(marker):].strip()
    return suffix in {"", "comecar", "iniciar", "start"}


def simulate(case: dict[str, Any]) -> list[dict[str, Any]]:
    activation = case.get("activation")
    if activation is None and case.get("invoked"):
        activation = "explicit_invocation"
    if activation not in {"explicit_invocation", "explicit_mention", "plugin_selected"}:
        raise AssertionError(
            f"{case['id']}: scenario must model plugin selection, explicit invocation, or explicit mention"
        )

    if not case["turns"]:
        return [
            {
                "action": "send_intake",
                "state": "INTAKE",
                "missing": [],
                "output": render_intake(),
            }
        ]

    if (
        activation == "explicit_mention"
        and not case["turns"][0].get("fields")
        and is_start_only_explicit_mention(case["turns"][0].get("text", ""))
    ):
        return [
            {
                "action": "send_intake",
                "state": "INTAKE",
                "missing": [],
                "output": render_intake(),
            }
        ]

    record: dict[str, Any] = {}
    unconfirmed_dates: set[str] = set()
    conflicting_fields: set[str] = set()
    results = []
    for turn in case["turns"]:
        incoming = turn.get("fields", {})
        inferred_dates = set(turn.get("inferredDates", []))
        record = merge_record(record, incoming)
        corrected_dates = DATE_FIELD_IDS.intersection(incoming) - inferred_dates
        unconfirmed_dates.difference_update(corrected_dates)
        unconfirmed_dates.update(inferred_dates)
        unconfirmed_dates.difference_update(turn.get("confirmedDates", []))
        conflicting_fields.difference_update(incoming)
        conflicting_fields.update(turn.get("conflictingFields", []))
        missing = missing_fields(record, unconfirmed_dates | conflicting_fields)
        if missing and contains_override(turn.get("text", "")):
            action = "generate"
            state = "DONE_WITH_GAPS"
        elif conflicting_fields:
            action = "ask_clarification"
            state = "WAITING_FOR_CLARIFICATION"
        elif unconfirmed_dates:
            action = "confirm_dates"
            state = "WAITING_FOR_CONFIRMATION"
        elif missing:
            action = "ask_missing"
            state = "WAITING_FOR_MISSING"
        else:
            action = "generate"
            state = "DONE"
        if action == "generate":
            output = render_report(record, missing)
        elif action == "confirm_dates":
            output = render_date_confirmation(record, unconfirmed_dates)
        elif action == "ask_clarification":
            conflicts = [
                field_id for field_id in FIELD_IDS if field_id in conflicting_fields
            ]
            output = render_field_prompt(conflicts, clarification=True)
        else:
            output = render_field_prompt(missing)
        results.append(
            {"action": action, "state": state, "missing": missing, "output": output}
        )
    return results


def check_packaging() -> None:
    for section in (
        "INTAKE",
        "FIELD_SCHEMA",
        "VALIDATION_RULES",
        "PARTIAL_EXAMPLE",
        "DETAIL_FIDELITY_EXAMPLE",
        "REPORT_TEMPLATE",
        "COMPLETE_GUIDANCE",
        "INCOMPLETE_GUIDANCE",
    ):
        extract_skill_section(section)

    required_paths = [
        "plugin.json",
        ".codex-plugin/plugin.json",
        "skills/relatorio-reuniao/SKILL.md",
        "skills/relatorio-reuniao/agents/openai.yaml",
        "tests/scenarios.json",
        "tests/chatgpt-acceptance.md",
        "assets/logo.png",
        "PRIVACY.md",
        "TERMS.md",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"missing package files: {', '.join(missing)}")

    logo = (ROOT / "assets/logo.png").read_bytes()
    if logo[:8] != b"\x89PNG\r\n\x1a\n" or logo[12:16] != b"IHDR":
        raise AssertionError("assets/logo.png must be a valid PNG")
    width, height = struct.unpack(">II", logo[16:24])
    if width != height:
        raise AssertionError("assets/logo.png must be square")

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
        missing_phrases = [
            phrase for phrase in required_phrases if phrase not in text
        ]
        if missing_phrases:
            raise AssertionError(f"{path} is missing mandatory public statements")
    for obsolete in (
        ROOT / "references",
        SKILL_ROOT / "assets",
        SKILL_ROOT / "references",
    ):
        if obsolete.exists():
            raise AssertionError(
                "runtime contract must live only in SKILL.md: "
                + str(obsolete.relative_to(ROOT))
            )
    for forbidden in ("mcp.json", ".mcp.json", ".app.json"):
        if (ROOT / forbidden).exists():
            raise AssertionError(f"forbidden integration file present: {forbidden}")

    portable_manifest = load_json("plugin.json")
    compat_manifest = load_json(".codex-plugin/plugin.json")
    expected_version = "0.3.3"
    expected_developer = "João Eduardo Ferreira Bertacchi"
    expected_author_url = "https://github.com/joaobertacchi"
    expected_repository = "https://github.com/joaobertacchi/gpt-workflows"
    expected_interface = {
        "websiteURL": expected_repository,
        "privacyPolicyURL": f"{expected_repository}/blob/main/PRIVACY.md",
        "termsOfServiceURL": f"{expected_repository}/blob/main/TERMS.md",
        "logo": "./assets/logo.png",
    }

    if portable_manifest["name"] != compat_manifest["name"]:
        raise AssertionError("plugin manifests must use the same name")
    if portable_manifest["version"] != compat_manifest["version"]:
        raise AssertionError("plugin manifests must use the same version")
    if portable_manifest["version"] != expected_version:
        raise AssertionError("public submission package must ship as version 0.3.3")
    if portable_manifest["author"]["name"] != expected_developer:
        raise AssertionError("portable manifest must use the verified developer name")
    if compat_manifest["author"]["name"] != expected_developer:
        raise AssertionError("compatibility manifest must use the verified developer name")
    if portable_manifest["author"].get("url") != expected_author_url:
        raise AssertionError("portable manifest must publish the developer URL")
    if compat_manifest["author"].get("url") != expected_author_url:
        raise AssertionError("compatibility manifest must publish the developer URL")
    if portable_manifest.get("homepage") != expected_repository:
        raise AssertionError("portable manifest must publish the repository homepage")
    if portable_manifest.get("repository") != expected_repository:
        raise AssertionError("portable manifest must publish its repository")

    portable_interface = portable_manifest["extensions"]["com.openai"]["interface"]
    compat_interface = compat_manifest["interface"]
    if portable_interface.get("developerName") != expected_developer:
        raise AssertionError("portable interface must use the verified developer name")
    if compat_interface.get("developerName") != expected_developer:
        raise AssertionError("compatibility interface must use the verified developer name")
    for key, expected in expected_interface.items():
        if portable_interface.get(key) != expected:
            raise AssertionError(f"portable interface has invalid {key}")
        if compat_interface.get(key) != expected:
            raise AssertionError(f"compatibility interface has invalid {key}")
    for key in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
        if portable_interface[key] != compat_interface[key]:
            raise AssertionError(f"plugin manifests disagree on interface.{key}")
    override_starters = [
        prompt
        for prompt in portable_interface["defaultPrompt"]
        if "pendências" in prompt.casefold()
    ]
    if not override_starters or not all(
        contains_override(prompt) for prompt in override_starters
    ):
        raise AssertionError("incomplete-report starters must use an explicit override phrase")

    guidance = "\n".join(
        (
            extract_skill_section("COMPLETE_GUIDANCE"),
            extract_skill_section("INCOMPLETE_GUIDANCE"),
        )
    )
    required_guidance = (
        "Todas as informações necessárias foram preenchidas",
        "copie o conteúdo do relatório",
        "O plugin não envia mensagens",
    )
    missing_guidance = [phrase for phrase in required_guidance if phrase not in guidance]
    if missing_guidance:
        raise AssertionError(
            "SKILL.md is missing required delivery guidance: "
            + ", ".join(missing_guidance)
        )

    invocation_metadata = (
        ROOT / "skills/relatorio-reuniao/agents/openai.yaml"
    ).read_text(encoding="utf-8")
    required_metadata = (
        'display_name: "Documentar Reunião"',
        'default_prompt: "Use $relatorio-reuniao',
        "allow_implicit_invocation: true",
    )
    missing_metadata = [
        phrase
        for phrase in required_metadata
        if phrase.casefold() not in invocation_metadata.casefold()
    ]
    if missing_metadata:
        raise AssertionError(
            "openai.yaml is missing required invocation metadata: "
            + ", ".join(missing_metadata)
        )

    validation_rules = load_embedded_json("VALIDATION_RULES")
    required_validation_keys = {
        "missingSentinels",
        "explicitOverridePhrases",
        "explicitNegativeAnswers",
    }
    missing_validation_keys = sorted(required_validation_keys - validation_rules.keys())
    if missing_validation_keys:
        raise AssertionError(
            "SKILL.md is missing validation data: "
            + ", ".join(missing_validation_keys)
        )

    provided_details_field = next(
        field for field in FIELD_SCHEMA["fields"] if field["id"] == "provided_details"
    )
    if provided_details_field["label"] != "Registro detalhado":
        raise AssertionError(
            "provided_details label must match the required report heading"
        )

    skill_text = (ROOT / "skills/relatorio-reuniao/SKILL.md").read_text(
        encoding="utf-8"
    ).casefold()
    required_skill_concepts = (
        "@documentar reunião",
        "starts a new active report",
        "only these seven fields are required",
        "generate immediately when all fields are valid",
        "do not include a pending section",
        "confirm",
        "nenhum próximo passo definido",
        "não haverá follow up",
        "structured commercial meeting",
        "ontem",
        "time, duration, objective, decisions, success criteria",
    )
    missing_skill_concepts = [
        phrase for phrase in required_skill_concepts if phrase.casefold() not in skill_text
    ]
    if missing_skill_concepts:
        raise AssertionError(
            "SKILL.md is missing strict generation behavior: "
            + ", ".join(missing_skill_concepts)
        )

    intake = extract_skill_section("INTAKE")
    required_intake_labels = (
        "empresa (cliente)",
        "data da reunião/visita",
        "pessoa(s) de contato",
        "corretiva, preventiva, desenvolvimento ou negociação",
        "assuntos discutidos",
        "responsável por cada ação",
        "data para follow up",
    )
    missing_intake_labels = [
        label for label in required_intake_labels if label.casefold() not in intake.casefold()
    ]
    if missing_intake_labels:
        raise AssertionError(
            "intake is missing required content: " + ", ".join(missing_intake_labels)
        )

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

    detail_example = extract_skill_section("DETAIL_FIDELITY_EXAMPLE")
    required_detail_content = (
        "## Registro detalhado",
        "Luciano relatou",
        "Luciano avaliou",
        "Luciano pediu",
        "Eu propus",
    )
    missing_detail_content = [
        phrase for phrase in required_detail_content if phrase not in detail_example
    ]
    if missing_detail_content:
        raise AssertionError(
            "detail fidelity example is missing required attribution: "
            + ", ".join(missing_detail_content)
        )

    template = extract_skill_section("REPORT_TEMPLATE")
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
    missing_placeholders = [
        placeholder for placeholder in required_placeholders if placeholder not in template
    ]
    if missing_placeholders:
        raise AssertionError(
            "report template is missing placeholders: "
            + ", ".join(missing_placeholders)
        )
    if "Pendências de informação" in template:
        raise AssertionError(
            "complete report template must not contain an unconditional pending section"
        )


FIELD_SCHEMA = load_embedded_json("FIELD_SCHEMA")
VALIDATION_RULES = load_embedded_json("VALIDATION_RULES")
FIELD_IDS = [field["id"] for field in FIELD_SCHEMA["fields"]]
DATE_FIELD_IDS = {
    field["id"]
    for field in FIELD_SCHEMA["fields"]
    if field.get("validation", {}).get("kind") == "absolute_date"
}
MISSING_SENTINELS = {normalize(value) for value in VALIDATION_RULES["missingSentinels"]}
EXPLICIT_NEGATIVE_VALUES = {
    normalize(value)
    for values in VALIDATION_RULES["explicitNegativeAnswers"].values()
    for value in values
}
EXPLICIT_NEGATIVE_VALUES.update(
    normalize(field["explicitNoneValue"])
    for field in FIELD_SCHEMA["fields"]
    if field.get("allowExplicitNone")
)
OVERRIDE_PHRASES = [normalize(value) for value in VALIDATION_RULES["explicitOverridePhrases"]]


def main() -> int:
    check_packaging()
    scenarios = load_json("tests/scenarios.json")["cases"]
    failures: list[str] = []
    for case in scenarios:
        actual = simulate(case)
        try:
            for turn in actual:
                if turn["action"] == "generate":
                    assert_copy_boundary(turn["output"])
        except AssertionError as error:
            failures.append(f"{case['id']}: {error}")
            continue
        expected = case["expectations"]
        if len(actual) != len(expected) or not all(
            expectation_matches(actual_item, expected_item)
            for actual_item, expected_item in zip(actual, expected)
        ):
            failures.append(
                f"{case['id']}: expected {json.dumps(expected, ensure_ascii=False)}, "
                f"got {json.dumps(actual, ensure_ascii=False)}"
            )
        else:
            print(f"PASS {case['id']}")

    if failures:
        print("\nFlow checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"\nAll {len(scenarios)} conversational flow scenarios passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
