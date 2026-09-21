@echo off
cd /d "%~dp0"
.venv\Scripts\python.exe scripts\coletar_evidencias.py
if errorlevel 1 goto erro
echo TESTES CONCLUIDOS. Abra 03_ABRIR_JUPYTERLAB.bat para estudar o notebook.
pause
exit /b 0
:erro
echo O teste foi interrompido. Envie uma captura da mensagem acima.
pause
exit /b 1
