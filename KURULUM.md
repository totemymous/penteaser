# 🚀 XSS Assistant - Kurulum ve Çalıştırma Rehberi

## 📋 Gereksinimler

- **Python:** 3.9 veya üzeri
- **Redis:** 6.0 veya üzeri
- **İşletim Sistemi:** Linux, macOS veya Windows (WSL)
- **RAM:** En az 2GB
- **Disk:** ~500MB boş alan

## 🔧 Kurulum Adımları

### 1. Repository'yi İndirin

```bash
git clone https://github.com/totemymous/penteaser.git
cd penteaser
```

### 2. Branch'i Değiştirin

```bash
# En son özelliklerin olduğu branch'e geçin
git checkout claude/understand-project-setup-011CUrZipvJfQfTcwLgJAYtz
```

### 3. Python Virtual Environment Oluşturun

```bash
# Virtual environment oluştur
python3 -m venv .venv

# Aktif et (Linux/macOS)
source .venv/bin/activate

# VEYA Windows için
# .venv\Scripts\activate
```

### 4. Bağımlılıkları Yükleyin

```bash
# Backend bağımlılıkları
pip install -r backend/requirements.txt

# Worker bağımlılıkları
pip install -r workers/requirements.txt
```

### 5. Redis Kurulumu ve Başlatma

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Docker ile (Tüm platformlar):
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Redis Kontrolü:
```bash
redis-cli ping
# "PONG" yanıtını almalısınız
```

## 🎯 Servisleri Başlatma

Projeyi çalıştırmak için **4 ayrı terminal** açmanız gerekiyor:

### Terminal 1: Vulnerable Test App (Port 5000)

```bash
cd /path/to/penteaser
source .venv/bin/activate
python test_app/vulnerable_app.py
```

**Çıktı:**
```
🚀 Starting Vulnerable Test Application...
⚠️  WARNING: This app is intentionally vulnerable!
📍 Access at: http://localhost:5000
```

### Terminal 2: Backend API (Port 8000)

```bash
cd /path/to/penteaser/backend
source ../.venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Çıktı:**
```
🚀 XSS Assistant v0.1.0 starting...
📝 API docs available at: /docs
🔍 Health check: /health
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 3: Celery Worker

```bash
cd /path/to/penteaser
source .venv/bin/activate
python -m celery -A workers.tasks worker --loglevel=info --concurrency=1
```

**Çıktı:**
```
-------------- celery@yourhost ready.
```

### Terminal 4: İsteğe Bağlı - Test Komutları

Bu terminalde test komutlarını çalıştırabilirsiniz.

## ✅ Kurulum Testi

### 1. Hızlı Sistem Kontrolü

```bash
cd /path/to/penteaser
source .venv/bin/activate

# Health check
curl http://localhost:8000/health

# Vulnerable app kontrolü
curl http://localhost:5000/ | grep "XSS"

# Redis kontrolü
redis-cli ping
```

### 2. Dashboard'a Erişim

Tarayıcınızda açın:
```
http://localhost:8000/
```

Görecekleriniz:
- ✅ Real-time metrikler
- ✅ Hedef listesi
- ✅ Session izleme
- ✅ Bulgular raporu

### 3. Test Hedefleri Ekleyin

Dashboard üzerinden "Add Target" butonuna tıklayın ve ekleyin:

**Hedef 1: Local Vulnerable App**
- Name: Local Test App
- URL: http://localhost:5000/
- Description: Intentionally vulnerable test application

**Hedef 2: External Test Site (opsiyonel)**
- Name: Acunetix Test PHP
- URL: http://testphp.vulnweb.com/
- Description: Legal public test site

### 4. İlk Taramayı Başlatın

Dashboard'da:
1. Targets tab'ine gidin
2. "Local Test App" hedefini bulun
3. "Start Scan" butonuna tıklayın
4. Sessions tab'inde taramayı izleyin
5. Tamamlandığında "View Report" ile bulguları görün

## 🧪 Manuel Test Komutları

### API ile Hedef Ekleme

```bash
curl -X POST http://localhost:8000/api/v1/targets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Target",
    "url": "http://localhost:5000/",
    "description": "My test target"
  }'
```

### API ile Tarama Başlatma

```bash
# Önce target ID'yi alın (örn: 1)
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "name": "Test Scan",
    "description": "Testing XSS and SQL Injection"
  }'
```

### Rapor Görüntüleme

```bash
# Session ID'yi alın (örn: 1) ve rapor isteyin
curl http://localhost:8000/api/v1/reports/sessions/1 | python3 -m json.tool
```

## 🔍 Test Edilecek Vulnerable Endpoints

### XSS Test Endpoints:

1. **Reflected XSS (GET):**
   ```
   http://localhost:5000/search?q=<script>alert('XSS')</script>
   ```

2. **Reflected XSS (POST):**
   ```
   http://localhost:5000/comment
   Form: author=<script>alert('XSS')</script>
   ```

3. **Stored XSS:**
   ```
   http://localhost:5000/guestbook
   Form: name=Test&message=<script>alert('Stored XSS')</script>
   ```

### SQL Injection Test Endpoint:

```
http://localhost:5000/login?username=admin' OR '1'='1
```

**Beklenen sonuç:** SQL error veya unauthorized data access

## 📊 Hazır Test Script'leri

### Tam Sistem Testi

```bash
cd /path/to/penteaser
chmod +x scripts/*.sh

# Dashboard testi
./scripts/test_dashboard.sh

# WAF detection testi
./scripts/test_waf_detection.sh

# Stored XSS testi
./scripts/test_stored_xss.sh
```

## 🎨 Dashboard Özellikleri

### Ana Ekran:
- **Total Targets:** Eklenen hedef sayısı
- **Total Sessions:** Çalıştırılan tarama sayısı
- **Active Scans:** Devam eden taramalar
- **Total Vulnerabilities:** Bulunan toplam zafiyet

### Targets Tab:
- Hedef listesi
- Hedef ekleme
- Hedef başına tarama başlatma

### Sessions Tab:
- Tüm taramalar
- Status (pending, running, completed, failed)
- Duration
- Report görüntüleme

### Findings Tab:
- Tüm bulgular
- Severity-based filtreleme (Critical, High, Medium, Low)
- Detaylı payload ve evidence
- Remediation önerileri

## 🐛 Sorun Giderme

### Redis Bağlantı Hatası

```bash
# Redis çalışıyor mu kontrol et
redis-cli ping

# Redis başlat
redis-server --daemonize yes
```

### Port Zaten Kullanımda

```bash
# Port 5000 için
lsof -ti:5000 | xargs kill -9

# Port 8000 için
lsof -ti:8000 | xargs kill -9
```

### Celery Worker Başlamıyor

```bash
# Redis connection kontrol et
redis-cli ping

# Virtual environment aktif mi?
which python
# /path/to/penteaser/.venv/bin/python olmalı

# Eski worker'ları öldür
pkill -f celery
```

### Dashboard Yüklenmiyor

```bash
# Backend çalışıyor mu?
curl http://localhost:8000/health

# CORS ayarları kontrol
# backend/app/main.py dosyasında CORS enabled olmalı
```

### Tarama Hiç Başlamıyor

```bash
# Celery worker loglarını kontrol et
tail -f /tmp/worker.log

# Redis kuyrukları kontrol et
redis-cli
> KEYS *
> LLEN celery
```

## 📁 Proje Yapısı

```
penteaser/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # Ana uygulama
│   │   ├── models/      # Database modelleri
│   │   ├── routers/     # API endpoints
│   │   └── config.py    # Konfigürasyon
│   └── requirements.txt
├── workers/              # Celery workers
│   ├── tasks.py         # Ana task'lar
│   ├── xss_tester.py    # XSS detection
│   ├── sqli_tester.py   # SQL Injection detection
│   ├── waf_detector.py  # WAF detection
│   └── requirements.txt
├── frontend/             # Web dashboard
│   ├── index.html       # Dashboard UI
│   └── dashboard.js     # Dashboard logic
├── test_app/            # Vulnerable test app
│   └── vulnerable_app.py
├── scripts/             # Test scripts
│   ├── test_dashboard.sh
│   ├── test_waf_detection.sh
│   └── test_stored_xss.sh
└── data/                # SQLite database
    └── xss_assistant.db
```

## 🔒 Güvenlik Notları

⚠️ **ÖNEMLİ:**

1. **Bu araç sadece yetkili penetrasyon testleri için kullanılmalıdır**
2. Vulnerable test app (`localhost:5000`) sadece test amaçlıdır
3. Production ortamında kullanmayın
4. Sadece kendinize ait veya test izni aldığınız sistemleri test edin
5. `AUTO_APPROVE_SESSIONS=true` ayarı sadece test/lab ortamları içindir

## 📖 API Dokümantasyonu

API dokümantasyonuna erişim:
```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```

## 🎯 İlk Tarama Sonrası Beklentiler

Başarılı bir taramadan sonra görecekleriniz:

### Findings:
- ✅ 2x Reflected XSS (HIGH) - `/search` ve `/comment` endpoints
- ✅ 1x SQL Injection (CRITICAL) - `/login` endpoint
- ✅ WAF Detection (INFO) - "No WAF detected"

### Session Details:
- Status: Completed
- Duration: ~5-10 saniye
- Endpoints Tested: 3
- Vulnerabilities Found: 3

### Report:
- Detaylı payload bilgisi
- HTTP response snippets
- Remediation önerileri
- OWASP kategorileri

## 🆘 Yardım ve Destek

### Loglar

```bash
# Backend logs
tail -f /tmp/backend.log

# Worker logs
tail -f /tmp/worker.log

# Vulnerable app logs
tail -f /tmp/vuln_app.log
```

### GitHub Issues

Sorun yaşıyorsanız:
```
https://github.com/totemymous/penteaser/issues
```

## 🚀 Başarılı Kurulum Örneği

Tüm servisler başarıyla çalışıyorsa görecekleriniz:

```bash
# Terminal 1
🚀 Starting Vulnerable Test Application...
 * Running on http://127.0.0.1:5000

# Terminal 2
🚀 XSS Assistant v0.1.0 starting...
INFO:     Uvicorn running on http://0.0.0.0:8000

# Terminal 3
-------------- celery@yourhost ready.

# Browser (http://localhost:8000)
✅ Dashboard yüklendi
✅ Total Targets: 0
✅ Total Sessions: 0
```

Artık sistemi kullanmaya hazırsınız! 🎉

---

**Dashboard:** http://localhost:8000/
**API Docs:** http://localhost:8000/docs
**Test App:** http://localhost:5000/

İyi testler! 🔒🛡️
