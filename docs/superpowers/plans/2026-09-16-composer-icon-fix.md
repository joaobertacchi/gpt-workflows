# Composer Icon Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a version `0.3.4` Skills-only ZIP whose OpenAI interface references the bundled square PNG through required `composerIcon` metadata.

**Architecture:** Keep root `plugin.json` as the portable source and mirror release metadata in the compatibility manifest. Reuse `assets/logo.png` for both `logo` and `composerIcon`; the existing allowlisted archive member means packaging structure does not change.

**Tech Stack:** JSON manifests, Python 3 dependency-free harness, Bash, Info-ZIP `zip` and `unzip`.

---

### Task 1: Reserve Release Version 0.3.4

**Files:**
- Modify: `scripts/test_flow.py:518-534`
- Modify: `plugin.json:4`
- Modify: `.codex-plugin/plugin.json:3`
- Modify: `docs/public-submission.md:22-24`
- Modify: `README.md:96-100`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Write the failing version and documentation checks**

Change the expected release version and add documentation checks in `check_packaging()`:

```python
expected_version = "0.3.4"
```

After loading `submission`, add:

```python
if "Version 0.3.4" not in submission:
    raise AssertionError("submission release notes must name version 0.3.4")

readme = (ROOT / "README.md").read_text(encoding="utf-8")
if "dist/documentar-reuniao-0.3.4.zip" not in readme:
    raise AssertionError("README must name the current public archive")
```

Update the existing version failure text to avoid a stale literal:

```python
if portable_manifest["version"] != expected_version:
    raise AssertionError(f"public submission package must ship as version {expected_version}")
```

- [ ] **Step 2: Run the harness to verify RED**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL with `public submission package must ship as version 0.3.4`.

- [ ] **Step 3: Apply the minimal version bump**

Set `version` to `0.3.4` in both manifests.

Change the release-notes sentence in `docs/public-submission.md` to:

```markdown
Initial public submission of Documentar Reunião, a skills-only plugin with no MCP server, authentication, external API, or developer-operated data collection. Version 0.3.4 adds the required square composer icon while preserving detailed notes and attribution, confirming inferred dates, collecting only unresolved required fields, and producing a report-only copy block.
```

Change the README package path to:

```markdown
`dist/documentar-reuniao-0.3.4.zip`
```

- [ ] **Step 4: Run the harness to verify GREEN**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: all 30 conversational flow scenarios pass.

- [ ] **Step 5: Commit the version bump**

```bash
git add plugin.json .codex-plugin/plugin.json docs/public-submission.md README.md scripts/test_flow.py
git commit -m "chore: bump plugin version to 0.3.4"
```

### Task 2: Add the Required Composer Icon

**Files:**
- Modify: `scripts/test_flow.py:522-578`
- Modify: `plugin.json:31-36`
- Modify: `.codex-plugin/plugin.json:17-22`
- Test: `scripts/test_flow.py`

- [ ] **Step 1: Write the failing composer-icon check**

Add `composerIcon` to `expected_interface`:

```python
expected_interface = {
    "websiteURL": expected_repository,
    "privacyPolicyURL": f"{expected_repository}/blob/main/PRIVACY.md",
    "termsOfServiceURL": f"{expected_repository}/blob/main/TERMS.md",
    "composerIcon": "./assets/logo.png",
    "logo": "./assets/logo.png",
}
```

After validating `expected_interface`, require both visual fields to reference the same image:

```python
if portable_interface["composerIcon"] != portable_interface["logo"]:
    raise AssertionError("composer icon and logo must reference the same square image")
```

The existing package checks already require `assets/logo.png`, validate its PNG header, and assert equal width and height.

- [ ] **Step 2: Run the harness to verify RED**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: FAIL with `portable interface has invalid composerIcon`.

- [ ] **Step 3: Add composerIcon to both manifests**

In root `plugin.json`, add beside `logo`:

```json
"composerIcon": "./assets/logo.png",
"logo": "./assets/logo.png",
```

In `.codex-plugin/plugin.json`, add the same two fields under `interface`, preserving escaped Unicode elsewhere:

```json
"composerIcon": "./assets/logo.png",
"logo": "./assets/logo.png",
```

- [ ] **Step 4: Run the harness to verify GREEN**

Run:

```bash
python3 scripts/test_flow.py
```

Expected: all 30 conversational flow scenarios pass.

- [ ] **Step 5: Commit the manifest fix**

```bash
git add plugin.json .codex-plugin/plugin.json scripts/test_flow.py
git commit -m "fix: add required composer icon"
```

### Task 3: Build and Verify the Corrected ZIP

**Files:**
- Generate, ignored: `dist/documentar-reuniao-0.3.4.zip`

- [ ] **Step 1: Run the public packaging workflow**

```bash
./scripts/build_public_zip.sh
```

Expected: all 30 scenarios pass, `unzip` reports no compressed-data errors, and the final line is the absolute path ending in `dist/documentar-reuniao-0.3.4.zip`.

- [ ] **Step 2: Verify the exact archive listing**

```bash
unzip -Z1 dist/documentar-reuniao-0.3.4.zip
```

Expected exactly:

```text
plugin.json
assets/logo.png
skills/relatorio-reuniao/SKILL.md
skills/relatorio-reuniao/agents/openai.yaml
```

- [ ] **Step 3: Verify integrity, manifest metadata, and size**

```bash
unzip -tq dist/documentar-reuniao-0.3.4.zip
unzip -p dist/documentar-reuniao-0.3.4.zip plugin.json | python3 -c 'import json, sys; manifest = json.load(sys.stdin); interface = manifest["extensions"]["com.openai"]["interface"]; assert manifest["version"] == "0.3.4"; assert interface["composerIcon"] == "./assets/logo.png"'
test "$(wc -c < dist/documentar-reuniao-0.3.4.zip | tr -d ' ')" -lt 104857600
```

Expected: `unzip` reports no errors and both assertions exit successfully.

- [ ] **Step 4: Perform the final repository check**

```bash
git diff --check
git status --short --branch
```

Expected: no whitespace errors, no tracked changes, and `dist/` absent from normal status because it is ignored.
