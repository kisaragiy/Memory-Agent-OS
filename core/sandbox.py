import subprocess
import tempfile
import os

class Sandbox:
    def run(self, code):

        with tempfile.TemporaryDirectory() as tmpdir:

            file_path = os.path.join(tmpdir, "task.py")

            with open(file_path, "w") as f:
                f.write(code)

            try:
                result = subprocess.run(
                    ["python", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

            except Exception as e:
                return {"error": str(e)}
