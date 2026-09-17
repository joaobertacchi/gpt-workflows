# Report-Only Message Design

## Goal

Deliver every generated meeting report as the entire chat message, rendered inline by ChatGPT, so the conversation copy button copies exactly the report and nothing else.

## Current Behavior

Version `0.3.6` delivers the report as a native Markdown file artifact (`relatorio-reuniao.md`) with a fenced Markdown fallback for unsupported surfaces. In ChatGPT Work this renders correctly only after the user opens the generated file. Status and operational guidance always precede the report. The user found the open-file step unexpected friction and chose inline rendering as the primary consumption model (read and share rendered content).

## New Delivery Contract

For every complete, overridden, or regenerated report:

1. The entire message is exactly the report, beginning with `# Relatório de reunião/visita`.
2. The report renders as Markdown: headings, bold labels, bullet lists, and the three-column next-steps table (`Ação`, `Responsável`, `Prazo`).
3. No status, no operational guidance, no code fences, and no text before or after the report. The message copy button copies only the report.
4. Overridden or regenerated drafts carry `## Pendências de informação` and `Não informado` placeholders inside the report; the pending section itself signals incompleteness, so no separate warning exists.
5. A complete report contains no `Pendências de informação` section and no missing placeholder.
6. A correction reopens validation and the next message is again exactly the new report.

## Removals

- The `relatorio-reuniao.md` file artifact and the fenced Markdown fallback disappear.
- The `COMPLETE_GUIDANCE` and `INCOMPLETE_GUIDANCE` sections and their marked blocks are removed from `SKILL.md`; no guidance text is emitted with any report.
- The send/save refusal rule remains a conversational behavior in Common Mistakes and the disclosure remains in `TERMS.md`; nothing user-facing is lost because no guidance message exists anymore.
- The harness loses artifact machinery: `artifactName`, `artifactContent`, the `artifactSupported` case flag, guidance rendering, and the artifact/fallback assertions.

## Rendering Rationale

ChatGPT renders Markdown in regular conversation output: headings, bold labels, lists, and tables display formatted without any file or fence. OpenAI's migration guidance for imported skills states: "Return the underlying content as regular conversation output instead; for example, render artifact tables as standard tables. Artifact-specific HTML, persistence, refresh behavior, and interactions aren't preserved." This is the documented, supported path and removes all artifact-surface dependency.

## Runtime Scope

The change remains instruction-only and skills-only:

- `skills/relatorio-reuniao/SKILL.md` defines the report-only message contract and keeps the single report template;
- `scripts/test_flow.py` models and validates the inline contract offline;
- no new package member is required; and
- the public ZIP allowlist remains unchanged.

## Validation

The offline harness must validate:

- every `generate` message starts with `# Relatório de reunião/visita` and contains no code fences;
- the report is the whole message: no operational phrases, no guidance sections anywhere in the output;
- complete reports omit the pending section; overridden reports include it inside the report;
- the next-steps table renders the `Ação`, `Responsável` and `Prazo` columns;
- relative dates and the explicit override keep their existing scenarios; and
- both manifests, README, and submission notes reference version `0.3.7`.

The harness cannot prove live chat rendering. Final acceptance also requires a ChatGPT Work conversation confirming the message displays the rendered report alone and that the message copy button copies only the report.

## Versioning

Release as version `0.3.7` in both manifests. Version `0.3.6` is already submitted to the portal and must remain unchanged. Update release notes, README references, and the acceptance baseline. The packaging script derives the filename from root `plugin.json`, producing `dist/documentar-reuniao-0.3.7.zip`.

## Acceptance

The improvement is ready when:

- all conversational scenarios pass with the inline contract;
- the harness's report-only assertion passes for every generated message;
- ChatGPT Work renders the report as the entire message with no extra text;
- the message copy button copies only the report;
- a draft report shows `Pendências de informação` inside the report; and
- `dist/documentar-reuniao-0.3.7.zip` passes the existing integrity and allowlist checks.
