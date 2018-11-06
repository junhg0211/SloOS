:start
@echo off

:mainpage
set a=a

cls
echo.
echo ========================================================================================================================
echo                                                   Slo OS Debugger
echo                                                      MainPage
echo ========================================================================================================================
echo.
echo         1. Dibeogeu                                      0. Jongryo
echo         2. Saeksang byeongyeong
echo.
echo ========================================================================================================================
echo.

set /p a=Weonha-neun gineung-eul ipryeok hago, Enter key-reul nuruseyo:

if %a%==1 goto run
if %a%==2 goto yet
if %a%==0 exit

goto mainpage

:run
cls
python .\src\Main.pyw
echo.
echo Program-i jongryo doeeot-seupnida. Amu key-na nulleoseo mainpage-ro doragapnida.
echo.
pause>nul

goto mainpage

:yet
cls
echo.
echo ========================================================================================================================
echo                                                   Slo OS Debugger
echo                                                        Error
echo ========================================================================================================================
echo.
echo                                       Ajik gaebal doeji anun gineung ipnida.
echo                                Amu key-na nulleoseo main-hwamyeon-euro doragapnida.
echo.
echo ========================================================================================================================
echo.
pause>nul

goto mainpage

