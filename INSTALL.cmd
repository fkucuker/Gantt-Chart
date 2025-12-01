@echo off
REM =============================================================================
REM Gantt Chart Application - Tek Tikla Kurulum
REM =============================================================================
REM Bu dosyaya cift tiklayarak uygulamayi sifirdan kurabilirsiniz.
REM =============================================================================

title Gantt Chart - Kurulum

cd /d "%~dp0"

echo.
echo  ===================================================================
echo.
echo     ██████╗  █████╗ ███╗   ██╗████████╗████████╗
echo    ██╔════╝ ██╔══██╗████╗  ██║╚══██╔══╝╚══██╔══╝
echo    ██║  ███╗███████║██╔██╗ ██║   ██║      ██║   
echo    ██║   ██║██╔══██║██║╚██╗██║   ██║      ██║   
echo    ╚██████╔╝██║  ██║██║ ╚████║   ██║      ██║   
echo     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝      ╚═╝   
echo.
echo            Faaliyet Planlama Uygulamasi
echo.
echo  ===================================================================
echo.

echo [*] Ongereksinimler kontrol ediliyor...
echo.

REM Docker kurulu mu?
docker version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [X] HATA: Docker kurulu degil!
    echo.
    echo      Docker Desktop'i asagidaki adresten indirin:
    echo      https://www.docker.com/products/docker-desktop
    echo.
    echo      Kurduktan sonra bu dosyayi tekrar calistirin.
    echo.
    pause
    exit /b 1
)
echo  [OK] Docker kurulu.

REM Docker calisiyor mu?
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [X] HATA: Docker Desktop calismiyorl!
    echo.
    echo      Lutfen Docker Desktop uygulamasini baslatin
    echo      ve bu dosyayi tekrar calistirin.
    echo.
    pause
    exit /b 1
)
echo  [OK] Docker Desktop calisiyor.

echo.
echo  ===================================================================
echo   Kurulum baslatiliyor. Bu islem birkac dakika surebilir...
echo  ===================================================================
echo.

REM setup.bat setup komutunu calistir
call setup.bat setup

echo.
echo  ===================================================================
echo   Herhangi bir tusa basin...
echo  ===================================================================
pause >nul

