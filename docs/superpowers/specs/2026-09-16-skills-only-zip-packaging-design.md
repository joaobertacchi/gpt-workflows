# Skills-Only ZIP Packaging Design

## Goal

Produce a deterministic, minimal ZIP accepted by the current OpenAI **Skills only** upload flow and correct the final-submission short-description limit.

## Updated Requirements

The submission portal requires a valid ZIP upload. Current submission validation requires:

- one unambiguous plugin root;
- a supported manifest at that root;
- at least one valid skill;
- no MCP or app configuration for Skills-only uploads;
- a compressed size no greater than 100 MB;
- regular, readable, unencrypted archive members with relative `/`-separated paths; and
- final listing fields within their stricter character limits.

The current `shortDescription` exceeds the final limit of 30 characters. Replace it in both manifests and the portal copy with `Documente reuniões comerciais`, which is 29 Unicode characters.

Version `0.3.3` remains unchanged because no package has been uploaded to the portal yet.

## Packaging Script

Create executable `scripts/build_public_zip.sh` using Bash with `set -euo pipefail`.

The script must:

1. resolve the repository root from its own location;
2. require `python3`, `zip`, and `unzip` on `PATH`;
3. run `python3 scripts/test_flow.py` before packaging;
4. read the version from root `plugin.json`;
5. create `dist/` and replace only the same-version output archive;
6. call `zip` with an explicit file list from the repository root;
7. run `unzip -tq` to verify archive integrity;
8. compare `unzip -Z1` output against the exact expected file list; and
9. print the absolute archive path when successful.

The output path is `dist/documentar-reuniao-<version>.zip`.

## Archive Contents

The ZIP contains exactly these regular files at these paths:

```text
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

The portable `plugin.json` is at the archive root. Its `extensions.com.openai` object contains the public listing metadata, so `.codex-plugin/plugin.json` is not required in the upload. Privacy and terms are public URLs and do not need duplicate Markdown files in the archive.

The script must not archive `.git`, `.codex-plugin`, `docs`, `tests`, `scripts`, `README.md`, `PRIVACY.md`, `TERMS.md`, `.DS_Store`, or any other development file.

## Generated Output

Add `/dist/` to `.gitignore`. The ZIP is generated locally and is not committed. Source manifests, the packaging script, documentation, and tests remain versioned.

## Validation

Extend the deterministic harness to require:

- `shortDescription` is exactly `Documente reuniões comerciais` in both manifests;
- display name is at most 30 characters;
- short description is at most 30 characters;
- developer name is at most 80 characters;
- no more than three starter prompts;
- each starter prompt is at most 128 characters;
- `scripts/build_public_zip.sh` and `.gitignore` exist;
- the script names all four allowed archive members; and
- `.gitignore` contains `/dist/`.

Run the script as integration verification. Inspect the resulting ZIP for integrity, exact paths, root manifest placement, absence of excluded files, and size below 100 MB.

All 30 conversational scenarios, manifest parsing, YAML/frontmatter validation, whitespace checks, local cache identity, and clean Git status remain required.

## Documentation

Update `README.md` with one command:

```bash
./scripts/build_public_zip.sh
```

Document the output path and state that the generated archive is the file uploaded in **Create plugin → Skills only**.

Update `docs/public-submission.md` so its short description exactly matches the manifests.

## Acceptance

Packaging is complete when:

- the script exits successfully;
- `dist/documentar-reuniao-0.3.3.zip` exists;
- archive validation reports no error;
- the archive contains exactly the four approved files;
- the compressed archive is below 100 MB;
- all automated checks pass; and
- source changes are committed and pushed while `dist/` remains ignored.
