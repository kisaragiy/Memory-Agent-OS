from agents.code_agent import generate_patch
from agents.patcher import apply_patch
import subprocess


def run_tests():
    result = subprocess.run(["pytest", "-q"], capture_output=True)
    return result.returncode == 0


def auto_fix(file_path, instruction):
    with open(file_path, "r") as f:
        code = f.read()

    patch = generate_patch(file_path, instruction, code)

    print("=== PATCH ===")
    print(patch)

    # 先测试当前系统
    if not run_tests():
        print("❌ baseline tests failed, abort")
        return

    # 应用 patch
    result = apply_patch(patch)
    print(result)

    # 再测试
    if run_tests():
        print("✅ patch accepted")
    else:
        print("❌ patch broke system, should rollback")
