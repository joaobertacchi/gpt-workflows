# Single-File Meeting Skill Design

## Goal

Make `Documentar Reunião` execute predictably in ChatGPT when the selected local plugin does not load supporting runtime files. The critical workflow contract must be available directly in `SKILL.md`.

## Evidence

ChatGPT loaded and enabled plugin versions `0.2.1` and `0.2.2`, but `@Documentar Reunião começar` produced generic meeting prompts instead of the packaged intake. The responses introduced fields outside the schema, including time, duration, decisions, deadlines, and success criteria. Reinstalling through the Plugins Directory, changing the plugin version, and adding `$relatorio-reuniao` to the skill metadata did not resolve the behavior.

Codex loaded the supporting files successfully, so the failure is specific to relying on those files on the ChatGPT acceptance surface.

## Runtime Architecture

`skills/relatorio-reuniao/SKILL.md` is the only runtime source of workflow instructions. It contains:

- activation rules;
- the literal initial intake response;
- the seven required fields, types, allowed values, and explicit-none values;
- collection, correction, conflict, validation, date-confirmation, and override rules;
- generation states and transitions;
- the complete report template;
- incomplete-draft labeling and delivery guidance;
- examples and common mistakes.

`skills/relatorio-reuniao/agents/openai.yaml` remains only because it supplies discovery metadata and the explicit `$relatorio-reuniao` starter prompt.

The runtime `assets/` and `references/` directories are removed. Root `tests/` and `scripts/` remain development-only resources.

## Conversation Contract

The first response to an empty activation or `começar`, `iniciar`, or `start` must reproduce the seven-field intake from `SKILL.md`. It must not request time, duration, decisions, success criteria, or unrelated deadlines.

The required fields remain:

1. company;
2. meeting or visit date;
3. contacts;
4. visit type: `corretiva`, `preventiva`, `desenvolvimento`, or `negociação`;
5. topics discussed;
6. next steps with an action and responsible person, or explicit absence;
7. follow-up date, or explicit absence.

Relative dates are converted to calendar dates and confirmed before complete generation. Clear corrections replace prior values. Ambiguous conflicts trigger a question about only the conflicting field. Missing-information questions contain only unresolved required fields.

A complete record generates immediately. An incomplete record generates only after affirmative use of a configured override phrase and is visibly labeled as a draft with every pending field.

## Report Contract

The complete report contains company, meeting date, contacts, visit type, follow-up date, topics, and next steps. Action-based next steps use `Ação` and `Responsável` columns. Explicit absence renders `Nenhum próximo passo definido` and `Não haverá follow up`.

`Pendências de informação` appears only after an explicit incomplete override. Complete reports contain no placeholders or pending section.

## Testing

The deterministic harness reads the single runtime contract and verifies:

- the literal intake and all seven labels;
- required-field types and values;
- invalid absolute dates;
- corrections, retractions, and conflicts;
- inferred-date confirmation;
- field-specific negative answers;
- affirmative-only overrides;
- complete and incomplete report output;
- absence of runtime `assets/` and `references/` directories;
- manifest and metadata consistency.

The package version becomes `0.3.0`. After installation through the ChatGPT Plugins Directory, acceptance starts with only `@Documentar Reunião começar`. The remaining scenarios run only after the intake matches the contract.

## Boundaries

The plugin remains skills-only. It does not add MCP, backend services, storage, external APIs, CRM integration, credentials, transcription, or persistence. Android testing remains post-publication.
