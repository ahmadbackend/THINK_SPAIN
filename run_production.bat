@echo off
REM Windows batch file to run production harvester

echo =====================================================
echo PRODUCTION HARVESTER - Windows
echo =====================================================

REM Activate virtual environment if it exists
if exist "THINK\Scripts\activate.bat" (
    echo Activating virtual environment...
    call THINK\Scripts\activate.bat
)

echo Starting production harvester...
python production_harvester.py

pause

