import pathlib
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    void compute_stats(const double* arr, int n,
                       double* out_mean,
                       double* out_variance,
                       double* out_std);
""")

_dll_path = pathlib.Path(__file__).parent.parent / "c_core" / "stats.dll"
_lib = ffi.dlopen(str(_dll_path))


def compute_stats(arr: list) -> tuple:
    n = len(arr)
    c_arr    = ffi.new("double[]", arr)
    out_mean = ffi.new("double*")
    out_var  = ffi.new("double*")
    out_std  = ffi.new("double*")
    _lib.compute_stats(c_arr, n, out_mean, out_var, out_std)
    return out_mean[0], out_var[0], out_std[0]


if __name__ == "__main__":
    import numpy as np
    rng = np.random.default_rng(0)
    data = rng.standard_normal(100).tolist()
    m, v, s = compute_stats(data)
    print(f"cffi    mean={m:.4f}  var={v:.4f}  std={s:.4f}")
