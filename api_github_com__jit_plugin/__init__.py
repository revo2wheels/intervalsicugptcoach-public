import json, base64, os

# Optional: Load GitHub schema definition for local validation
GITHUB_SCHEMA = {}
if os.path.exists("githubschema.json"):
    with open("githubschema.json", "r", encoding="utf-8") as f:
        GITHUB_SCHEMA = json.load(f)

def loadAllRules():
    """
    Local replacement for the GitHub API call:
      GET /repos/{owner}/{repo}/contents/all-modules.md

    Returns the same payload shape expected by run_report() and audit controllers.
    This ensures parity between offline/local and live ChatGPT governance behavior.
    """
    with open("all-modules.md", "r", encoding="utf-8") as f:
        content = f.read()

    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    return {
        "name": "all-modules.md",
        "path": "all-modules.md",
        "sha": "localdev000",
        "content": encoded,
        "encoding": "base64",
        # ↓ Added for audit controller compliance ↓
        "manifest_origin": "local",
        "manifest_source": "live",
        "framework_version": "Unified Reporting Framework v5.1",
        "ruleset_version": "v16.16G"
    }
