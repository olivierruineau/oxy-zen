@echo off
REM Script pour tuer tous les processus oxy-zen
echo 🔪 Arrêt de tous les processus Oxy-Zen...
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*oxy-zen*'} | Stop-Process -Force"
echo ✅ Terminé!
pause
