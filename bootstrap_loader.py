# bootstrap_loader.py

from core.tools.tool_registry import tool_registry, load_tools_from_directory

def bootstrap_loader():
    directories = [
        "core/tools",
        "agents/tools",
        "tools"
    ]

    for directory in directories:
        load_tools_from_directory(directory, tool_registry)

    # Print the final registration list for debugging
    print("Bootstrap Registry Summary:")
    for name, tool in tool_registry.list_tools().items():
        print(f"Tool: {name}, Permissions: {tool['permissions']}")

# Automatically run bootstrap loader on startup
bootstrap_loader()
