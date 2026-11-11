import sys, subprocess
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from tests.autofix import attempt_autofix

def run_test(step):
    f = Path(__file__).parent / "steps" / f"test_{step}.py"
    if not f.exists():
        print(f"❌ الملف مش موجود: {f}"); sys.exit(1)
    r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True, timeout=180)
    print(r.stdout)
    return r.returncode == 0, r.stderr

if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "step1"
    print("=" * 55)
    print(f"🧪 اختبار: {step}")
    print("=" * 55)
    success, stderr = run_test(step)
    if success:
        print(f"\n🎉 {step} مقفولة 100%")
        sys.exit(0)
    print("\n🔧 محاولة إصلاح...")
    fixed, msg = attempt_autofix(stderr)
    print(f"  {'✅' if fixed else '❌'} {msg}")
    if fixed:
        success, _ = run_test(step)
        if success:
            print(f"\n🎉 {step} اتصلحت تلقائياً!")
            sys.exit(0)
    sys.exit(1)
