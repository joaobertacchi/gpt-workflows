#!/usr/bin/env python3
"""Run dependency-free offline checks for the relatorio-reuniao conversation contract."""

from __future__ import annotations

import json
import os
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


def item_value_is_complete(
    item_field: str, value: Any, item_field_types: dict[str, str]
) -> bool:
    kind = item_field_types.get(item_field)
    if kind == "string":
        return isinstance(value, str) and is_substantive(value, MISSING_SENTINELS)
    if kind == "date":
        return is_absolute_date(value, ITEM_DATE_FORMATS)
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
                    item_value_is_complete(
                        item_field, item.get(item_field), item_field_types
                    )
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


def render_date_confirmation(
    record: dict[str, Any],
    field_ids: set[str],
    item_dates: set[tuple[str, int]] | None = None,
) -> str:
    labels = {field["id"]: field["label"] for field in FIELD_SCHEMA["fields"]}
    entries = [
        f"{labels[field_id]}: {record[field_id]}"
        for field_id in FIELD_IDS
        if field_id in field_ids
    ]
    for field_id, item_index in sorted(
        item_dates or set(),
        key=lambda entry: (FIELD_IDS.index(entry[0]), entry[1]),
    ):
        deadline = record[field_id][item_index]["deadline"]
        entries.append(f"{labels[field_id]} #{item_index + 1}: {deadline}")
    return f"Confirme as datas interpretadas: {'; '.join(entries)}. Estão corretas?"


def render_delivery_guidance(incomplete: bool) -> str:
    section = "INCOMPLETE_GUIDANCE" if incomplete else "COMPLETE_GUIDANCE"
    return extract_skill_section(section)


def next_step_cell(value: Any) -> str:
    if (
        isinstance(value, str)
        and is_substantive(value, MISSING_SENTINELS)
        and not contains_explicit_negative(value)
    ):
        return value
    return str(FIELD_SCHEMA["missingValue"])


def next_step_deadline_cell(item: dict[str, Any]) -> str:
    deadline = item.get("deadline")
    if is_absolute_date(deadline, ITEM_DATE_FORMATS):
        return deadline
    return str(FIELD_SCHEMA["missingValue"])


def render_next_steps(record: dict[str, Any]) -> str:
    next_steps = record.get("next_steps")
    if (
        isinstance(next_steps, list)
        and bool(next_steps)
        and all(isinstance(item, dict) for item in next_steps)
    ):
        rows = ["| Ação | Responsável | Prazo |", "| --- | --- | --- |"]
        rows.extend(
            f"| {next_step_cell(item.get('action'))} | "
            f"{next_step_cell(item.get('responsible'))} | "
            f"{next_step_deadline_cell(item)} |"
            for item in next_steps
        )
        return "\n".join(rows)
    if isinstance(next_steps, str):
        return next_steps
    return FIELD_SCHEMA["missingValue"]


def render_report(
    record: dict[str, Any], missing: list[str], artifact_supported: bool
) -> dict[str, Any]:
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
    rendered_steps = render_next_steps(record)

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
    artifact_supported = case.get("artifactSupported", True)
    unconfirmed_dates: set[str] = set()
    unconfirmed_item_dates: set[tuple[str, int]] = set()
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
        if "next_steps" in incoming:
            unconfirmed_item_dates = {
                entry for entry in unconfirmed_item_dates if entry[0] != "next_steps"
            }
            unconfirmed_item_dates.update(
                ("next_steps", index)
                for index in turn.get("inferredNextStepDeadlines", [])
            )
        confirmed_item_dates = set(turn.get("confirmedNextStepDeadlines", []))
        unconfirmed_item_dates = {
            entry
            for entry in unconfirmed_item_dates
            if entry[1] not in confirmed_item_dates
        }
        conflicting_fields.difference_update(incoming)
        conflicting_fields.update(turn.get("conflictingFields", []))
        missing = missing_fields(
            record,
            unconfirmed_dates
            | conflicting_fields
            | {field_id for field_id, _ in unconfirmed_item_dates},
        )
        if missing and contains_override(turn.get("text", "")):
            action = "generate"
            state = "DONE_WITH_GAPS"
        elif conflicting_fields:
            action = "ask_clarification"
            state = "WAITING_FOR_CLARIFICATION"
        elif unconfirmed_dates or unconfirmed_item_dates:
            action = "confirm_dates"
            state = "WAITING_FOR_CONFIRMATION"
        elif missing:
            action = "ask_missing"
            state = "WAITING_FOR_MISSING"
        else:
            action = "generate"
            state = "DONE"
        delivery: dict[str, Any] | None = None
        if action == "generate":
            delivery = render_report(record, missing, artifact_supported)
            output = delivery["output"]
        elif action == "confirm_dates":
            output = render_date_confirmation(
                record, unconfirmed_dates, unconfirmed_item_dates
            )
        elif action == "ask_clarification":
            conflicts = [
                field_id for field_id in FIELD_IDS if field_id in conflicting_fields
            ]
            output = render_field_prompt(conflicts, clarification=True)
        else:
            output = render_field_prompt(missing)
        result = {"action": action, "state": state, "missing": missing, "output": output}
        if delivery is not None:
            result.update(
                artifactName=delivery["artifactName"],
                artifactContent=delivery["artifactContent"],
            )
        results.append(result)
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
        "docs/public-submission.md",
        ".gitignore",
        "scripts/build_public_zip.sh",
    ]
    missing = [path for path in required_paths if not (ROOT / path).is_file()]
    if missing:
        raise AssertionError(f"missing package files: {', '.join(missing)}")

    package_script_path = ROOT / "scripts/build_public_zip.sh"
    if not os.access(package_script_path, os.X_OK):
        raise AssertionError("scripts/build_public_zip.sh must be executable")
    package_script = package_script_path.read_text(encoding="utf-8")
    archive_paths = (
        "plugin.json",
        "assets/logo.png",
        "skills/relatorio-reuniao/SKILL.md",
        "skills/relatorio-reuniao/agents/openai.yaml",
    )
    if any(path not in package_script for path in archive_paths):
        raise AssertionError("public ZIP script must name every approved archive member")
    if "/dist/" not in (ROOT / ".gitignore").read_text(encoding="utf-8"):
        raise AssertionError("generated dist directory must be ignored")

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
    expected_version = "0.3.5"
    expected_developer = "João Eduardo Ferreira Bertacchi"
    expected_author_url = "https://github.com/joaobertacchi"
    expected_repository = "https://github.com/joaobertacchi/gpt-workflows"
    expected_interface = {
        "websiteURL": expected_repository,
        "privacyPolicyURL": f"{expected_repository}/blob/main/PRIVACY.md",
        "termsOfServiceURL": f"{expected_repository}/blob/main/TERMS.md",
        "composerIcon": "./assets/logo.png",
        "logo": "./assets/logo.png",
    }

    if portable_manifest["name"] != compat_manifest["name"]:
        raise AssertionError("plugin manifests must use the same name")
    if portable_manifest["version"] != compat_manifest["version"]:
        raise AssertionError("plugin manifests must use the same version")
    if portable_manifest["version"] != expected_version:
        raise AssertionError(
            f"public submission package must ship as version {expected_version}"
        )
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
    if portable_interface["composerIcon"] != portable_interface["logo"]:
        raise AssertionError(
            "composer icon and logo must reference the same square image"
        )
    for key in ("displayName", "shortDescription", "longDescription", "defaultPrompt"):
        if portable_interface[key] != compat_interface[key]:
            raise AssertionError(f"plugin manifests disagree on interface.{key}")
    expected_short_description = "Documente reuniões comerciais"
    if portable_interface["shortDescription"] != expected_short_description:
        raise AssertionError("public short description must match the approved copy")
    if len(portable_interface["displayName"]) > 30:
        raise AssertionError("public display name must be at most 30 characters")
    if len(portable_interface["shortDescription"]) > 30:
        raise AssertionError("public short description must be at most 30 characters")
    if len(portable_interface["developerName"]) > 80:
        raise AssertionError("public developer name must be at most 80 characters")
    starter_prompts = portable_interface["defaultPrompt"]
    if len(starter_prompts) > 3:
        raise AssertionError("public listing must have at most three starter prompts")
    if any(len(prompt) > 128 for prompt in starter_prompts):
        raise AssertionError("public starter prompts must be at most 128 characters")
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
        "use os controles do artefato",
        "copie o conteúdo do bloco Markdown",
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
        "if the user asks to send or save the report",
        "create or update a native markdown file artifact",
        "relatorio-reuniao.md",
        "do not repeat the complete report inline",
        "if the active surface cannot create or expose a markdown artifact",
    )
    missing_skill_concepts = [
        phrase for phrase in required_skill_concepts if phrase.casefold() not in skill_text
    ]
    if missing_skill_concepts:
        raise AssertionError(
            "SKILL.md is missing strict generation behavior: "
            + ", ".join(missing_skill_concepts)
        )

    submission = (ROOT / "docs/public-submission.md").read_text(encoding="utf-8")
    if "Version 0.3.5" not in submission:
        raise AssertionError("submission release notes must name version 0.3.5")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "dist/documentar-reuniao-0.3.5.zip" not in readme:
        raise AssertionError("README must name the current public archive")
    positive_cases = re.findall(r"^### P[1-5] ", submission, flags=re.MULTILINE)
    negative_cases = re.findall(r"^### N[1-3] ", submission, flags=re.MULTILINE)
    if len(positive_cases) != 5 or len(negative_cases) != 3:
        raise AssertionError(
            "submission material must contain five positive and three negative cases"
        )
    required_submission_content = (
        "João Eduardo Ferreira Bertacchi",
        "https://github.com/joaobertacchi/gpt-workflows/issues",
        "Version 0.3.5 delivers meeting reports",
        "Skills only",
        "No credentials or fixture data required",
        f"Short description: {expected_short_description}",
    )
    if any(phrase not in submission for phrase in required_submission_content):
        raise AssertionError("submission material is missing mandatory portal content")

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
ITEM_DATE_FORMATS = list(FIELD_SCHEMA.get("itemDateFormats", []))
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
                    assert_report_delivery(
                        turn, case.get("artifactSupported", True)
                    )
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
