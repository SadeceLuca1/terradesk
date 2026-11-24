@echo off
echo ========================================
echo   TerraDesk Kurulum Baslıyor...
echo ========================================
echo.

REM Python kontrolu
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.11+ yukleyin.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python bulundu:
python --version
echo.

REM pip guncelle
echo pip guncelleniyor...
python -m pip install --upgrade pip

echo.
echo Bagimliliklar yukleniyor (pygame-ce, pywin32)...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [HATA] Bagimlilik yukleme basarisiz oldu!
    echo pygame-ce yerine klasik pygame denemek icin:
    echo   python -m pip install pygame^>=2.6.0
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Kurulum tamamlandi!
echo   Oyunu baslatmak icin: python main.py
echo ========================================
pause
