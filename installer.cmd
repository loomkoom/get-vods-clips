@Echo Off
SETLOCAL EnableDelayedExpansion
:: code for colored lines
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do     rem"') do (
  set "DEL=%%a"
)
SET root=%~dp0
pushd %~dp0

:: installing with scoop
call :colorEcho 0B "Installing scoop and any program dependencies (scoop needs administrator access on first install)"
echo[
call powershell -NoProfile -ExecutionPolicy Bypass -NoLogo -File ./inst/scoop-installer.ps1
echo[

call ./inst/RefreshEnv.cmd

:: testing that programs are installed
python -V >nul 2>&1 || goto :python
git --version >nul 2>&1 || goto :git
mpv -V >nul 2>&1 || goto :mpv
ffmpeg -version >nul 2>&1 || goto :ffmpeg
echo[
call :colorEcho 0B "Installing or updating Get-vods-clips now"
echo[

for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i

if not exist .git\ (
	echo[
    echo This seems to be your first run The setup will now proceed to download all required files They will be downloaded to the same location as where this install file is.
    echo[
	echo[
    git init . >nul
    git remote add origin https://github.com/loomkoom/get-vods-clips.git >nul 2>&1
    git fetch --all
	git reset --hard origin/main
)

git fetch origin main >nul 2>&1
git remote show origin > tmp.txt
set findfile="tmp.txt"
set findtext="up"
findstr %findtext% %findfile% >nul 2>&1 || goto :forward
goto :install

:python
	TITLE Error!
	call :colorEcho 04 "python not added to PATH or not installed"
	echo[
	echo run installer again or download latest python version manually at https://www.python.org/downloads/ and make sure you add to PATH: https://i.imgur.com/KXgMcOK.png
    goto :end
:git
	TITLE Error!
	call :colorEcho 04 "git not added to PATH or not installed"
	echo[
	echo run installer again or download git manually at https://git-scm.com/
    goto :end
:ffmpeg
	TITLE Warning!
	call :colorEcho 04 "ffmpeg not added to PATH or not installed"
	echo[
	echo run installer again or download a ffmpeg version manually at https://ffmpeg.org/download.html#build-windows and make sure you add to PATH
    goto :end
:mpv
	TITLE Error!
	call :colorEcho 04 "mpv not installed or not added to path"
    echo[
    echo run installer again or download mpv manually at https://mpv.io/installation/
    goto :end

:forward
	set findfile="tmp.txt"
	set forwardable="fast-forwardable"
	findstr %forwardable% %findfile% >nul 2>&1
	goto :update
:update
	echo Starting update...
	echo Latest update:
	git --no-pager log --pretty=oneline -n1 origin/%BRANCH% ^%BRANCH%
	git pull origin %BRANCH%
	if errorlevel 1 goto force
	echo Finished updating
	goto :install
:force
	git fetch --all
	git reset --hard origin/%BRANCH%
	echo Finished updating
	goto :install

:install
	if exist tmp.txt del tmp.txt
	FOR /f %%p in ('where python') do SET PYTHONPATH=%%p
	call :colorEcho 0B "Checking-Installing requirements (takes some time on first install)"
    echo[
	chcp 65001 >nul
	set PYTHONIOENCODING=utf-8
	call :colorEcho 0B "Installing python packages"
    echo[
	python -m pip install --upgrade pip
	python -m pip install wheel
	python -m pip install -r requirements.txt
    if errorlevel 1 (
        call :colorEcho 04 "Requirements installation failed, Perhaps some dependency is missing or access was denied"
        echo Possible solutions:
        echo    - Run as administrator"
        echo    - Google the error"
        pause
        exit
    )
    call :colorEcho 0A "All python packages installed"
    echo[
	ping 127.0.0.1 -n 2 > nul
	type success.txt
	echo[
	echo[
	if %ERRORLEVEL% == 15 goto :update
	goto :end

:end
    pause
    exit
:colorEcho
    <nul set /p ".=%DEL%" > "%~2"
    findstr /v /a:%1 /R "^$" "%~2" nul
    del "%~2" > nul 2>&1i
