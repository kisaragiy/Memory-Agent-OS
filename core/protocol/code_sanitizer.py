import ast

def remove_comments_prefix(code: str) -> str:
    if code.startswith("#"):
        return ""
    return code

def fix_flask_bugs(code: str) -> str:
    lines = code.splitlines()
    fixed_lines = []
    for line in lines:
        if "global users" not in line and "setattr(" not in line:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)

def validate_python_syntax(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def ensure_clean_imports(code: str) -> str:
    lines = code.splitlines()
    cleaned_lines = []
    for line in lines:
        if not line.startswith("import ") and not line.startswith("from "):
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def sanitize(code: str) -> str:
    code = remove_comments_prefix(code)
    code = fix_flask_bugs(code)
    if validate_python_syntax(code):
        code = ensure_clean_imports(code)
    else:
        code = "# Fallback code for safe execution"
    return code
