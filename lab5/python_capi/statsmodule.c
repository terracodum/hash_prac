#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include "../c_core/stats.h"

static PyObject* py_compute_stats(PyObject* self, PyObject* args)
{
    PyObject* seq;
    if (!PyArg_ParseTuple(args, "O", &seq))
        return NULL;

    seq = PySequence_Fast(seq, "argument must be a sequence");
    if (!seq) return NULL;

    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq);
    if (n <= 0) {
        Py_DECREF(seq);
        PyErr_SetString(PyExc_ValueError, "array must be non-empty");
        return NULL;
    }

    double* arr = (double*)malloc((size_t)n * sizeof(double));
    if (!arr) {
        Py_DECREF(seq);
        return PyErr_NoMemory();
    }

    for (Py_ssize_t i = 0; i < n; i++) {
        double v = PyFloat_AsDouble(PySequence_Fast_GET_ITEM(seq, i));
        if (v == -1.0 && PyErr_Occurred()) {
            free(arr);
            Py_DECREF(seq);
            return NULL;
        }
        arr[i] = v;
    }
    Py_DECREF(seq);

    double out_mean, out_var, out_std;
    compute_stats(arr, (int)n, &out_mean, &out_var, &out_std);
    free(arr);

    return Py_BuildValue("(ddd)", out_mean, out_var, out_std);
}

static PyMethodDef StatsMethods[] = {
    {"compute_stats", py_compute_stats, METH_VARARGS,
     "compute_stats(arr) -> (mean, variance, std)"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef statsmodule = {
    PyModuleDef_HEAD_INIT, "stats_capi", NULL, -1, StatsMethods
};

PyMODINIT_FUNC PyInit_stats_capi(void)
{
    return PyModule_Create(&statsmodule);
}
