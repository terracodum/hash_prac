#include "stats.h"
#include <math.h>
#include <stdlib.h>

void compute_stats(const double* arr, int n,
                   double* out_mean,
                   double* out_variance,
                   double* out_std)
{
    if (!arr || n <= 0 || !out_mean || !out_variance || !out_std) {
        if (out_mean)     *out_mean     = 0.0;
        if (out_variance) *out_variance = 0.0;
        if (out_std)      *out_std      = 0.0;
        return;
    }

    double sum = 0.0;
    for (int i = 0; i < n; i++) sum += arr[i];
    double mean = sum / n;

    double var_sum = 0.0;
    for (int i = 0; i < n; i++) {
        double d = arr[i] - mean;
        var_sum += d * d;
    }
    double variance = var_sum / n;

    *out_mean     = mean;
    *out_variance = variance;
    *out_std      = sqrt(variance);
}
