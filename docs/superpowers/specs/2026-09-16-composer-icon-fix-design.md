# Composer Icon Fix Design

## Problem

The Skills-only package passes upload validation but fails final submission with:

```text
`interface.composerIcon` is required and must reference a square image.
```

The portable manifest declares `extensions.com.openai.interface.logo` but omits `composerIcon`. Portal normalization carries that omission into the generated Codex manifest. Final directory validation therefore rejects the release even though upload validation previously described the field as optional.

## Fix

Use the existing `assets/logo.png` for both visual fields:

```json
"composerIcon": "./assets/logo.png",
"logo": "./assets/logo.png"
```

Add `composerIcon` to:

- `plugin.json` under `extensions.com.openai.interface`; and
- `.codex-plugin/plugin.json` under `interface`.

The existing image is a valid square PNG measuring 1254 by 1254 pixels. No new visual asset is required.

Set both manifest versions to `0.3.4`. Version `0.3.3` has already been submitted as a portal draft that cannot be deleted, so the corrected package must use a new semantic version.

## Package Impact

The archive allowlist remains unchanged because `assets/logo.png` is already included. Regenerating the package creates `dist/documentar-reuniao-0.3.4.zip` with a manifest that references the included square image.

The automatic conversion notice is expected and requires no change. Root `plugin.json` remains the portable source, and the portal may add a normalized `.codex-plugin/plugin.json` to the submitted bundle.

## Validation

Extend `scripts/test_flow.py` to require:

- both manifests define `composerIcon` as `./assets/logo.png`;
- `composerIcon` and `logo` use the same path;
- both manifests use version `0.3.4`;
- the referenced file exists;
- the file has a valid PNG header; and
- its width equals its height.

Run the full harness, regenerate the ZIP, verify archive integrity, and confirm the archive still contains exactly the four approved paths.

## Acceptance

The correction is complete when all 30 conversational scenarios pass, `dist/documentar-reuniao-0.3.4.zip` passes integrity and allowlist checks, and both source manifests reference the bundled square PNG through `composerIcon`.
