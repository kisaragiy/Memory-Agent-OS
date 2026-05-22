TOOLS = {}


def register_tool(name, func, description):
    TOOLS[name] = {
        "func": func,
        "desc": description
    }


def get_tool(name):
    return TOOLS.get(name)


def list_tools():
    return {k: v["desc"] for k, v in TOOLS.items()}
