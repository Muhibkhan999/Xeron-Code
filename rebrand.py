import os

ROOT = r"C:\Users\Admin\Downloads\free-claude-code-main\free-claude-code-main"

REPLACEMENTS = [
    ("Free Claude Code", "Free Xeron Code"),
    ("free-claude-code", "free-xeron-code"),
    ("free_claude_code", "free_xeron_code"),
    ("FccDesktopIcon", "FxcDesktopIcon"),
    ("FccModelCombobox", "FxcModelCombobox"),
    ("projectFccModels", "projectFxcModels"),
    ("fetchFccModels", "fetchFxcModels"),
    ("Fcc-Launch-Id", "Fxc-Launch-Id"),
    ("Fcc_", "Fxc_"),
    ("FCC_", "FXC_"),
    ("FCC.", "FXC."),
    (".fcc", ".fxc"),
    ("fcc-", "fxc-"),
    ("fcc_", "fxc_"),
    ('"fcc"]', '"fxc"]'),
    ('{fcc =', '{fxc ='),
    ('model_provider = "fcc"', 'model_provider = "fxc"'),
    ('model_provider="fcc"', 'model_provider="fxc"'),
    ('"fcc" not in', '"fxc" not in'),
    ('[model_providers]\nfcc =', '[model_providers]\nfxc ='),
    ('"model_provider": "fcc"', '"model_provider": "fxc"'),
    ('"modelProvider": "fcc"', '"modelProvider": "fxc"'),
    ("fcc's", "fxc's"),
    ("fcc.patch.yml", "fxc.patch.yml"),
    ("_fcc)", "_fxc)"),
    ("_fcc_", "_fxc_"),
    ("vision-fcc.png", "vision-fxc.png"),
    ("only_fcc)", "only_fxc)"),
    ("only_fcc(", "only_fxc("),
    ("stops_before_fcc", "stops_before_fxc"),
    ("identifies_fcc", "identifies_fxc"),
    ("FCC", "FXC"),
]

EXCLUDED_NAMES = {"pyproject.toml", "uv.lock"}

def should_process(filepath):
    basename = os.path.basename(filepath)
    if basename in EXCLUDED_NAMES or basename == "rebrand.py":
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return False
    rel = os.path.relpath(filepath, ROOT)
    lower = rel.lower()
    if basename == ".env.example":
        return True
    if lower.endswith(".md"):
        return True
    if lower.endswith((".yml", ".yaml")) and lower.startswith(".github/"):
        return True
    if lower.endswith((".ts", ".js", ".html", ".css")):
        if lower.startswith("src/free_claude_code/api/admin_static/") or lower.startswith("src/free_claude_code/cli/launchers/"):
            return True
    return True

def replace_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    for old, new in REPLACEMENTS:
        content = content.replace(old, new)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    for dirpath, _, filenames in os.walk(ROOT):
        for fname in filenames:
            filepath = os.path.join(dirpath, fname)
            if not should_process(filepath):
                continue
            replace_in_file(filepath)

if __name__ == "__main__":
    main()
