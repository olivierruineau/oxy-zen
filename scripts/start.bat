@echo off
REM Script de lancement d'Oxy-Zen
cd /d "%~dp0\.."
echo 🧘 Lancement d'Oxy-Zen...
uv run python main.py
