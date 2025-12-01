# Gantt Chart - Faaliyet Planlama Uygulaması

Modern, kullanıcı dostu Gantt Chart tabanlı proje ve faaliyet planlama uygulaması.

## 🚀 Hızlı Başlangıç (Tek Komutla Kurulum)

### Ön Gereksinimler

- **Docker Desktop** kurulu ve çalışıyor olmalı
- İndirme: https://www.docker.com/products/docker-desktop

### Windows - En Kolay Yol (Çift Tıkla)

📁 Proje klasöründeki **`INSTALL.cmd`** dosyasına çift tıklayın.

Veya terminal kullanarak:

```powershell
# PowerShell
.\setup.ps1 setup

# CMD
setup.bat setup
```

### Linux / macOS

```bash
chmod +x setup.sh
./setup.sh setup
```

### Make (Tüm Platformlar)

```bash
make setup
```

---

## ✅ Kurulum Ne Yapar?

Tek komut ile otomatik olarak:

1. ✅ Docker kurulum kontrolü yapar
2. ✅ `.env` dosyasını oluşturur
3. ✅ Docker image'larını build eder
4. ✅ Tüm servisleri başlatır (DB, API, Web)
5. ✅ Veritabanı migration'larını çalıştırır
6. ✅ Örnek verileri yükler

**Kurulum tamamlandıktan sonra:**

| Servis | Adres |
|--------|-------|
| 🌐 Frontend | http://localhost |
| 🔌 Backend API | http://localhost:5000 |
| 📊 Health Check | http://localhost:5000/api/health |

---

## 🔐 Demo Hesapları

| Rol | Email | Şifre |
|-----|-------|-------|
| Admin | admin@gantt.local | admin123 |
| Editor | editor@gantt.local | editor123 |
| Viewer | viewer@gantt.local | viewer123 |

---

## 📋 Özellikler

### FAZ-1 (MVP) ✅

- **Activity / Topic / SubTask** hiyerarşik yapısı
- **Gantt Chart** görselleştirme
- Kullanıcı rolleri: Admin, Editor, Viewer
- SubTask durumları: PLANNED, IN_PROGRESS, COMPLETED, OVERDUE
- Tooltip ile detay görüntüleme
- **Dark / Light mod** desteği
- Admin One tarzı modern dashboard arayüzü

### FAZ-2 (Etkileşim & UX) ✅

- **Drag & Drop** ile tarih güncelleme (sadece Admin/Editor)
- **Bildirim sistemi** - gerçek zamanlı bildirimler
- **Rol bazlı UI kontrolü** - yetkisiz işlemler devre dışı
- Notification API ve frontend entegrasyonu
- SubTask PATCH endpoint'i ile tarih güncelleme

---

## 🛠️ Kullanılabilir Komutlar

### Temel Komutlar

| Komut | Açıklama |
|-------|----------|
| `setup` | 🚀 Sıfırdan tam kurulum (önerilen) |
| `start` | Servisleri başlat |
| `stop` | Servisleri durdur |
| `restart` | Servisleri yeniden başlat |
| `status` | Servis durumlarını göster |

### Log Komutları

| Komut | Açıklama |
|-------|----------|
| `logs` | Tüm logları göster |
| `logs-api` | API loglarını göster |
| `logs-web` | Web loglarını göster |
| `logs-db` | DB loglarını göster |

### Veritabanı Komutları

| Komut | Açıklama |
|-------|----------|
| `migrate` | DB migration'ları çalıştır |
| `seed` | Örnek veri yükle |

### Geliştirme Komutları

| Komut | Açıklama |
|-------|----------|
| `dev` | Geliştirme ortamı (sadece DB) |
| `dev-stop` | Geliştirme ortamını durdur |
| `test` | Testleri çalıştır |

### Temizlik Komutları

| Komut | Açıklama |
|-------|----------|
| `clean` | Container ve volume'ları sil |
| `clean-all` | Her şeyi sil (image'lar dahil) |

**Kullanım:**

```bash
# PowerShell
.\setup.ps1 <komut>

# CMD
setup.bat <komut>

# Bash
./setup.sh <komut>

# Make
make <komut>
```

---

## 📦 Kurulum Seçenekleri

### Seçenek 1: Tek Komutla Tam Kurulum (Önerilen)

```bash
# Windows (Çift tıkla)
INSTALL.cmd

# Windows PowerShell
.\setup.ps1 setup

# Windows CMD
setup.bat setup

# Linux/macOS
./setup.sh setup

# Make
make setup
```

### Seçenek 2: Manuel Docker Kurulumu

```bash
# 1. .env dosyasını oluştur
cp infra/env.example .env   # Linux/Mac
copy infra\env.example .env  # Windows

# 2. Docker Compose ile başlat
cd infra
docker compose --env-file ../.env up -d --build

# 3. Migration ve seed
docker compose --env-file ../.env exec api alembic upgrade head
docker compose --env-file ../.env exec api python seed.py
```

### Seçenek 3: Geliştirme Ortamı

Sadece veritabanını Docker'da çalıştırıp, backend ve frontend'i local'de geliştirmek için:

```bash
# 1. Sadece veritabanını başlat
.\setup.ps1 dev        # Windows
./setup.sh dev         # Linux/Mac
make dev               # Make

# 2. Backend'i başlat (yeni terminal)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://gantt_user:gantt_secret_2024@localhost:5432/gantt_app
alembic upgrade head
python seed.py
flask run --debug

# 3. Frontend'i başlat (yeni terminal)
cd frontend
npm install
npm run dev
```

---

## 🛠️ Teknoloji Stack

### Backend

| Teknoloji | Versiyon |
|-----------|----------|
| Python | 3.13 |
| Flask | 3.1.2 |
| SQLAlchemy | 2.0.44 |
| Alembic | 1.17.2 |
| PostgreSQL | 16.11 |
| psycopg2 | 2.9.11 |
| Gunicorn | 23.0.0 |

### Frontend

| Teknoloji | Versiyon |
|-----------|----------|
| Vue.js | 3.5.x |
| TypeScript | 5.6.x |
| Vite | 6.x |
| Pinia | 2.3.x |
| Vue Router | 4.5.x |
| TailwindCSS | 3.4.x |
| Axios | 1.7.x |

### Infrastructure

| Teknoloji | Versiyon |
|-----------|----------|
| Docker | Latest |
| nginx | Alpine |
| Node.js | 24 LTS |

---

## 📡 API Endpoints

### Auth

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/api/auth/login` | Giriş yap |
| GET | `/api/auth/me` | Mevcut kullanıcı |
| POST | `/api/auth/logout` | Çıkış yap |

### Activities

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/activities` | Tüm faaliyetler |
| POST | `/api/activities` | Yeni faaliyet (admin/editor) |
| GET | `/api/activities/:id` | Faaliyet detayı |
| PUT | `/api/activities/:id` | Güncelle (admin/editor) |
| DELETE | `/api/activities/:id` | Sil (admin) |

### Topics

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/activities/:id/topics` | Konular |
| POST | `/api/activities/:id/topics` | Yeni konu |
| PUT | `/api/topics/:id` | Güncelle |
| DELETE | `/api/topics/:id` | Sil |

### SubTasks

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/topics/:id/subtasks` | Alt görevler |
| POST | `/api/topics/:id/subtasks` | Yeni alt görev |
| PUT | `/api/subtasks/:id` | Güncelle |
| PATCH | `/api/subtasks/:id` | Kısmi güncelle |
| DELETE | `/api/subtasks/:id` | Sil |

### Gantt

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/activities/:id/gantt` | Gantt verisi |

### Notifications

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/notifications` | Kullanıcı bildirimleri |
| PATCH | `/api/notifications/:id` | Okundu işaretle |

### Health Check

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/health` | API durumu |

---

## 👥 Roller ve Yetkiler

| Yetki | Admin | Editor | Viewer |
|-------|-------|--------|--------|
| Faaliyetleri görüntüle | ✅ | ✅ | ✅ |
| Faaliyet oluştur | ✅ | ✅ | ❌ |
| Faaliyet güncelle | ✅ | ✅* | ❌ |
| Faaliyet sil | ✅ | ❌ | ❌ |
| Konu/Alt görev CRUD | ✅ | ✅* | ❌ |

*Editor sadece kendi faaliyetlerini düzenleyebilir.

---

## 🎨 Tema Kullanımı

Uygulama dark ve light mod destekler:

- Tema tercihi `localStorage`'da saklanır
- Sağ üst köşedeki ikon ile değiştirilebilir
- Sistem teması otomatik algılanır

### Tailwind CSS Class Stratejisi

```css
/* Light mode varsayılan */
bg-slate-50 text-slate-800

/* Dark mode */
dark:bg-slate-900 dark:text-slate-100
```

---

## 🧪 Test

### Backend Testleri

```bash
# Docker içinde
.\setup.ps1 test     # Windows
./setup.sh test      # Linux/Mac
make test-backend    # Make

# Local'de
cd backend
pytest -v
```

### Frontend Testleri

```bash
cd frontend
npm run test
```

---

## 📁 Proje Yapısı

```
/
├── backend/
│   ├── app/
│   │   ├── __init__.py      # Flask app factory
│   │   ├── config.py        # Konfigürasyon
│   │   ├── db.py            # Veritabanı bağlantısı
│   │   ├── models.py        # SQLAlchemy modelleri
│   │   ├── auth/            # Kimlik doğrulama
│   │   ├── routes/          # API endpoint'leri
│   │   └── services/        # İş mantığı servisleri
│   ├── migrations/          # Alembic migration'ları
│   ├── tests/               # Pytest testleri
│   ├── requirements.txt     # Python bağımlılıkları
│   ├── Dockerfile
│   ├── seed.py              # Örnek veri script'i
│   └── wsgi.py              # WSGI entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── gantt/       # Gantt chart bileşenleri
│   │   │   └── layout/      # Layout bileşenleri
│   │   ├── pages/           # Sayfa bileşenleri
│   │   ├── router/          # Vue Router
│   │   ├── services/        # API servisleri
│   │   ├── store/           # Pinia store'ları
│   │   └── types/           # TypeScript tipleri
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── infra/
│   ├── docker-compose.yml      # Production compose
│   ├── docker-compose.dev.yml  # Development compose
│   └── env.example             # Örnek .env dosyası
│
├── INSTALL.cmd         # 🆕 Windows tek tıkla kurulum
├── setup.ps1           # Windows PowerShell kurulum
├── setup.bat           # Windows CMD kurulum
├── setup.sh            # Linux/Mac kurulum
├── Makefile            # Make komutları
└── README.md
```

---

## 📝 Git Workflow

- `main` → Stabil, deploy edilebilir
- `dev` → Aktif geliştirme
- `feature/<özellik>` → Yeni özellikler
- `fix/<sorun>` → Bug fix'ler

### Commit Mesaj Formatı

```
feat: yeni özellik
fix: hata düzeltme
refactor: kod iyileştirme
docs: dokümantasyon
test: test ekleme
```

### Release Tags

- FAZ-1: `v1.0.0-FAZ1`
- FAZ-2: `v2.0.0-FAZ2`

---

## 🐛 Sorun Giderme

### Docker başlatılamıyor

```bash
# Docker Desktop'ın çalıştığından emin olun
docker info

# Eski container'ları temizleyin
.\setup.ps1 clean-all  # Windows
./setup.sh clean-all   # Linux/Mac
```

### Veritabanı bağlantı hatası

```bash
# Veritabanı container'ının çalıştığını kontrol edin
.\setup.ps1 status  # Windows
./setup.sh status   # Linux/Mac

# Logları kontrol edin
.\setup.ps1 logs-db
```

### Port çakışması

```bash
# .env dosyasında portları değiştirin
# POSTGRES_PORT=5433 (varsayılan 5432)
```

### Sıfırdan Başlamak

Her şeyi silip sıfırdan başlamak için:

```bash
.\setup.ps1 clean-all   # Windows
./setup.sh clean-all    # Linux/Mac
make clean-all          # Make

# Sonra yeniden kurulum
.\setup.ps1 setup       # Windows
./setup.sh setup        # Linux/Mac
make setup              # Make
```

---

## 📄 Lisans

MIT License

---

**Geliştirici:** fkucuker 
**Versiyon:** 2.0.0-FAZ2
