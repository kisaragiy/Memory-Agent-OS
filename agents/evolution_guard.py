EVOLUTION_COUNTER = 0
EVOLUTION_LIMIT = 3   # 每 N 轮才允许一次进化


def allow_evolution():
    global EVOLUTION_COUNTER

    EVOLUTION_COUNTER += 1

    if EVOLUTION_COUNTER >= EVOLUTION_LIMIT:
        EVOLUTION_COUNTER = 0
        return True

    return False
