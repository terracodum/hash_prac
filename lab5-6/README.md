# Лабораторная работа №5 — FFI: вызов C из Python

**Вариант 5:** вычисление среднего, дисперсии и стандартного отклонения массива.

---

## Что реализовано

### C-функция (`c_core/`)

Файлы: `stats.h`, `stats.c`

```c
void compute_stats(const double* arr, int n,
                   double* out_mean,
                   double* out_variance,
                   double* out_std);
```

Принимает массив вещественных чисел и три выходных указателя.  
Считает mean/variance/std за два прохода по массиву.  
Собирается в `stats.dll` командой `build.bat` (нужен GCC).

---

### Четыре способа вызова из Python

#### 1. ctypes (`python_ctypes/bench_ctypes.py`)
Загружает `stats.dll` через `ctypes.CDLL`.  
Объявляет типы аргументов (`argtypes`) и возвращаемого значения (`restype`).  
Передаёт массив как `(c_double * n)(*arr)`, результаты через `byref`.

#### 2. cffi (`python_cffi/bench_cffi.py`)
Описывает сигнатуру функции через `ffi.cdef(...)`.  
Загружает DLL через `ffi.dlopen(...)`.  
Массив создаётся как `ffi.new("double[]", arr)`.

#### 3. CPython C API (`python_capi/statsmodule.c` + `setup.py`)
Полноценный модуль-расширение на C.  
Принимает Python-список, конвертирует в `double*`, вызывает `compute_stats`, возвращает кортеж через `Py_BuildValue("(ddd)", ...)`.  
Сборка: `py -3.12 setup.py build_ext --inplace`

#### 4. Cython (`python_cython/stats_cy.pyx` + `setup.py`)
`.pyx`-файл объявляет `cdef extern` на заголовок `stats.h`.  
Python-обёртка `stats(list arr)` переводит список в `double*` и вызывает C-функцию.  
Сборка: `py -3.12 setup.py build_ext --inplace`

---

## Бенчмарк (`benchmark/benchmark.ipynb`)

- **Тестовые данные:** 100 000 массивов по 100 элементов, `seed=42`
- **Схема:** разогрев 1 000 вызовов → 50 замеров × 100 000 вызовов
- **Метрики:** min, max, mean, median, std
- **Графики:** bar chart по среднему + boxplot по 50 замерам
- ctypes и cffi работают без предварительной компиляции; C API и Cython — опционально

---

## Как запустить

```bat
REM 1. Собрать DLL (нужен gcc)
cd lab5\c_core
build.bat

REM 2. (Опционально) собрать C API
cd ..\python_capi
py -3.12 setup.py build_ext --inplace

REM 3. (Опционально) собрать Cython
cd ..\python_cython
py -3.12 setup.py build_ext --inplace

REM 4. Открыть ноутбук
cd ..\benchmark
jupyter notebook benchmark.ipynb
```

> Если gcc нет: `winget install MSYS2.MSYS2` или `scoop install gcc`

---

## Ожидаемые результаты

| Подход | Скорость | Сложность реализации |
|--------|----------|----------------------|
| ctypes | средняя | минимальная — чистый Python |
| cffi | средняя | низкая — декларативный cdef |
| C API | высокая | высокая — C-код вручную |
| Cython | высокая | средняя — Python-подобный синтаксис |

ctypes и cffi медленнее из-за маршалинга типов при каждом вызове.  
C API и Cython работают напрямую внутри интерпретатора — накладные расходы минимальны.
