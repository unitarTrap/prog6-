import time
import multiprocessing
import threading
from queue import Queue
import matplotlib.pyplot as plt

from ferma_fact import fermat_factorization as py_fermat
import ferma_fact_cy


TEST_LST = [101, 9973, 104729, 101909, 609133, 1300039, 9999991, 99999959, 99999971, 3000009]

# Функции-обёртки
def run_py(x): return py_fermat(x)
def run_cy(x): return ferma_fact_cy.fermat_factorization(x)


# Потоковая версия
def thread_worker(queue, results, func):
    while not queue.empty():
        try:
            num = queue.get_nowait()
        except:
            return
        res = func(num)
        results.append((num, res))


def thread_map_reduce(data, func, n_threads=4):
    q = Queue()
    for item in data:
        q.put(item)
    threads = []
    results = []
    start = time.time()
    for _ in range(n_threads):
        t = threading.Thread(target=thread_worker, args=(q, results, func))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    return results, end - start


# Процессная версия
def process_worker(subdata, func, output):
    results = [func(x) for x in subdata]
    output.put(results)


def process_map_reduce(data, func, n_processes=4):
    chunk_size = len(data) // n_processes
    chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(n_processes)]
    if len(data) % n_processes != 0:
        chunks[-1].extend(data[n_processes * chunk_size:])
    processes = []
    output = multiprocessing.Queue()
    start = time.time()
    for chunk in chunks:
        p = multiprocessing.Process(target=process_worker, args=(chunk, func, output))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    results = []
    while not output.empty():
        results.extend(output.get())
    end = time.time()
    return results, end - start


# Визуализация
def plot_results(results):
    labels = list(results.keys())
    times = list(results.values())
    plt.figure(figsize=(10, 6))
    plt.barh(labels, times, color='skyblue')
    plt.xlabel("Время выполнения (сек)")
    plt.title("Сравнение: Потоки vs Процессы, Python vs Cython")
    for i, v in enumerate(times):
        plt.text(v + 0.01, i, f"{v:.4f} сек", va='center')
    plt.tight_layout()
    plt.savefig("map_reduce_comparison.png")
    plt.show()


if __name__ == '__main__':
    results = {}

    # Потоки
    _, t1 = thread_map_reduce(TEST_LST, run_py, n_threads=4)
    results['Thread Python'] = t1
    _, t2 = thread_map_reduce(TEST_LST, run_cy, n_threads=4)
    results['Thread Cython'] = t2

    # Процессы
    _, t3 = process_map_reduce(TEST_LST, run_py, n_processes=4)
    results['Process Python'] = t3
    _, t4 = process_map_reduce(TEST_LST, run_cy, n_processes=4)
    results['Process Cython'] = t4

    for name, t in results.items():
        print(f"{name}: {t:.4f} сек")

    plot_results(results)
