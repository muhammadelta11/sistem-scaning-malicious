@echo off
REM Batch script to run performance benchmark
REM This script sets up the environment and runs the benchmark

echo Setting up environment for performance benchmark...

REM Change to the Django project directory
cd /d %~dp0..

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found, using system Python
)

REM Run the benchmark script
python scanner/performance_benchmark.py %*

REM Deactivate virtual environment
if exist venv\Scripts\deactivate.bat (
    call venv\Scripts\deactivate.bat
)

echo Benchmark completed.
pause
