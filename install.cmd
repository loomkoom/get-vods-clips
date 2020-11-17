@ECHO OFF
python -V >nul 2>&1 || goto :python


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
echo Packages downloaded.
ffmpeg >nul 2>&1 ||goto :ffmpeg
echo Requirements satisfied.
echo Press Enter to exit.
set /p input=
exit

:python
	TITLE Error!
	echo Python not added to PATH or not installed. Download Latest python version at https://www.python.org/downloads/ and make sure you add to PATH: https://i.imgur.com/KXgMcOK.png
	echo Press any key to exit.
	pause >nul

:ffmpeg
	TITLE Warning!
	echo ffmpeg not added to PATH or not installed.
	echo If you want to be able to automatically download vods please install it.
	echo Download a ffmpeg version (recommended git full) at https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z for windows and make sure you add to PATH using GUI (https://windowsloop.com/install-ffmpeg-windows-10/#add-ffmpeg-to-Windows-path) or command line (set PATH=%%PATH%%;C:\path\to\ffmpeg\)
	echo Press any key to exit.
	pause >nul