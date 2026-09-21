@echo off
cd /d "%~dp0"
echo VarejoMix V2 - Preparacao
python --version
if errorlevel 1 goto erro
docker compose version
if errorlevel 1 goto erro
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 goto erro
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erro
docker compose up -d --wait --wait-timeout 120
if errorlevel 1 goto erro
echo PREPARACAO CONCLUIDA. Execute agora 02_TESTAR_WINDOWS.bat.
pause
exit /b 0
:erro
echo Nao foi possivel concluir. Envie uma captura da mensagem de erro.
pause
exit /b 1
