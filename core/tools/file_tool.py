class FileTool:

    def read_file(self, path):
        try:
            with open(path, 'r') as f:
                return {'success': True, 'result': f.read()}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def write_file(self, path, content):
        try:
            with open(path, 'w') as f:
                f.write(content)
            return {'success': True, 'result': 'written'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def patch_file(self, path, diff):
        try:
            with open(path, 'r+') as f:
                original_content = f.read()
                new_content = self._apply_diff(original_content, diff)
                f.seek(0)
                f.write(new_content)
                f.truncate()
            return {'success': True, 'result': 'patched'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _apply_diff(self, original, diff):
        # Simple line-based patching for demonstration
        original_lines = original.splitlines()
        diff_lines = diff.splitlines()

        patched_lines = []
        i, j = 0, 0

        while i < len(original_lines) and j < len(diff_lines):
            if original_lines[i] == diff_lines[j]:
                patched_lines.append(original_lines[i])
                i += 1
                j += 1
            else:
                patched_lines.append(diff_lines[j])
                j += 1

        # Append remaining lines from either original or diff
        patched_lines.extend(original_lines[i:])
        patched_lines.extend(diff_lines[j:])

        return '\n'.join(patched_lines)
