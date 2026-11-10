@echo off
cd /d "%~dp0"
python capturar.py >> captura.log 2>&1
