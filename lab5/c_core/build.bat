@echo off
REM Сборка stats.dll через GCC (MinGW/MSYS2)
REM Если нет gcc — поставь: winget install MSYS2.MSYS2  или  scoop install gcc

gcc -shared -fPIC -O2 -o stats.dll stats.c -lm
if %errorlevel% == 0 (
    echo [OK] stats.dll собран
) else (
    echo [FAIL] Ошибка сборки. Убедись что gcc доступен в PATH.
)
