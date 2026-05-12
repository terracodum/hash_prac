from setuptools import setup, Extension
from Cython.Build import cythonize
import pathlib

root = pathlib.Path(__file__).parent.parent

ext = Extension(
    "stats_cy",
    sources=[
        str(pathlib.Path(__file__).parent / "stats_cy.pyx"),
        str(root / "c_core" / "stats.c"),
    ],
    include_dirs=[str(root / "c_core")],
    extra_compile_args=["-O2"],
)

setup(name="stats_cy", ext_modules=cythonize([ext], language_level="3"))
# Сборка: py -3.12 setup.py build_ext --inplace
