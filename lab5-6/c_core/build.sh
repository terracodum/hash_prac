#!/usr/bin/env bash
# Сборка stats.so (Linux/macOS)
set -e
gcc -shared -fPIC -O2 -o stats.so stats.c -lm
echo "[OK] stats.so собран"
