@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv3.10\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo Python 3.10 virtual environment not found: %PYTHON%
    exit /b 1
)

pushd "%ROOT%"
"%PYTHON%" -m plover.scripts.dist_main %*
set "EXITCODE=%ERRORLEVEL%"
popd
exit /b %EXITCODE%