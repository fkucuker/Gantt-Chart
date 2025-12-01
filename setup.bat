@echo off
REM =============================================================================
REM Gantt Chart Application - Windows Batch Setup Script
REM =============================================================================
REM Kullanim: setup.bat [komut]
REM Komutlar: setup, start, stop, restart, logs, migrate, seed, dev, clean, help
REM =============================================================================

setlocal enabledelayedexpansion

if "%1"=="" goto :help
if "%1"=="setup" goto :setup
if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="logs-api" goto :logs-api
if "%1"=="logs-web" goto :logs-web
if "%1"=="logs-db" goto :logs-db
if "%1"=="migrate" goto :migrate
if "%1"=="seed" goto :seed
if "%1"=="dev" goto :dev
if "%1"=="dev-stop" goto :dev-stop
if "%1"=="clean" goto :clean
if "%1"=="clean-all" goto :clean-all
if "%1"=="test" goto :test
if "%1"=="help" goto :help
echo [!] Bilinmeyen komut: %1
goto :help

:check-docker
echo [*] Docker kontrol ediliyor...
docker version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [X] HATA: Docker kurulu degil!
    echo.
    echo     Docker Desktop'i indirin:
    echo     https://www.docker.com/products/docker-desktop
    echo.
    exit /b 1
)
echo [OK] Docker kurulu.

docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo [X] HATA: Docker Desktop calismiyorl!
    echo.
    echo     Lutfen Docker Desktop'i baslatin ve tekrar deneyin.
    echo.
    exit /b 1
)
echo [OK] Docker Desktop calisiyor.
goto :eof

:check-env
if not exist ".env" (
    echo [*] .env dosyasi olusturuluyor...
    copy "infra\env.example" ".env" >nul
    echo [OK] .env dosyasi olusturuldu.
) else (
    echo [OK] .env dosyasi mevcut.
)
goto :eof

:wait-for-db
echo [*] Veritabani baglantisi kontrol ediliyor...
set attempts=0
:db_loop
if %attempts% geq 30 (
    echo.
    echo [!] Veritabani baglantisi zaman asimina ugradi, devam ediliyor...
    goto :eof
)
cd infra
docker compose --env-file ..\.env exec -T db pg_isready -U gantt_user -d gantt_app >nul 2>&1
if errorlevel 1 (
    cd ..
    set /a attempts+=1
    echo|set /p="."
    timeout /t 2 /nobreak >nul
    goto :db_loop
)
cd ..
echo.
echo [OK] Veritabani hazir.
goto :eof

:setup
echo.
echo ===================================================================
echo          Gantt Chart - Sifirdan Kurulum Basliyor
echo ===================================================================
echo.

call :check-docker
if errorlevel 1 exit /b 1

call :check-env

echo [*] Docker image'lari build ediliyor...
cd infra
docker compose --env-file ..\.env build
if errorlevel 1 (
    cd ..
    echo [X] Build hatasi!
    exit /b 1
)
cd ..
echo [OK] Build tamamlandi.

echo [*] Servisler baslatiliyor...
cd infra
docker compose --env-file ..\.env up -d
if errorlevel 1 (
    cd ..
    echo [X] Servisler baslatilamadi!
    exit /b 1
)
cd ..
echo [OK] Servisler baslatildi.

call :wait-for-db

REM Ekstra bekleme
timeout /t 3 /nobreak >nul

echo [*] Migration'lar calistiriliyor...
cd infra
docker compose --env-file ..\.env exec -T api alembic upgrade head
if errorlevel 1 (
    cd ..
    echo [X] Migration hatasi!
    exit /b 1
)
cd ..
echo [OK] Migration'lar tamamlandi.

echo [*] Ornek veriler yukleniyor...
cd infra
docker compose --env-file ..\.env exec -T api python seed.py
if errorlevel 1 (
    cd ..
    echo [X] Seed hatasi!
    exit /b 1
)
cd ..
echo [OK] Seed tamamlandi.

echo.
echo ===================================================================
echo                    KURULUM TAMAMLANDI!
echo ===================================================================
echo.
echo Uygulama adresleri:
echo    Frontend: http://localhost
echo    Backend:  http://localhost:5000
echo.
echo Demo hesaplari:
echo    Admin:  admin@gantt.local / admin123
echo    Editor: editor@gantt.local / editor123
echo    Viewer: viewer@gantt.local / viewer123
echo.

set /p openBrowser="Tarayicida acilsin mi? (E/h): "
if /i not "%openBrowser%"=="h" (
    start http://localhost
)
goto :eof

:start
call :check-docker
if errorlevel 1 exit /b 1
call :check-env
echo [*] Servisler baslatiliyor...
cd infra
docker compose --env-file ..\.env up -d
cd ..
echo [OK] Servisler baslatildi.
echo Frontend: http://localhost ^| Backend: http://localhost:5000
goto :eof

:stop
echo [*] Servisler durduruluyor...
cd infra
docker compose --env-file ..\.env down
cd ..
echo [OK] Servisler durduruldu.
goto :eof

:restart
call :stop
call :start
goto :eof

:status
echo [*] Servis durumlari:
cd infra
docker compose --env-file ..\.env ps
cd ..
goto :eof

:logs
cd infra
docker compose --env-file ..\.env logs -f
cd ..
goto :eof

:logs-api
cd infra
docker compose --env-file ..\.env logs -f api
cd ..
goto :eof

:logs-web
cd infra
docker compose --env-file ..\.env logs -f web
cd ..
goto :eof

:logs-db
cd infra
docker compose --env-file ..\.env logs -f db
cd ..
goto :eof

:migrate
echo [*] Migration'lar calistiriliyor...
cd infra
docker compose --env-file ..\.env exec -T api alembic upgrade head
cd ..
echo [OK] Migration'lar tamamlandi.
goto :eof

:seed
echo [*] Ornek veriler yukleniyor...
cd infra
docker compose --env-file ..\.env exec -T api python seed.py
cd ..
echo [OK] Seed tamamlandi.
goto :eof

:dev
call :check-docker
if errorlevel 1 exit /b 1
call :check-env
echo [*] Gelistirme ortami baslatiliyor (sadece DB)...
cd infra
docker compose --env-file ..\.env -f docker-compose.dev.yml up -d
cd ..
echo [OK] PostgreSQL calisiyor: localhost:5432
echo.
echo Sonraki adimlar:
echo    Backend:  cd backend ^&^& pip install -r requirements.txt ^&^& flask run --debug
echo    Frontend: cd frontend ^&^& npm install ^&^& npm run dev
goto :eof

:dev-stop
echo [*] Gelistirme ortami durduruluyor...
cd infra
docker compose --env-file ..\.env -f docker-compose.dev.yml down
cd ..
echo [OK] Gelistirme ortami durduruldu.
goto :eof

:clean
echo [*] Temizlik yapiliyor...
cd infra
docker compose --env-file ..\.env down -v --remove-orphans
cd ..
echo [OK] Container ve volume'lar temizlendi.
goto :eof

:clean-all
call :clean
echo [*] Docker image'lari siliniyor...
docker rmi infra-api infra-web 2>nul
echo [OK] Tum kaynaklar temizlendi.
goto :eof

:test
echo [*] Backend testleri calistiriliyor...
cd infra
docker compose --env-file ..\.env exec -T api pytest -v
cd ..
goto :eof

:help
echo.
echo ===================================================================
echo          Gantt Chart - Faaliyet Planlama Uygulamasi
echo ===================================================================
echo.
echo KULLANIM:
echo    setup.bat [komut]
echo.
echo HIZLI BASLANGIC:
echo    setup.bat setup      - Sifirdan tam kurulum (onerilen)
echo.
echo DOCKER KOMUTLARI:
echo    setup.bat start      - Servisleri baslat
echo    setup.bat stop       - Servisleri durdur
echo    setup.bat restart    - Servisleri yeniden baslat
echo    setup.bat status     - Servis durumlarini goster
echo    setup.bat logs       - Tum loglari goster
echo    setup.bat logs-api   - API loglarini goster
echo    setup.bat logs-web   - Web loglarini goster
echo    setup.bat logs-db    - DB loglarini goster
echo.
echo VERITABANI:
echo    setup.bat migrate    - Migration'lari calistir
echo    setup.bat seed       - Ornek veri yukle
echo.
echo GELISTIRME:
echo    setup.bat dev        - Dev ortami baslat (sadece DB)
echo    setup.bat dev-stop   - Dev ortamini durdur
echo.
echo TEST:
echo    setup.bat test       - Backend testlerini calistir
echo.
echo TEMIZLIK:
echo    setup.bat clean      - Container ve volume'lari sil
echo    setup.bat clean-all  - Her seyi sil (image'lar dahil)
echo.
echo ONGEREKSINIMLER:
echo    - Docker Desktop (https://www.docker.com/products/docker-desktop)
echo.
goto :eof
