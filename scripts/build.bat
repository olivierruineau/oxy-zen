@echo off
REM Script de build pour créer l'exécutable Windows OxyZen.exe
REM Nécessite uv (https://github.com/astral-sh/uv)

echo ========================================
echo    Oxy-Zen - Build Executable
echo ========================================
echo.

REM Vérifier que uv est installé
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] uv n'est pas installe ou pas dans le PATH
    echo Installe uv depuis: https://github.com/astral-sh/uv
    exit /b 1
)

echo [1/3] Installation des dependances (avec PyInstaller)...
uv sync --group dev
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec de l'installation des dependances
    exit /b 1
)

echo.
echo [2/3] Generation de l'executable avec PyInstaller...
uv run pyinstaller build.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Echec de la generation de l'executable
    exit /b 1
)

echo.
echo [3/3] Nettoyage...
REM Les fichiers temporaires sont dans build/ (conserve pour debug)

echo.
echo ========================================
echo   Build termine avec succes !
echo ========================================
echo.
echo Executable genere : dist\OxyZen.exe
echo.
echo Pour tester :
echo   cd dist
echo   .\OxyZen.exe
echo.
echo Pour l'auto-demarrage :
echo   1. Win+R puis taper : shell:startup
echo   2. Copier dist\OxyZen.exe ou creer un raccourci
echo.

pause
