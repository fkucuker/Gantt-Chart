# =============================================================================
# Gantt Chart Application - Windows PowerShell Setup Script
# =============================================================================
# Kullanım: .\setup.ps1 [komut]
# Komutlar: setup, start, stop, restart, logs, migrate, seed, dev, clean, help
# =============================================================================

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

# Renkli çıktı fonksiyonları
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "📌 $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Step { param($msg) Write-Host "▶️  $msg" -ForegroundColor Blue }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }

# Docker kurulum kontrolü
function Test-Docker {
    try {
        $null = & docker version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Docker command failed"
        }
        return $true
    }
    catch {
        return $false
    }
}

# Docker Desktop çalışıyor mu kontrolü
function Test-DockerRunning {
    try {
        $info = & docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        return $true
    }
    catch {
        return $false
    }
}

# Ön gereksinim kontrolü
function Test-Prerequisites {
    Write-Step "Ongereksinimler kontrol ediliyor..."
    
    # Docker kurulu mu?
    if (-not (Test-Docker)) {
        Write-Error "Docker kurulu degil!"
        Write-Host ""
        Write-Host "Docker Desktop'i indirin: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    Write-Success "Docker kurulu."
    
    # Docker çalışıyor mu?
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker Desktop calismiyorl!"
        Write-Host ""
        Write-Host "Lutfen Docker Desktop'i baslatin ve tekrar deneyin." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    Write-Success "Docker Desktop calisiyor."
}

# .env dosyası kontrolü
function Check-Env {
    $envPath = Join-Path $ProjectRoot ".env"
    $examplePath = Join-Path $ProjectRoot "infra\env.example"
    
    if (-not (Test-Path $envPath)) {
        Write-Step ".env dosyasi olusturuluyor..."
        Copy-Item $examplePath $envPath
        Write-Success ".env dosyasi olusturuldu."
    } else {
        Write-Success ".env dosyasi mevcut."
    }
}

# Docker Compose wrapper
function Invoke-DockerCompose {
    param([string[]]$Arguments)
    Push-Location (Join-Path $ProjectRoot "infra")
    try {
        $envFile = Join-Path $ProjectRoot ".env"
        & docker compose --env-file $envFile @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose komutu basarisiz oldu."
        }
    } finally {
        Pop-Location
    }
}

# Container sağlık kontrolü
function Wait-ForHealthy {
    param(
        [string]$Service,
        [int]$MaxWaitSeconds = 60
    )
    
    Write-Step "$Service servisi hazir olana kadar bekleniyor..."
    
    $waited = 0
    $interval = 2
    
    while ($waited -lt $MaxWaitSeconds) {
        try {
            Push-Location (Join-Path $ProjectRoot "infra")
            $envFile = Join-Path $ProjectRoot ".env"
            $status = & docker compose --env-file $envFile ps --format json 2>&1 | ConvertFrom-Json
            Pop-Location
            
            $serviceInfo = $status | Where-Object { $_.Service -eq $Service }
            if ($serviceInfo -and $serviceInfo.Health -eq "healthy") {
                Write-Success "$Service servisi hazir."
                return $true
            }
        }
        catch {
            # JSON parse hatası olabilir, devam et
        }
        
        Start-Sleep -Seconds $interval
        $waited += $interval
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Warning "$Service servisi $MaxWaitSeconds saniye icinde hazir olmadi, devam ediliyor..."
    return $false
}

# Veritabanı hazır mı kontrolü
function Wait-ForDatabase {
    Write-Step "Veritabani baglantisi kontrol ediliyor..."
    
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        try {
            Push-Location (Join-Path $ProjectRoot "infra")
            $envFile = Join-Path $ProjectRoot ".env"
            $result = & docker compose --env-file $envFile exec -T db pg_isready -U gantt_user -d gantt_app 2>&1
            Pop-Location
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Veritabani hazir."
                return $true
            }
        }
        catch {
            # Hata olabilir, devam et
        }
        
        $attempt++
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
    
    Write-Host ""
    Write-Warning "Veritabani baglantisi kurulamadi, yine de devam ediliyor..."
    return $false
}

# Komut işleyicileri
function Invoke-Setup {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         Gantt Chart - Sifirdan Kurulum Basliyor                   ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    # Ön gereksinim kontrolü
    Test-Prerequisites
    
    Check-Env
    
    Write-Step "Docker image'lari build ediliyor..."
    Invoke-DockerCompose @("build")
    Write-Success "Build tamamlandi."
    
    Write-Step "Servisler baslatiliyor..."
    Invoke-DockerCompose @("up", "-d")
    Write-Success "Servisler baslatildi."
    
    # Veritabanı hazır olana kadar bekle
    Wait-ForDatabase
    
    # Ekstra bekleme - container'ların tam başlaması için
    Start-Sleep -Seconds 3
    
    Write-Step "Migration'lar calistiriliyor..."
    Invoke-DockerCompose @("exec", "-T", "api", "alembic", "upgrade", "head")
    Write-Success "Migration'lar tamamlandi."
    
    Write-Step "Ornek veriler yukleniyor..."
    Invoke-DockerCompose @("exec", "-T", "api", "python", "seed.py")
    Write-Success "Seed tamamlandi."
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Success "KURULUM TAMAMLANDI!"
    Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Info "Uygulama adresleri:"
    Write-Host "   Frontend: http://localhost" -ForegroundColor White
    Write-Host "   Backend:  http://localhost:5000" -ForegroundColor White
    Write-Host ""
    Write-Info "Demo hesaplari:"
    Write-Host "   Admin:  admin@gantt.local / admin123" -ForegroundColor White
    Write-Host "   Editor: editor@gantt.local / editor123" -ForegroundColor White
    Write-Host "   Viewer: viewer@gantt.local / viewer123" -ForegroundColor White
    Write-Host ""
    
    # Tarayıcıda aç (opsiyonel)
    $openBrowser = Read-Host "Tarayicida acilsin mi? (E/h)"
    if ($openBrowser -ne "h" -and $openBrowser -ne "H") {
        Start-Process "http://localhost"
    }
}

function Invoke-Start {
    Test-Prerequisites
    Check-Env
    Write-Step "Servisler baslatiliyor..."
    Invoke-DockerCompose @("up", "-d")
    Write-Success "Servisler baslatildi."
    Write-Info "Frontend: http://localhost | Backend: http://localhost:5000"
}

function Invoke-Stop {
    Write-Step "Servisler durduruluyor..."
    Invoke-DockerCompose @("down")
    Write-Success "Servisler durduruldu."
}

function Invoke-Restart {
    Invoke-Stop
    Invoke-Start
}

function Invoke-Logs {
    Invoke-DockerCompose @("logs", "-f")
}

function Invoke-LogsApi {
    Invoke-DockerCompose @("logs", "-f", "api")
}

function Invoke-LogsWeb {
    Invoke-DockerCompose @("logs", "-f", "web")
}

function Invoke-LogsDb {
    Invoke-DockerCompose @("logs", "-f", "db")
}

function Invoke-Migrate {
    Write-Step "Migration'lar calistiriliyor..."
    Invoke-DockerCompose @("exec", "-T", "api", "alembic", "upgrade", "head")
    Write-Success "Migration'lar tamamlandi."
}

function Invoke-Seed {
    Write-Step "Ornek veriler yukleniyor..."
    Invoke-DockerCompose @("exec", "-T", "api", "python", "seed.py")
    Write-Success "Seed tamamlandi."
}

function Invoke-Dev {
    Test-Prerequisites
    Check-Env
    Write-Step "Gelistirme ortami baslatiliyor (sadece DB)..."
    Push-Location (Join-Path $ProjectRoot "infra")
    try {
        $envFile = Join-Path $ProjectRoot ".env"
        & docker compose --env-file $envFile -f docker-compose.dev.yml up -d
    } finally {
        Pop-Location
    }
    Write-Success "PostgreSQL calisiyor: localhost:5432"
    Write-Host ""
    Write-Info "Sonraki adimlar:"
    Write-Host "   Backend:  cd backend; pip install -r requirements.txt; flask run --debug" -ForegroundColor White
    Write-Host "   Frontend: cd frontend; npm install; npm run dev" -ForegroundColor White
}

function Invoke-DevStop {
    Write-Step "Gelistirme ortami durduruluyor..."
    Push-Location (Join-Path $ProjectRoot "infra")
    try {
        $envFile = Join-Path $ProjectRoot ".env"
        & docker compose --env-file $envFile -f docker-compose.dev.yml down
    } finally {
        Pop-Location
    }
    Write-Success "Gelistirme ortami durduruldu."
}

function Invoke-Clean {
    Write-Step "Temizlik yapiliyor..."
    Invoke-DockerCompose @("down", "-v", "--remove-orphans")
    Write-Success "Container ve volume'lar temizlendi."
}

function Invoke-CleanAll {
    Invoke-Clean
    Write-Step "Docker image'lari siliniyor..."
    docker rmi infra-api infra-web 2>$null
    Write-Success "Tum kaynaklar temizlendi."
}

function Invoke-Test {
    Write-Step "Backend testleri calistiriliyor..."
    Invoke-DockerCompose @("exec", "-T", "api", "pytest", "-v")
}

function Invoke-Status {
    Write-Step "Servis durumlari:"
    Invoke-DockerCompose @("ps")
}

function Show-Help {
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║         Gantt Chart - Faaliyet Planlama Uygulamasi                ║" -ForegroundColor Magenta
    Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "KULLANIM:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 [komut]"
    Write-Host ""
    Write-Host "HIZLI BASLANGIC:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 setup      → Sifirdan tam kurulum (onerilen)" -ForegroundColor Green
    Write-Host ""
    Write-Host "DOCKER KOMUTLARI:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 start      → Servisleri baslat"
    Write-Host "   .\setup.ps1 stop       → Servisleri durdur"
    Write-Host "   .\setup.ps1 restart    → Servisleri yeniden baslat"
    Write-Host "   .\setup.ps1 status     → Servis durumlarini goster"
    Write-Host "   .\setup.ps1 logs       → Tum loglari goster"
    Write-Host "   .\setup.ps1 logs-api   → API loglarini goster"
    Write-Host "   .\setup.ps1 logs-web   → Web loglarini goster"
    Write-Host "   .\setup.ps1 logs-db    → DB loglarini goster"
    Write-Host ""
    Write-Host "VERITABANI:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 migrate    → Migration'lari calistir"
    Write-Host "   .\setup.ps1 seed       → Ornek veri yukle"
    Write-Host ""
    Write-Host "GELISTIRME:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 dev        → Dev ortami baslat (sadece DB)"
    Write-Host "   .\setup.ps1 dev-stop   → Dev ortamini durdur"
    Write-Host ""
    Write-Host "TEST:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 test       → Backend testlerini calistir"
    Write-Host ""
    Write-Host "TEMIZLIK:" -ForegroundColor Yellow
    Write-Host "   .\setup.ps1 clean      → Container ve volume'lari sil"
    Write-Host "   .\setup.ps1 clean-all  → Her seyi sil (image'lar dahil)"
    Write-Host ""
    Write-Host "ONGEREKSINIMLER:" -ForegroundColor Yellow
    Write-Host "   - Docker Desktop (https://www.docker.com/products/docker-desktop)"
    Write-Host ""
}

# Ana komut yönlendirici
switch ($Command.ToLower()) {
    "setup"     { Invoke-Setup }
    "start"     { Invoke-Start }
    "stop"      { Invoke-Stop }
    "restart"   { Invoke-Restart }
    "status"    { Invoke-Status }
    "logs"      { Invoke-Logs }
    "logs-api"  { Invoke-LogsApi }
    "logs-web"  { Invoke-LogsWeb }
    "logs-db"   { Invoke-LogsDb }
    "migrate"   { Invoke-Migrate }
    "seed"      { Invoke-Seed }
    "dev"       { Invoke-Dev }
    "dev-stop"  { Invoke-DevStop }
    "clean"     { Invoke-Clean }
    "clean-all" { Invoke-CleanAll }
    "test"      { Invoke-Test }
    "help"      { Show-Help }
    default     { 
        Write-Warning "Bilinmeyen komut: $Command"
        Show-Help 
    }
}
