import os
import re

root = r"C:\Users\Admin\Downloads\free-xeron-code-main\free-xeron-code-main"
excluded_names = {"rebrand.py", "uv.lock", "_scan.py", "_replace.py"}

# Collect all files containing fcc/Fcc/FXC
files_to_process = []
for dirpath, dirnames, filenames in os.walk(root):
    for fname in filenames:
        if fname in excluded_names:
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            if re.search(r'fcc', content, re.IGNORECASE):
                files_to_process.append((fpath, content))
        except Exception:
            pass

# Step 1: Protect keep-patterns with unique placeholders
# Each entry: (regex_pattern, placeholder_string)
PROTECT_PATTERNS = [
    (re.compile(r'ffcc00', re.IGNORECASE), '<<HEX_FFXC00>>'),
    (re.compile(r'fcc\.internal', re.IGNORECASE), '<<DOMAIN_FXC_INT>>'),
    (re.compile(r'fcc\.invalid', re.IGNORECASE), '<<DOMAIN_FXC_INV>>'),
    (re.compile(r'fcc\.test', re.IGNORECASE), '<<DOMAIN_FXC_TEST>>'),
    (re.compile(r'fcc:anthropic-reasoning', re.IGNORECASE), '<<PROTO_FXC_AM>>'),
    (re.compile(r'fcc:history', re.IGNORECASE), '<<PROTO_FXC_HIST>>'),
    (re.compile(r'"q":"fcc"', re.IGNORECASE), '<<TEST_Q_FXC>>'),
]

# Restoration map: placeholder -> original text
RESTORE_MAP = {
    '<<HEX_FFXC00>>': 'ffcc00',
    '<<DOMAIN_FXC_INT>>': 'fcc.internal',
    '<<DOMAIN_FXC_INV>>': 'fcc.invalid',
    '<<DOMAIN_FXC_TEST>>': 'fcc.test',
    '<<PROTO_FXC_AM>>': 'fcc:anthropic-reasoning',
    '<<PROTO_FXC_HIST>>': 'fcc:history',
    '<<TEST_Q_FXC>>': '"q":"fcc"',
}

# Specific replacements (applied before generic catch-all)
SPECIFIC_REPLACEMENTS = [
    ("fcc provider", "fxc provider"),
    ("fcc smoke", "fxc smoke"),
    ("fcc server", "fxc server"),
    ("Fcc", "Fxc"),
    ("fcc.chat.draftWithoutDot", "fxc.chat.draftWithoutDot"),
    ("fcc.chat.draft", "fxc.chat.draft"),
    ("fcc.code.", "fxc.code."),
    ('"modelProvider": "fxc"', '"modelProvider": "fxc"'),
    ('modelProvider": "fcc"', 'modelProvider": "fxc"'),
    ('model_provider = "fxc"', 'model_provider = "fxc"'),
    ('model_provider="fxc"', 'model_provider="fxc"'),
    ('"model_providers"]["fcc"', '"model_providers"]["fxc"'),
    ("test_uninstall_sh_removes_and_verifies_only_fcc", "test_uninstall_sh_removes_and_verifies_only_fxc"),
    ("test_uninstall_ps1_removes_and_verifies_only_fcc", "test_uninstall_ps1_removes_and_verifies_only_fxc"),
    ("test_native_probe_failure_stops_before_fxc", "test_native_probe_failure_stops_before_fxc"),
    ("identifies_fxc", "identifies_fxc"),
    ("fcc provider env", "fxc provider env"),
    ("fcc internal", "fxc internal"),
    ("vision-fxc.png", "vision-fxc.png"),
    ("fxc's", "fxc's"),
    ("fxc.patch.yml", "fxc.patch.yml"),
    # Generic catch-all for remaining standalone fcc
    ("fcc", "fxc"),
    ("FXC", "FXC"),
]

total_changes = 0

for fpath, content in files_to_process:
    original = content
    
    # Step 1: Protect keep-patterns with placeholders
    for pattern, placeholder in PROTECT_PATTERNS:
        content = pattern.sub(placeholder, content)
    
    # Step 2: Apply specific replacements
    for old, new in SPECIFIC_REPLACEMENTS:
        if old in content:
            count = content.count(old)
            content = content.replace(old, new)
            total_changes += count
    
    # Step 3: Restore keep-patterns from placeholders
    for placeholder, original_text in RESTORE_MAP.items():
        content = content.replace(placeholder, original_text)
    
    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        rel = os.path.relpath(fpath, root)
        print(f"Modified: {rel}")

print(f"\nTotal individual replacements: {total_changes}")
