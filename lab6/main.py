import math
import timeit
from ferma_fact import fermat_factorization, is_perfect_square

# Пример использования
if __name__ == '__main__':
    time_res = timeit.repeat("res = [fermat_factorization(i) for i in TEST_LST];",
                  setup='import math; from main import is_perfect_square; from main import fermat_factorization; TEST_LST = [101, 9973, 104729, 101909, 609133, 1300039, 9999991, 99999959, 99999971, 3000009, 700000133, 61335395416403926747]',
                  number=10, repeat=1)
    print(time_res)