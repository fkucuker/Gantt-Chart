# =============================================================================
# Gantt Chart Application - Makefile
# =============================================================================
# Tek komutla kurulum ve yönetim için kullanın.
# Windows kullanıcıları: setup.ps1 veya setup.bat kullanabilirsiniz.
# =============================================================================

.PHONY: all setup install start stop restart logs seed clean help dev prod test check-docker

# Default target
all: help

# -----------------------------------------------------------------------------
# ÖN GEREKSİNİM KONTROLLERI
# -----------------------------------------------------------------------------

## Docker kurulu ve çalışıyor mu kontrol et
check-docker:
	@echo "🔍 Docker kontrol ediliyor..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker kurulu değil! https://docs.docker.com/get-docker/"; exit 1; }
	@echo "✅ Docker kurulu."
	@docker info >/dev/null 2>&1 || { echo "❌ Docker çalışmıyor! Docker Desktop'ı başlatın."; exit 1; }
	@echo "✅ Docker çalışıyor."

# -----------------------------------------------------------------------------
# SETUP - Sıfırdan kurulum
# -----------------------------------------------------------------------------

## Tam kurulum (env + docker build + start + migrate + seed)
setup: check-docker env-check
	@echo "🚀 Gantt Chart uygulaması kuruluyor..."
	@$(MAKE) install
	@$(MAKE) start
	@echo "⏳ Veritabanı hazır olana kadar bekleniyor..."
	@$(MAKE) wait-for-db
	@sleep 3
	@$(MAKE) migrate
	@$(MAKE) seed
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo "✅ KURULUM TAMAMLANDI!"
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📌 Uygulama adresleri:"
	@echo "   Frontend: http://localhost"
	@echo "   Backend:  http://localhost:5000"
	@echo ""
	@echo "🔐 Demo hesapları:"
	@echo "   Admin:  admin@gantt.local / admin123"
	@echo "   Editor: editor@gantt.local / editor123"
	@echo "   Viewer: viewer@gantt.local / viewer123"

## .env dosyası kontrolü ve oluşturma
env-check:
	@if [ ! -f .env ]; then \
		echo "📝 .env dosyası oluşturuluyor..."; \
		cp infra/env.example .env; \
		echo "✅ .env dosyası oluşturuldu."; \
	else \
		echo "✅ .env dosyası mevcut."; \
	fi

## Docker image'larını build et
install:
	@echo "🔨 Docker image'ları build ediliyor..."
	@cd infra && docker compose --env-file ../.env build
	@echo "✅ Build tamamlandı."

## Veritabanı hazır olana kadar bekle
wait-for-db:
	@echo "⏳ Veritabanı bağlantısı kontrol ediliyor..."
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do \
		cd infra && docker compose --env-file ../.env exec -T db pg_isready -U gantt_user -d gantt_app >/dev/null 2>&1 && echo "✅ Veritabanı hazır." && exit 0; \
		printf "."; \
		sleep 2; \
	done; \
	echo ""; \
	echo "⚠️  Veritabanı zaman aşımı, devam ediliyor..."

# -----------------------------------------------------------------------------
# DOCKER KOMUTLARI
# -----------------------------------------------------------------------------

## Tüm servisleri başlat
start: check-docker
	@echo "▶️  Servisler başlatılıyor..."
	@cd infra && docker compose --env-file ../.env up -d
	@echo "✅ Servisler başlatıldı."

## Tüm servisleri durdur
stop:
	@echo "⏹️  Servisler durduruluyor..."
	@cd infra && docker compose --env-file ../.env down
	@echo "✅ Servisler durduruldu."

## Servisleri yeniden başlat
restart: stop start

## Servis durumlarını göster
status:
	@echo "📊 Servis durumları:"
	@cd infra && docker compose --env-file ../.env ps

## Container loglarını göster
logs:
	@cd infra && docker compose --env-file ../.env logs -f

## API loglarını göster
logs-api:
	@cd infra && docker compose --env-file ../.env logs -f api

## Web loglarını göster
logs-web:
	@cd infra && docker compose --env-file ../.env logs -f web

## DB loglarını göster
logs-db:
	@cd infra && docker compose --env-file ../.env logs -f db

# -----------------------------------------------------------------------------
# VERİTABANI KOMUTLARI
# -----------------------------------------------------------------------------

## Veritabanı migration'larını çalıştır
migrate:
	@echo "📦 Migration'lar çalıştırılıyor..."
	@cd infra && docker compose --env-file ../.env exec -T api alembic upgrade head
	@echo "✅ Migration'lar tamamlandı."

## Veritabanını seed et (örnek veri)
seed:
	@echo "🌱 Örnek veriler yükleniyor..."
	@cd infra && docker compose --env-file ../.env exec -T api python seed.py
	@echo "✅ Seed tamamlandı."

## Yeni migration oluştur
migration-create:
	@read -p "Migration adı: " name; \
	cd infra && docker compose --env-file ../.env exec api alembic revision --autogenerate -m "$$name"

# -----------------------------------------------------------------------------
# GELİŞTİRME ORTAMI
# -----------------------------------------------------------------------------

## Geliştirme ortamını başlat (sadece DB)
dev: check-docker env-check
	@echo "🔧 Geliştirme ortamı başlatılıyor (sadece DB)..."
	@cd infra && docker compose --env-file ../.env -f docker-compose.dev.yml up -d
	@echo ""
	@echo "✅ PostgreSQL çalışıyor: localhost:5432"
	@echo ""
	@echo "📌 Sonraki adımlar:"
	@echo "   Backend:  cd backend && pip install -r requirements.txt && flask run --debug"
	@echo "   Frontend: cd frontend && npm install && npm run dev"

## Geliştirme ortamını durdur
dev-stop:
	@cd infra && docker compose --env-file ../.env -f docker-compose.dev.yml down

# -----------------------------------------------------------------------------
# PRODUCTION
# -----------------------------------------------------------------------------

## Production build ve başlat
prod: check-docker env-check
	@echo "🏭 Production ortamı başlatılıyor..."
	@cd infra && docker compose --env-file ../.env -f docker-compose.yml up -d --build
	@echo "✅ Production ortamı çalışıyor."

# -----------------------------------------------------------------------------
# TEST
# -----------------------------------------------------------------------------

## Backend testlerini çalıştır
test-backend:
	@echo "🧪 Backend testleri çalıştırılıyor..."
	@cd infra && docker compose --env-file ../.env exec -T api pytest -v

## Frontend testlerini çalıştır
test-frontend:
	@echo "🧪 Frontend testleri çalıştırılıyor..."
	@cd frontend && npm run test

## Tüm testleri çalıştır
test: test-backend test-frontend

# -----------------------------------------------------------------------------
# TEMİZLİK
# -----------------------------------------------------------------------------

## Container ve volume'ları temizle
clean:
	@echo "🧹 Temizlik yapılıyor..."
	@cd infra && docker compose --env-file ../.env down -v --remove-orphans
	@echo "✅ Temizlik tamamlandı."

## Her şeyi temizle (image'lar dahil)
clean-all: clean
	@echo "🗑️  Docker image'ları siliniyor..."
	@docker rmi infra-api infra-web 2>/dev/null || true
	@echo "✅ Tüm kaynaklar temizlendi."

# -----------------------------------------------------------------------------
# YARDIM
# -----------------------------------------------------------------------------

## Bu yardım mesajını göster
help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════════╗"
	@echo "║         Gantt Chart - Faaliyet Planlama Uygulaması                ║"
	@echo "╚═══════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📌 HIZLI BAŞLANGIÇ:"
	@echo "   make setup          → Sıfırdan tam kurulum (önerilen)"
	@echo ""
	@echo "🐳 DOCKER KOMUTLARI:"
	@echo "   make start          → Servisleri başlat"
	@echo "   make stop           → Servisleri durdur"
	@echo "   make restart        → Servisleri yeniden başlat"
	@echo "   make status         → Servis durumlarını göster"
	@echo "   make logs           → Tüm logları göster"
	@echo "   make logs-api       → API logları"
	@echo "   make logs-web       → Web logları"
	@echo "   make logs-db        → DB logları"
	@echo ""
	@echo "📦 VERİTABANI:"
	@echo "   make migrate        → Migration'ları çalıştır"
	@echo "   make seed           → Örnek veri yükle"
	@echo ""
	@echo "🔧 GELİŞTİRME:"
	@echo "   make dev            → Dev ortamı başlat (sadece DB)"
	@echo "   make dev-stop       → Dev ortamını durdur"
	@echo ""
	@echo "🧪 TEST:"
	@echo "   make test           → Tüm testleri çalıştır"
	@echo "   make test-backend   → Backend testleri"
	@echo "   make test-frontend  → Frontend testleri"
	@echo ""
	@echo "🧹 TEMİZLİK:"
	@echo "   make clean          → Container ve volume'ları sil"
	@echo "   make clean-all      → Her şeyi sil (image'lar dahil)"
	@echo ""
	@echo "ÖN GEREKSİNİMLER:"
	@echo "   - Docker (https://docs.docker.com/get-docker/)"
	@echo ""
