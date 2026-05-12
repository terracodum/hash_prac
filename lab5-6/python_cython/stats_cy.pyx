from libc.stdlib cimport malloc, free

cdef extern from "../c_core/stats.h":
    void compute_stats(const double* arr, int n,
                       double* out_mean,
                       double* out_variance,
                       double* out_std)


def stats(list arr):
    cdef int n = len(arr)
    if n <= 0:
        raise ValueError("array must be non-empty")

    cdef double* c_arr = <double*>malloc(n * sizeof(double))
    if not c_arr:
        raise MemoryError()

    for i in range(n):
        c_arr[i] = arr[i]

    cdef double out_mean, out_var, out_std
    compute_stats(c_arr, n, &out_mean, &out_var, &out_std)
    free(c_arr)

    return out_mean, out_var, out_std
