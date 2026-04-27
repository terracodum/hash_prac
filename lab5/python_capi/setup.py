from setuptools import setup, Extension
import pathlib

root = pathlib.Path(__file__).parent.parent

ext = Extension(
    "stats_capi",
    sources=[
        str(pathlib.Path(__file__).parent / "statsmodule.c"),
        str(root / "c_core" / "stats.c"),
    ],
    include_dirs=[str(root / "c_core")],
    extra_compile_args=["-O2"],
)

setup(name="stats_capi", ext_modules=[ext])
# Сборка: py -3.12 setup.py build_ext --inplace
