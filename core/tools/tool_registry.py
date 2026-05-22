# core/tools/tool_registry.py

import os
import importlib.util
import fnmatch  # Import fnmatch here
from typing import Dict, Callable, Type, List  # Import List here
import inspect  # Import inspect for constructor inspection

class ToolRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance

    def register(self, name: str, tool_instance: Callable, description: str = "", permissions: Dict[str, bool] = {"execute": True}):
        if not isinstance(permissions, dict):
            raise ValueError("Permissions must be a dictionary")
        if name in self.tools:
            print(f"Tool {name} already registered. Skipping duplicate registration.")
            return
        self.tools[name] = {
            "instance": tool_instance,
            "description": description,
            "permissions": permissions,
            "success": 0,
            "fail": 0
        }

    def list(self) -> List[str]:
        return list(self.tools.keys())

    def get_tool(self, name: str) -> Callable:
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool["instance"]

    def record(self, name: str, success: bool):
        if name in self.tools:
            if success:
                self.tools[name]["success"] += 1
            else:
                self.tools[name]["fail"] += 1

    def get(self, name: str) -> dict:
        return self.tools.get(name)

    def get_instance(self, name: str):
        tool = self.tools.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool["instance"]

EXCLUDED_NAMES = {
    "Dict",
    "Callable",
    "Type",
    "ToolRegistry",
    "ToolRouter",
    "bootstrap",
    "is_valid_tool"
}

def is_valid_tool(obj):
    if isinstance(obj, type) and hasattr(obj, 'execute') and callable(getattr(obj, 'execute')):
        return True
    if hasattr(obj, '__tool__') and obj.__tool__:
        return True
    return False

def load_tools_from_directory(directory: str, tool_registry: ToolRegistry, quiet=False):
    SKIP_FILES = {
        '*.disabled.py',
        '*disabled.py',
        '__init__.py',
        'tool_registry.py',
        'tool_router.py',
        'router*.py',  # Skip any router module
        'planner*.py',  # Skip any planner module
        'infrastructure*.py'  # Skip any infrastructure-only module
    }

    for filename in os.listdir(directory):
        if filename.endswith(".py"):
            skip = False
            for pattern in SKIP_FILES:
                if fnmatch.fnmatch(filename, pattern):
                    skip = True
                    break
            if skip:
                continue

            module_name = filename[:-3]
            file_path = os.path.join(directory, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in module.__dict__.items():
                if is_valid_tool(obj):
                    full_name = f"{module_name}.{name}"
                    if full_name not in tool_registry.tools:
                        if isinstance(obj, type) and hasattr(obj, 'execute'):
                            # Check constructor signature
                            sig = inspect.signature(obj.__init__)
                            required_params = [param for param in sig.parameters.values() if param.default is param.empty]
                            if len(required_params) > 1:  # Only self parameter should be allowed
                                if not quiet:
                                    print(
                                        f"[TOOL REGISTRY] SKIPPED {full_name} "
                                        "(dependency injection required)"
                                    )
                            else:
                                tool_instance = obj()
                                tool_registry.register(full_name, tool_instance)
                                if not quiet:
                                    print(f"AUTO REGISTERED: {full_name}")
                        else:
                            tool_registry.register(full_name, obj)

def register_tool(name: str, tool_instance: Callable):
    get_global_registry().register(name, tool_instance)

# Ensure ToolRegistry is a singleton
tool_registry = ToolRegistry()

def bootstrap(quiet=False):
    load_tools_from_directory(
        os.path.dirname(__file__), get_global_registry(), quiet=quiet
    )

    if quiet:
        return
    for name, tool_info in get_global_registry().tools.items():
        if name not in EXCLUDED_NAMES:
            print(name, tool_info["description"], tool_info["permissions"])

# Uncomment the following line to manually bootstrap when needed
# bootstrap()

def get_global_registry():
    return tool_registry

GLOBAL_TOOL_REGISTRY = get_global_registry()
