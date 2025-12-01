#!/bin/bash
# =============================================================================
# Gantt Chart Application - Unix/Linux/Mac Setup Script
# =============================================================================
# Kullanım: ./setup.sh [komut]
# Komutlar: setup, start, stop, restart, logs, migrate, seed, dev, clean, help
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Yardımcı fonksiyonlar
success() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${CYAN}📌 $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
step() { echo -e "${BLUE}▶️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# Docker kurulum kontrolü
check_docker() {
    step "Ön gereksinimler kontrol ediliyor..."
    
    # Docker kurulu mu?
    if ! command -v docker &> /dev/null; then
        error "Docker kurulu değil!"
        echo ""
        echo -e "${YELLOW}Docker'ı kurmak için:${NC}"
        echo "  macOS: https://docs.docker.com/desktop/mac/install/"
        echo "  Linux: https://docs.docker.com/engine/install/"
        echo ""
        exit 1
    fi
    success "Docker kurulu."
    
    # Docker çalışıyor mu?
    if ! docker info &> /dev/null; then
        error "Docker servisi çalışmıyor!"
        echo ""
        echo -e "${YELLOW}Docker'ı başlatın:${NC}"
        echo "  macOS: Docker Desktop uygulamasını açın"
        echo "  Linux: sudo systemctl start docker"
        echo ""
        exit 1
    fi
    success "Docker çalışıyor."
}

# .env dosyası kontrolü
check_env() {
    if [ ! -f ".env" ]; then
        step ".env dosyası oluşturuluyor..."
        cp infra/env.example .env
        success ".env dosyası oluşturuldu."
    else
        success ".env dosyası mevcut."
    fi
}

# Veritabanı hazır mı kontrolü
wait_for_db() {
    step "Veritabanı bağlantısı kontrol ediliyor..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if cd infra && docker compose --env-file ../.env exec -T db pg_isready -U gantt_user -d gantt_app &> /dev/null; then
            cd ..
            echo ""
            success "Veritabanı hazır."
            return 0
        fi
        cd ..
        
        attempt=$((attempt + 1))
        printf "."
        sleep 2
    done
    
    echo ""
    warn "Veritabanı bağlantısı zaman aşımına uğradı, devam ediliyor..."
    return 0
}

# Komut işleyicileri
do_setup() {
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║         Gantt Chart - Sıfırdan Kurulum Başlıyor                   ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    check_docker
    check_env
    
    step "Docker image'ları build ediliyor..."
    cd infra && docker compose --env-file ../.env build && cd ..
    success "Build tamamlandı."
    
    step "Servisler başlatılıyor..."
    cd infra && docker compose --env-file ../.env up -d && cd ..
    success "Servisler başlatıldı."
    
    wait_for_db
    
    # Ekstra bekleme
    sleep 3
    
    step "Migration'lar çalıştırılıyor..."
    cd infra && docker compose --env-file ../.env exec -T api alembic upgrade head && cd ..
    success "Migration'lar tamamlandı."
    
    step "Örnek veriler yükleniyor..."
    cd infra && docker compose --env-file ../.env exec -T api python seed.py && cd ..
    success "Seed tamamlandı."
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    success "KURULUM TAMAMLANDI!"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    info "Uygulama adresleri:"
    echo "   Frontend: http://localhost"
    echo "   Backend:  http://localhost:5000"
    echo ""
    info "Demo hesapları:"
    echo "   Admin:  admin@gantt.local / admin123"
    echo "   Editor: editor@gantt.local / editor123"
    echo "   Viewer: viewer@gantt.local / viewer123"
    echo ""
    
    # Tarayıcıda aç (opsiyonel)
    read -p "Tarayıcıda açılsın mı? (E/h): " open_browser
    if [[ ! "$open_browser" =~ ^[hH]$ ]]; then
        if command -v open &> /dev/null; then
            open http://localhost
        elif command -v xdg-open &> /dev/null; then
            xdg-open http://localhost
        fi
    fi
}

do_start() {
    check_docker
    check_env
    step "Servisler başlatılıyor..."
    cd infra && docker compose --env-file ../.env up -d && cd ..
    success "Servisler başlatıldı."
    info "Frontend: http://localhost | Backend: http://localhost:5000"
}

do_stop() {
    step "Servisler durduruluyor..."
    cd infra && docker compose --env-file ../.env down && cd ..
    success "Servisler durduruldu."
}

do_restart() {
    do_stop
    do_start
}

do_status() {
    step "Servis durumları:"
    cd infra && docker compose --env-file ../.env ps && cd ..
}

do_logs() {
    cd infra && docker compose --env-file ../.env logs -f && cd ..
}

do_logs_api() {
    cd infra && docker compose --env-file ../.env logs -f api && cd ..
}

do_logs_web() {
    cd infra && docker compose --env-file ../.env logs -f web && cd ..
}

do_logs_db() {
    cd infra && docker compose --env-file ../.env logs -f db && cd ..
}

do_migrate() {
    step "Migration'lar çalıştırılıyor..."
    cd infra && docker compose --env-file ../.env exec -T api alembic upgrade head && cd ..
    success "Migration'lar tamamlandı."
}

do_seed() {
    step "Örnek veriler yükleniyor..."
    cd infra && docker compose --env-file ../.env exec -T api python seed.py && cd ..
    success "Seed tamamlandı."
}

do_dev() {
    check_docker
    check_env
    step "Geliştirme ortamı başlatılıyor (sadece DB)..."
    cd infra && docker compose --env-file ../.env -f docker-compose.dev.yml up -d && cd ..
    success "PostgreSQL çalışıyor: localhost:5432"
    echo ""
    info "Sonraki adımlar:"
    echo "   Backend:  cd backend && pip install -r requirements.txt && flask run --debug"
    echo "   Frontend: cd frontend && npm install && npm run dev"
}

do_dev_stop() {
    step "Geliştirme ortamı durduruluyor..."
    cd infra && docker compose --env-file ../.env -f docker-compose.dev.yml down && cd ..
    success "Geliştirme ortamı durduruldu."
}

do_clean() {
    step "Temizlik yapılıyor..."
    cd infra && docker compose --env-file ../.env down -v --remove-orphans && cd ..
    success "Container ve volume'lar temizlendi."
}

do_clean_all() {
    do_clean
    step "Docker image'ları siliniyor..."
    docker rmi infra-api infra-web 2>/dev/null || true
    success "Tüm kaynaklar temizlendi."
}

do_test() {
    step "Backend testleri çalıştırılıyor..."
    cd infra && docker compose --env-file ../.env exec -T api pytest -v && cd ..
}

show_help() {
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║         Gantt Chart - Faaliyet Planlama Uygulaması                ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}KULLANIM:${NC}"
    echo "   ./setup.sh [komut]"
    echo ""
    echo -e "${YELLOW}HIZLI BAŞLANGIÇ:${NC}"
    echo -e "   ${GREEN}./setup.sh setup${NC}      → Sıfırdan tam kurulum (önerilen)"
    echo ""
    echo -e "${YELLOW}DOCKER KOMUTLARI:${NC}"
    echo "   ./setup.sh start      → Servisleri başlat"
    echo "   ./setup.sh stop       → Servisleri durdur"
    echo "   ./setup.sh restart    → Servisleri yeniden başlat"
    echo "   ./setup.sh status     → Servis durumlarını göster"
    echo "   ./setup.sh logs       → Tüm logları göster"
    echo "   ./setup.sh logs-api   → API loglarını göster"
    echo "   ./setup.sh logs-web   → Web loglarını göster"
    echo "   ./setup.sh logs-db    → DB loglarını göster"
    echo ""
    echo -e "${YELLOW}VERİTABANI:${NC}"
    echo "   ./setup.sh migrate    → Migration'ları çalıştır"
    echo "   ./setup.sh seed       → Örnek veri yükle"
    echo ""
    echo -e "${YELLOW}GELİŞTİRME:${NC}"
    echo "   ./setup.sh dev        → Dev ortamı başlat (sadece DB)"
    echo "   ./setup.sh dev-stop   → Dev ortamını durdur"
    echo ""
    echo -e "${YELLOW}TEST:${NC}"
    echo "   ./setup.sh test       → Backend testlerini çalıştır"
    echo ""
    echo -e "${YELLOW}TEMİZLİK:${NC}"
    echo "   ./setup.sh clean      → Container ve volume'ları sil"
    echo "   ./setup.sh clean-all  → Her şeyi sil (image'lar dahil)"
    echo ""
    echo -e "${YELLOW}ÖN GEREKSİNİMLER:${NC}"
    echo "   - Docker (https://docs.docker.com/get-docker/)"
    echo ""
}

# Ana komut yönlendirici
case "${1:-help}" in
    setup)     do_setup ;;
    start)     do_start ;;
    stop)      do_stop ;;
    restart)   do_restart ;;
    status)    do_status ;;
    logs)      do_logs ;;
    logs-api)  do_logs_api ;;
    logs-web)  do_logs_web ;;
    logs-db)   do_logs_db ;;
    migrate)   do_migrate ;;
    seed)      do_seed ;;
    dev)       do_dev ;;
    dev-stop)  do_dev_stop ;;
    clean)     do_clean ;;
    clean-all) do_clean_all ;;
    test)      do_test ;;
    help)      show_help ;;
    *)
        warn "Bilinmeyen komut: $1"
        show_help
        exit 1
        ;;
esac
