"""
Генерирует тестовые данные для бенчмарка: N_CALLS массивов по ARR_SIZE элементов.
Seed фиксирован — результаты воспроизводимы.
"""
import numpy as np

N_CALLS  = 100_000
ARR_SIZE = 100
SEED     = 42


def generate() -> list[list[float]]:
    rng = np.random.default_rng(SEED)
    return [rng.standard_normal(ARR_SIZE).tolist() for _ in range(N_CALLS)]


if __name__ == "__main__":
    data = generate()
    print(f"Сгенерировано {len(data)} массивов × {ARR_SIZE} элементов (seed={SEED})")
