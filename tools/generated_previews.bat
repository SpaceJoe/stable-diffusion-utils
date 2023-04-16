cd ..
if not defined VENV_DIR (set "VENV_DIR=%~dp0%venv")
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
cd src
python preview.py <your target checkpoints dir>
pause