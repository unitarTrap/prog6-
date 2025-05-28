import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from ferma_fact import fermat_factorization as py_fermat_factorization
import ferma_fact_cy  
import matplotlib.pyplot as plt

# Тестовые числа
TEST_LST = [
    101, 9973, 104729, 101909, 609133, 1300039,
    9999991, 99999959, 99999971, 3000009
]

NUM_WORKERS = 4  # Количество потоков или процессов


def worker_task(n, use_cython=True):
    """Вызывает нужную реализацию факторизации"""
    if use_cython:
        return ferma_fact_cy.fermat_factorization(n)
    else:
        return py_fermat_factorization(n)


def run_executor(executor_class, use_cython=True):
    """Запускает вычисления через выбранный исполнитель (потоки или процессы)"""
    start = time.time()
    results = []

    with executor_class(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(worker_task, n, use_cython) for n in TEST_LST]
        for future in as_completed(futures):
            results.append(future.result())

    end = time.time()
    return results, end - start


if __name__ == '__main__':
    timings = {}

    print("Многопоточность с обычной реализацией...")
    _, t_thread_py = run_executor(ThreadPoolExecutor, use_cython=False)
    timings['Потоки (Python)'] = t_thread_py

    print("Многопоточность с Cython-реализацией...")
    _, t_thread_cy = run_executor(ThreadPoolExecutor, use_cython=True)
    timings['Потоки (Cython)'] = t_thread_cy

    print("Многопроцессность с обычной реализацией...")
    _, t_proc_py = run_executor(ProcessPoolExecutor, use_cython=False)
    timings['Процессы (Python)'] = t_proc_py

    print("Многопроцессность с Cython-реализацией...")
    _, t_proc_cy = run_executor(ProcessPoolExecutor, use_cython=True)
    timings['Процессы (Cython)'] = t_proc_cy

    print("\nРезультаты выполнения:")
    for label, duration in timings.items():
        print(f"{label:25s} — {duration:.5f} сек")

    # Построение графика
    labels = list(timings.keys())
    times = list(timings.values())
    colors = ['gray', 'blue', 'orange', 'green']

    plt.figure(figsize=(9, 6))
    plt.bar(labels, times, color=colors)
    plt.ylabel("Время выполнения (сек)")
    plt.title("Сравнение многопоточности и многопроцессности (Python и Cython)")
    plt.xticks(rotation=15)

    for i, v in enumerate(times):
        plt.text(i, v + 0.05, f"{v:.3f}", ha='center')

    plt.tight_layout()
    plt.savefig("map_reduce_timings.png")
    plt.show()
