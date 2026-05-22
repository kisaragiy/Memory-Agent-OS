# agents/memory.py

GLOBAL_KERNEL = None

def get_kernel():
    global GLOBAL_KERNEL
    return GLOBAL_KERNEL

def init_kernel_if_needed(user_input: str):
    global GLOBAL_KERNEL

    if GLOBAL_KERNEL is None:
        from agents.state import StoryKernel
        GLOBAL_KERNEL = StoryKernel(seed_prompt=user_input)
