@echo off
REM Install all production dependencies for local testing

echo =====================================================
echo Installing Production Dependencies
echo =====================================================

REM Activate virtual environment if it exists
if exist "THINK\Scripts\activate.bat" (
    echo Activating virtual environment...
    call THINK\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv THINK
    call THINK\Scripts\activate.bat
)

echo.
echo Installing packages from requirements_production.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements_production.txt

echo.
echo Verifying installations...
python -c "import undetected_chromedriver; import selenium; import selenium_stealth; import pandas; import psutil; print('✓ All imports successful')"

echo.
echo =====================================================
echo ✓ Installation complete!
echo =====================================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure
echo 2. Run: python production_harvester.py
echo.

pause

