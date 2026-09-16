# Public Submission Readiness Design

## Goal

Prepare version `0.3.3` of **Documentar Reunião** with only the repository materials and metadata required for an OpenAI public skills-only plugin submission.

## Scope

The package remains skills-only. It gains no MCP server, backend, authentication, storage, telemetry, website application, screenshots, or optional branding assets.

Repository work covers:

- verified publisher identity in package metadata;
- public website, support, privacy, and terms URLs;
- one production logo;
- mandatory listing copy, release notes, and reviewer test cases;
- automated checks that prevent submission with missing publication metadata; and
- patch version `0.3.3`.

Organization identity verification, the **Apps Management: Write** permission, portal form completion, review, and final publication remain manual OpenAI Platform steps.

## Publisher And Public URLs

The public developer name is `João Eduardo Ferreira Bertacchi`. This name must match the individual or business identity selected in the OpenAI Platform submission.

Use these public URLs:

- Website: `https://github.com/joaobertacchi/gpt-workflows`
- Repository: `https://github.com/joaobertacchi/gpt-workflows`
- Support: `https://github.com/joaobertacchi/gpt-workflows/issues`
- Privacy: `https://github.com/joaobertacchi/gpt-workflows/blob/main/PRIVACY.md`
- Terms: `https://github.com/joaobertacchi/gpt-workflows/blob/main/TERMS.md`

The support URL is portal submission data. The portable and compatibility manifests must include only fields supported by their schemas and OpenAI interface metadata; they must not invent a `supportURL` field.

## Manifest Changes

Both manifests move from `0.3.2` to `0.3.3` and use `João Eduardo Ferreira Bertacchi` for author and developer presentation.

The root portable manifest adds:

- `author.url` with the GitHub profile URL;
- `homepage` with the repository URL;
- `repository` with the repository URL; and
- OpenAI interface values for `websiteURL`, `privacyPolicyURL`, `termsOfServiceURL`, and `logo`.

The compatibility manifest mirrors the author and OpenAI interface values it supports. The logo path is `./assets/logo.png` from the plugin root.

## Required Public Documents

### Privacy

`PRIVACY.md` must state that the plugin package:

- is a skills-only instruction package;
- has no developer-operated server, account system, database, telemetry, or external API;
- does not independently collect, store, or transmit user content to the developer;
- processes no data outside the ChatGPT environment through plugin-owned infrastructure; and
- does not replace the privacy terms that govern the user's OpenAI service.

It must provide the GitHub Issues URL for privacy questions. It must not claim control over OpenAI's own processing.

### Terms

`TERMS.md` must state:

- the plugin's meeting-report purpose;
- that users must review names, dates, responsibilities, and content before sharing;
- that the plugin cannot send messages or write to CRM or external systems;
- that generated reports are provided without a guarantee of completeness or fitness for a particular purpose;
- that users remain responsible for lawful and appropriate use; and
- that source code distribution remains governed by the repository's MIT license.

No jurisdiction clause or optional commercial terms will be added.

## Logo

The user-generated `assets/logo.png` is the sole visual asset. It represents general workflow automation rather than only meeting documents. The file must be a valid square PNG and remain readable when reduced to a small icon.

No composer icon, screenshots, alternate logo, or additional brand system will be created.

## Submission Material

Create `docs/public-submission.md` as a copy source for mandatory portal fields. It must contain:

- plugin name, category, short description, and long description;
- developer identity and all public URLs;
- starter prompts already supported by the plugin;
- initial-submission release notes;
- exactly five positive reviewer cases; and
- exactly three negative reviewer cases.

Each reviewer case must provide a user prompt, expected workflow behavior, and expected result shape. No fixture data or credentials are required because the plugin has no MCP server or authentication.

### Positive Cases

1. `começar` returns exactly the seven required categories.
2. A complete first-turn record generates a report without a pending section.
3. A partial record asks only for unresolved required fields.
4. Relative meeting and follow-up dates are resolved and explicitly confirmed before generation.
5. Rich notes preserve all relevant facts and attribution in `Registro detalhado`, inside one report-only copy block.

### Negative Cases

1. A visit type outside the four allowed values triggers clarification instead of generation.
2. A quoted or hypothetical override phrase does not authorize an incomplete report.
3. A request to send or save the report in CRM, WhatsApp, or another external system must not claim the action occurred.

## README

Update the publication section to link the public privacy, terms, support, repository, and official submission portal. Keep local testing instructions and Android's post-publication status unchanged.

## Validation

Extend `scripts/test_flow.py` to verify:

- both manifest versions equal `0.3.3`;
- both manifests use the approved developer name;
- portable website, repository, privacy, terms, and logo metadata match the approved values;
- compatibility metadata agrees with the portable OpenAI interface;
- `PRIVACY.md`, `TERMS.md`, `docs/public-submission.md`, and `assets/logo.png` exist;
- the logo has a PNG signature and square dimensions; and
- submission material contains five positive and three negative cases.

All 30 existing conversational scenarios must remain green. JSON, YAML, frontmatter, whitespace, and installed-cache identity checks remain required.

## Acceptance

Repository readiness is complete when automated validation passes and all required public materials are committed and pushed. Portal readiness additionally requires the user to confirm:

- the publishing organization grants **Apps Management: Write**;
- `João Eduardo Ferreira Bertacchi` is a verified identity in that organization; and
- every public URL resolves from a signed-out browser session.

The submission itself remains a manual portal action at `https://platform.openai.com/plugins` using **Skills only**.
