# Detailed Report Fidelity Design

## Problem

Version `0.3.1` reliably collects the seven required fields, but its output contract does not require preservation of spontaneously supplied detail. The template reduces discussion to topic bullets and has no destination for meeting context, chronology, evidence, rationale, optional metadata, or other relevant facts.

In the observed Work conversation, the user supplied a detailed account containing the meeting time and duration, Luciano's report about low CRM adoption, the current registration problem, an evaluated WhatsApp approach, a request for alternatives, the proposed ChatGPT plugin, the requirements handoff, the proof-of-concept deadline, and the intended test flow. The generated report retained a useful summary but compressed or omitted part of that information.

The generated response also placed operational guidance next to the report without a strict copy boundary. A user copying the report can therefore copy instructions that are not part of the meeting record.

## Goals

- Preserve every relevant fact the user supplies while improving organization and wording.
- Keep the existing seven fields as the only required inputs.
- Never ask for optional details solely because the report can preserve them.
- Retain an executive topic summary and add a complete detailed record.
- Provide one unambiguous copyable Markdown block containing only the report.

## Non-Goals

- Producing a verbatim transcript.
- Requiring time, duration, decisions, objectives, or other optional details.
- Inventing facts, implications, motivations, causal links, or chronology.
- Adding tools, persistence, transcription, APIs, or external integrations.
- Changing the existing missing-field, date-confirmation, override, or correction rules except where corrections affect preserved details.

## Data Model

The seven existing fields remain the complete required schema:

- company;
- meeting date;
- contacts;
- visit type;
- topics discussed;
- next steps with a responsible person for each action; and
- follow-up date.

The active record gains one optional `provided_details` collection. It contains the context and specificity behind required-field values plus relevant user-provided facts that do not fit those fields. A topic label in `topics_discussed` does not replace its supporting details. The collection must not participate in missing-field validation.

A fact is relevant when it describes meeting context, chronology, a problem, evidence, the current process, an evaluated alternative, a decision, a restriction, a channel, a deadline, a time, a duration, an expectation, or another substantive part of the discussion. Greetings, filler, speech disfluencies, repeated statements, and instructions about operating the report itself are not meeting facts.

Extraction must preserve names, attribution, dates, times, durations, channels, quantities, relationships between facts, and temporal order when supplied. Distinct facts must not be merged into a generalization that loses information. The system may remove repetition and improve grammar but must not add interpretations.

Later corrections replace affected required values and affected detail facts. Unrelated facts remain present.

## Report Format

The report keeps the current header and required values, followed by these sections in order:

1. `Assuntos discutidos`: concise executive bullets identifying the main themes.
2. `Registro detalhado`: complete, organized facts supplied by the user.
3. `Próximos passos`: the existing action and responsible-person table or explicit no-action value.
4. `Pendências de informação`: included only for an overridden incomplete report, as today.

`Registro detalhado` uses complete sentences grouped into short bullets or paragraphs. It may restate a topic from the executive summary when necessary to preserve its context. It is omitted when the user supplied only the minimum structured values and there are no additional relevant facts. It remains present in an overridden report when details were supplied.

For the observed case, the detailed record must retain at least:

- that the meeting occurred at approximately 13:00 and lasted approximately one hour;
- Luciano's account that his sales team should register client meetings but has not been doing so consistently;
- the expectation that those records should already be entering the CRM;
- that Luciano evaluated WhatsApp during the conversation and asked for better alternatives;
- the proposed publicly installable ChatGPT plugin and its intended use by Luciano and his team;
- the sequence from receiving required-field information through preparing and sending a proof of concept; and
- each stated next step, owner, and deadline.

## Copy Boundary

Every generated report response contains exactly one fenced Markdown code block containing only the report. Complete/incomplete status and operational guidance appear before that block. No text, instruction, status, or punctuation appears after the closing fence.

The report block includes `Pendências de informação` when applicable because that section belongs to the document. Guidance about reviewing, sharing, copying, sending, or external systems remains outside the block.

This boundary applies to complete reports, overridden incomplete reports, and regenerated reports after a correction.

## Behavioral Flow

1. Extract required values and all relevant supplied facts from every user turn.
2. Merge later answers, preserving unrelated facts and applying explicit corrections.
3. Validate only the seven required fields.
4. Ask only for unresolved required fields, following the existing partial-collection contract.
5. Generate immediately when complete, or after a valid override when incomplete.
6. Build an executive topic summary without treating it as a replacement for the detailed facts.
7. Render all preserved details in `Registro detalhado` when that collection is non-empty.
8. Place status and guidance before one copyable Markdown report block and emit nothing after it.

## Test Strategy

### Deterministic Harness

Add a rich-note scenario modeled on the observed conversation. It must verify that the rendered report contains the supplied time, duration, attribution to Luciano, CRM adoption problem, WhatsApp evaluation, request for alternatives, plugin proposal, requirements handoff, proof-of-concept sequence, actions, owners, and deadlines.

Add a minimal complete scenario proving that `Registro detalhado` is absent when no additional facts exist.

Add an overridden incomplete scenario proving that supplied details remain in the report while unresolved required fields appear under `Pendências de informação`.

For every generated-report scenario, verify:

- exactly one `markdown` fence pair exists;
- only report content appears inside the fences;
- status and operational guidance appear before the opening fence; and
- the closing fence is the final response content.

Existing scenarios must continue to verify the seven-field intake, missing-only prompts, relative-date confirmation, negative answers, overrides, conflicts, corrections, and report generation.

### ChatGPT Work Acceptance

Install the new package version and start an isolated Work conversation with **Documentar Reunião**. Provide a detailed narrative containing required values plus optional context comparable to the observed case.

Acceptance requires:

- all supplied relevant facts appear in the report;
- no unsupported fact appears;
- the executive summary remains readable;
- the detailed section preserves attribution and chronology;
- no optional field is requested when absent; and
- the report can be copied from one Markdown block without operational guidance.

## Release Scope

This is an instruction and deterministic-harness change to the existing single-file skill architecture. The implementation updates `SKILL.md`, the harness and fixtures, acceptance documentation, and both manifests for the next patch release. It does not add runtime files, tools, or integrations.
