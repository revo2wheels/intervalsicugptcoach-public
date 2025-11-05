import json, base64

# Load local GitHub schema definition
with open("githubschema.json", "r", encoding="utf-8") as f:
    GITHUB_SCHEMA = json.load(f)

def loadAllRules():
    """
    Local replacement for the GitHub API /repos/.../contents/all-modules.md
    Uses githubschema.json to stay compliant with expected structure.
    """
    with open("all-modules.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Encode per GitHub REST schema spec
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    return {
        "name": "all-modules.md",
        "path": "all-modules.md",
        "sha": "localdev000",
        "content": encoded,
        "encoding": "base64",
    }
