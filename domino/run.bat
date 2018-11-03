:start
@echo off

cls
echo.
echo ========================================================================================================================
echo                                                     Domino Compiler
echo ========================================================================================================================
echo.
echo         exit. exit      [path]. run file
echo.
echo ========================================================================================================================
echo.

set /p filepath=please insert the file path:

if %filepath%==exit exit

cls
python domino.py %filepath%
pause>nul
goto start