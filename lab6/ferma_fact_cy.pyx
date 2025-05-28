import cython
from libc.math cimport sqrt, floor

# Функция, безопасная для работы без GIL
cdef void fermat_factorization_raw(long long N, long long* a, long long* b) nogil:
    if N % 2 == 0:
        a[0] = 2
        b[0] = N // 2
        return

    cdef long long x = <long long>floor(sqrt(N)) + 1
    cdef long long y_squared, y

    while True:
        y_squared = x * x - N
        y = <long long>floor(sqrt(y_squared))
        if y * y == y_squared:
            a[0] = x - y
            b[0] = x + y
            return
        x += 1

# Python-обёртка — работает с GIL, возвращает Python-кортеж
@cython.boundscheck(False)
@cython.wraparound(False)
cpdef tuple fermat_factorization(long long N):
    cdef long long a, b
    with nogil:
        fermat_factorization_raw(N, &a, &b)
    return (a, b)
