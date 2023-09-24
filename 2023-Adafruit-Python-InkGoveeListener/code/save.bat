@echo off
set PROJECT=Adafruit-Python-InkGoveeListener
set SRC=D:\

   REM SET YEAR=%DATE:~-4%
   REM SET MONTH=%DATE:~3,2%
   REM SET DAY=%DATE:~5,2%
   
   SET YYYYMMDD=%DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2%
set DEST=%USERPROFILE%\OneDrive\Documents\ElectronicsProjects\%PROJECT%\code_backup\%YYYYMMDD%

if not exist "%DEST%" (
	mkdir "%DEST%"
)
echo Copy files from %SRC% to %DEST%
copy "%SRC%\*.py" "%DEST%"
copy "%SRC%\*.bat" "%DEST%"
copy "%SRC%\*.bmp" "%DEST%"
copy "%SRC%\*.md" "%DEST%"

pause