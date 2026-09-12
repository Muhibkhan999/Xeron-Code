import os, re

root = r"C:\Users\Admin\Downloads\free-xeron-code-main\free-xeron-code-main"
excluded_names = {"rebrand.py", "uv.lock"}
excluded_ext = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".bin", ".pkl", ".so", ".dylib"}

results = []
for dirpath, dirnames, filenames in os.walk(root):
    for fname in filenames:
        if fname in excluded_names:
            continue
        fpath = os.path.join(dirpath, fname)
        ext = os.path.splitext(fname)[1].lower()
        if ext in excluded_ext:
            continue
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
            try:
                content = data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(r'fcc', line, re.IGNORECASE):
                    rel = os.path.relpath(fpath, root)
                    results.append(f"{rel}:{i}: {line[:300]}")
        except Exception:
            pass

for r in results:
    print(r)
print(f"\n--- TOTAL: {len(results)} matches ---")
