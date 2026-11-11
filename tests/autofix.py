import json, re, subprocess, sys
from pathlib import Path
KNOWLEDGE = Path(__file__).parent / "knowledge.json"

def attempt_autofix(error_text):
    kb = json.loads(KNOWLEDGE.read_text(encoding="utf-8"))
    for pat in kb.get("patterns", []):
        m = re.search(pat["regex"], error_text)
        if m:
            print(f"  🔍 نمط: {pat['description']}")
            if pat["fix_type"] == "pip_install":
                mod = pat["fix_arg"].format(*m.groups())
                print(f"  🔧 pip install {mod}")
                r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", mod], capture_output=True, text=True, timeout=120)
                return r.returncode == 0, ("ثبت " + mod if r.returncode == 0 else r.stderr[:100])
    return False, "نمط غير معروف"

if __name__ == "__main__":
    ok, msg = attempt_autofix(" ".join(sys.argv[1:]))
    print(f"{'✅' if ok else '❌'} {msg}")
    sys.exit(0 if ok else 1)
