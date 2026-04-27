import ctypes
import pathlib

_dll_path = pathlib.Path(__file__).parent.parent / "c_core" / "stats.dll"
_lib = ctypes.CDLL(str(_dll_path))

_lib.compute_stats.restype = None
_lib.compute_stats.argtypes = [
    ctypes.POINTER(ctypes.c_double),  # arr
    ctypes.c_int,                     # n
    ctypes.POINTER(ctypes.c_double),  # out_mean
    ctypes.POINTER(ctypes.c_double),  # out_variance
    ctypes.POINTER(ctypes.c_double),  # out_std
]


def compute_stats(arr: list) -> tuple:
    n = len(arr)
    c_arr = (ctypes.c_double * n)(*arr)
    mean = ctypes.c_double()
    var  = ctypes.c_double()
    std  = ctypes.c_double()
    _lib.compute_stats(c_arr, n,
                       ctypes.byref(mean),
                       ctypes.byref(var),
                       ctypes.byref(std))
    return mean.value, var.value, std.value


if __name__ == "__main__":
    import numpy as np
    rng = np.random.default_rng(0)
    data = rng.standard_normal(100).tolist()
    m, v, s = compute_stats(data)
    print(f"ctypes  mean={m:.4f}  var={v:.4f}  std={s:.4f}")
