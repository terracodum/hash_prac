#ifndef STATS_H
#define STATS_H

#ifdef _WIN32
  #define EXPORT __declspec(dllexport)
#else
  #define EXPORT __attribute__((visibility("default")))
#endif

EXPORT void compute_stats(const double* arr, int n,
                          double* out_mean,
                          double* out_variance,
                          double* out_std);

#endif
