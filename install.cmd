@ECHO OFF
FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
echo Checking/Installing requirements...
echo[
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Requirements installation failed. Perhaps some dependency is missing or access was denied? Possible solutions:
    echo - Run as administrator
    echo - Google the error
    echo Press any key to exit.
    set /p input=
    exit
)
echo[
echo Requirements satisfied.
echo Press Enter to exit.
set /p input=
exit