:start
@echo off

cls
echo.
echo ========================================================================================================================
echo                                                     Domino Compiler
echo ========================================================================================================================
echo.
echo         exit. exit      1. a.dmn        [path]. run file
echo.
echo ========================================================================================================================
echo.

set /p filepath=please insert the file path:

if %filepath%==exit exit
if %filepath%==1 set filepath=a.dmn

cls
python domino.py %filepath%
pause
goto start
