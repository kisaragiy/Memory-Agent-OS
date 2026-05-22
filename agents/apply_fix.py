from code_agent import generate_patch
from patcher import apply_patch

# 读取目标文件
file_path = "agents/router.py"

with open(file_path, "r") as f:
    code = f.read()

# 生成 patch
patch = generate_patch(
    file_path,
    "让路由更偏向代码任务（优先识别'写代码'）",
    code
)

print("=== PATCH ===")
print(patch)

# 应用 patch
result = apply_patch(patch)

print("\n=== RESULT ===")
print(result)
