from agents.tools.registry import register_tool


def save_file(text: str, filename="output.txt"):
    with open(filename, "w") as f:
        f.write(text)
    return f"saved to {filename}"


register_tool(
    "save_file",
    save_file,
    "保存文本到文件"
)
