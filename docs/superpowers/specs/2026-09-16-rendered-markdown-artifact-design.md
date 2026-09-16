# Rendered Markdown Artifact Design

## Goal

Deliver each meeting report as a native Markdown file artifact that ChatGPT can render for review while preserving the `.md` source for copying or download.

## Current Behavior

The skill currently requires exactly one fenced `markdown` block. ChatGPT therefore shows a code-style panel with literal `#`, `**`, table, and list syntax. This makes the source easy to copy but prevents the report from being displayed as a formatted document.

The deterministic harness enforces the same behavior by requiring one Markdown fence around every report.

## Supported Platform Behavior

OpenAI's **Work with files** documentation describes generated-file previews and explicitly includes Markdown files in the supported annotation workflow. This existing artifact surface is the intended delivery mechanism. The plugin will not add custom UI, HTML, an MCP server, an app, or another integration.

Artifact availability varies by ChatGPT surface, plan, and workspace configuration. The skill can instruct ChatGPT to create the artifact, but cannot force a host that does not expose file artifacts to do so. A deterministic fallback is therefore required.

## Delivery Contract

For every complete, overridden, or regenerated report:

1. Generate the report from the existing Markdown template.
2. Keep completion or incomplete-draft guidance in the chat response, outside the report.
3. Create or update a native Markdown file artifact named `relatorio-reuniao.md`.
4. Put only the report in the artifact, beginning with `# Relatório de reunião/visita`.
5. Do not also repeat the complete report inline when artifact creation succeeds.
6. Leave no conversational guidance inside the artifact.

The artifact source preserves headings, bold labels, bullet lists, tables, and the optional pending-information section. ChatGPT controls the artifact preview, source-copy, and download interactions.

Regeneration uses the same filename and replaces or updates the report artifact rather than intentionally presenting duplicate report files.

## Fallback

If the active ChatGPT surface cannot create or expose a Markdown artifact, retain the existing fallback:

- output completion or draft guidance first;
- place only the report inside exactly one fenced `markdown` block; and
- emit nothing after the closing fence.

The fallback prioritizes reliable access to copyable Markdown source over formatted rendering.

## Versioning

Release the behavior as version `0.3.5` in both manifests. Version `0.3.4` has already been submitted to the portal and must remain unchanged.

Update release notes and README references to `0.3.5`. The packaging script continues to derive the filename from root `plugin.json`, producing `dist/documentar-reuniao-0.3.5.zip`.

## Runtime Scope

The change remains instruction-only and skills-only:

- `skills/relatorio-reuniao/SKILL.md` defines artifact-first delivery and fallback behavior;
- `scripts/test_flow.py` models and validates the delivery contract offline;
- no generated report is stored by the plugin itself;
- no new package member is required; and
- the public ZIP allowlist remains unchanged.

## Validation

The offline harness must validate:

- artifact delivery is preferred when artifact support is available;
- the artifact filename is exactly `relatorio-reuniao.md`;
- artifact content starts with the report heading and contains no guidance;
- successful artifact delivery does not duplicate the report inline;
- unsupported artifact delivery produces the existing single fenced-block fallback;
- complete reports omit pending-information content;
- overridden reports retain pending placeholders and the pending-information section;
- regenerated reports follow the same artifact-first contract;
- both manifests use version `0.3.5`; and
- README and public submission notes reference version `0.3.5`.

The harness cannot prove how a particular ChatGPT client renders its native artifact viewer. Final acceptance therefore also requires a new ChatGPT Work conversation that verifies the `.md` artifact opens as a formatted report and that copying or downloading it preserves Markdown source.

## Acceptance

The improvement is ready when:

- all existing conversational scenarios and the new delivery checks pass;
- ChatGPT Work creates `relatorio-reuniao.md` for a complete report;
- the artifact preview renders headings, labels, lists, and tables as formatted content;
- copied or downloaded artifact content remains valid Markdown;
- a tested no-artifact path returns the fenced Markdown fallback; and
- `dist/documentar-reuniao-0.3.5.zip` passes the existing integrity and allowlist checks.
