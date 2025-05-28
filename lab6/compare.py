import timeit
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import time
import signal

# Функция-обработчик для ограничения времени выполнения
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Превышено время выполнения")

# Компилируем Cython модуль
print("Компиляция Cython модуля...")
subprocess.run(["python", "setup.py", "build_ext", "--inplace"], check=True)

# Импортируем Cython модуль
import ferma_fact_cy  # type: ignore
from ferma_fact import fermat_factorization as py_fermat_factorization, is_perfect_square

# Тестовые числа
TEST_LST = [101, 9973, 104729, 101909, 609133]
REPEAT = 3
NUMBER = 5

# Проверка, что обе реализации дают одинаковый результат
print("Проверка корректности...")
for num in TEST_LST:
    py_result = py_fermat_factorization(num)
    cy_result = ferma_fact_cy.fermat_factorization(num)
    assert py_result == cy_result, f"Разные результаты для {num}: Python {py_result}, Cython {cy_result}"

print("Измерение времени выполнения...")

# Измерение времени Python версии
try:
    py_times = timeit.repeat(
        "res = [py_fermat_factorization(i) for i in TEST_LST]",
        setup='from __main__ import py_fermat_factorization, TEST_LST',
        number=NUMBER,
        repeat=REPEAT
    )
    py_best = min(py_times)
except Exception as e:
    print(f"Ошибка при измерении времени Python версии: {e}")
    py_best = float('inf')

# Измерение времени Cython версии
try:
    cy_times = timeit.repeat(
        "res = [ferma_fact_cy.fermat_factorization(i) for i in TEST_LST]",
        setup='from __main__ import ferma_fact_cy, TEST_LST',
        number=NUMBER,
        repeat=REPEAT
    )
    cy_best = min(cy_times)
except Exception as e:
    print(f"Ошибка при измерении времени Cython версии: {e}")
    cy_best = float('inf')

# Проверка, что у нас есть результаты для обеих версий
if py_best == float('inf') and cy_best == float('inf'):
    print("Не удалось измерить время выполнения ни для одной версии")
    exit(1)
elif py_best == float('inf'):
    print("Не удалось измерить время выполнения Python версии")
    speedup = float('inf')
elif cy_best == float('inf'):
    print("Не удалось измерить время выполнения Cython версии")
    speedup = 0
else:
    speedup = py_best / cy_best

print(f"Время выполнения Python: {py_best:.5f} секунд")
print(f"Время выполнения Cython: {cy_best:.5f} секунд")
print(f"Ускорение: {speedup:.2f}x")

# Построение графика сравнения
labels = ['Python', 'Cython']
times = [py_best if py_best != float('inf') else 0, cy_best if cy_best != float('inf') else 0]
colors = ['red', 'blue']

plt.figure(figsize=(7, 5))
plt.bar(labels, times, color=colors, width=0.5)
plt.title('Сравнение производительности Python и Cython')
plt.xlabel('Реализация')
plt.ylabel('Время выполнения (сек)')

for i, v in enumerate(times):
    if v > 0:
        plt.text(i, v + 0.05, f"{v:.5f} сек", ha='center')
    else:
        plt.text(i, 0.05, "Timeout", ha='center')

plt.savefig('performance_comparison.png')
plt.tight_layout()
plt.show()

print("\nТестирование завершено. Результаты сохранены в файле performance_comparison.png.")
