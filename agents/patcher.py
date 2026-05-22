# agents/patcher.py

import subprocess
import tempfile


def apply_patch(patch_text: str):
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as f:
        f.write(patch_text)
        patch_file = f.name

    try:
        subprocess.run(
            ["patch", "-p1", "-i", patch_file],
            check=True
        )
        return "✅ Patch applied"
    except subprocess.CalledProcessError as e:
        return f"❌ Patch failed: {e}"
