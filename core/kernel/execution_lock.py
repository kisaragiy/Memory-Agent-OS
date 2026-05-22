class ExecutionLock:
    def __init__(self):
        self.locked = False

    def acquire(self):
        if self.locked:
            raise Exception("Kernel already executing")
        self.locked = True

    def release(self):
        self.locked = False

    def guard(self, func):
        def wrapper(*args, **kwargs):
            self.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                self.release()
        return wrapper
