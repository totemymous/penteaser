# 📤 GitHub'a Yükleme Rehberi

Bu proje şu anda local ortamda hazır. GitHub repository'nize yüklemek için:

## Yöntem 1: Tüm Proje Dosyalarını Manuel Upload

### Adım 1: Proje Dosyalarını İndirin

Bu komutu çalıştırın (Claude Code terminalinde):

```bash
# Projeyi ZIP olarak paketleyin (.venv ve .git hariç)
cd /home/user
zip -r penteaser-upload.zip penteaser \
  -x "penteaser/.venv/*" \
  -x "penteaser/__pycache__/*" \
  -x "penteaser/**/__pycache__/*" \
  -x "penteaser/.git/*" \
  -x "penteaser/data/*"

# ZIP dosyasının yerini göster
echo "ZIP dosyası hazır: /home/user/penteaser-upload.zip"
ls -lh /home/user/penteaser-upload.zip
```

### Adım 2: ZIP'i İndirin

Claude Code arayüzünden:
- File browser'dan `/home/user/penteaser-upload.zip` dosyasını bulun
- Sağ tıklayıp "Download" seçin

### Adım 3: GitHub'a Yükleyin

1. https://github.com/totemymous/penteaser adresine gidin
2. "uploading an existing file" linkine tıklayın
3. ZIP'i extract edin ve tüm dosyaları sürükleyip bırakın
4. Commit message: "Initial commit - XSS Assistant with Dashboard, WAF Detection, and SQL Injection testing"
5. "Commit changes" tıklayın

---

## Yöntem 2: Git ile Push (Daha Profesyonel)

### Adım 1: GitHub'da Boş Repo Oluşturun

1. https://github.com/new adresine gidin
2. Repository name: `penteaser`
3. Description: "XSS & SQL Injection Testing Tool"
4. Public veya Private seçin
5. **Initialize this repository with a README seçmeyin!** (boş olmalı)
6. "Create repository" tıklayın

### Adım 2: Local Bilgisayarınızda

Bu proje dosyalarını local bilgisayarınıza indirip şu komutları çalıştırın:

```bash
# GitHub'dan clone edin (ilk başta boş olacak)
git clone https://github.com/totemymous/penteaser.git
cd penteaser

# Aşağıdaki dosyaları bu dizine kopyalayın (manuel veya script ile)
# Tüm dosya listesi aşağıda
```

### Adım 3: Dosyaları Ekleyin ve Push Edin

```bash
cd penteaser

# Tüm dosyaları add edin
git add .

# Commit edin
git commit -m "Initial commit: XSS Assistant with Dashboard, WAF, SQLi

Features:
- Real-time web dashboard (Bootstrap 5)
- XSS detection (Reflected + Stored)
- SQL Injection testing (Error, Boolean, Time-based)
- WAF detection (9 major firewalls)
- Celery workers with Redis
- FastAPI backend
- Vulnerable test application

OWASP Top 10 A03:2021 - Injection coverage"

# GitHub'a push edin
git push -u origin main
# veya
git push -u origin master
```

---

## Yöntem 3: Dosya Listesi ile Manuel Kopyalama

İhtiyacınız olan tüm dosyalar:

### Ana Dizin:
```
penteaser/
├── start.sh                    # Başlatma script'i
├── stop.sh                     # Durdurma script'i
├── README.md                   # Ana dokümantasyon (eski)
├── KURULUM.md                  # Türkçe kurulum rehberi
├── QUICKSTART.md               # Hızlı başlangıç
├── GITHUB_UPLOAD.md           # Bu dosya
└── .gitignore                 # Git ignore
```

### Backend:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI entry point
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── target.py
│   │   ├── session.py
│   │   ├── finding.py
│   │   └── audit_log.py
│   └── routers/
│       ├── __init__.py
│       ├── health.py
│       ├── targets.py
│       ├── sessions.py
│       └── reports.py
└── requirements.txt
```

### Workers:
```
workers/
├── __init__.py
├── config.py
├── tasks.py                   # Celery tasks
├── xss_tester.py             # XSS detection
├── sqli_tester.py            # SQL Injection detection
├── waf_detector.py           # WAF detection
├── browser.py
└── requirements.txt
```

### Frontend:
```
frontend/
├── index.html                # Dashboard UI
└── dashboard.js              # Dashboard logic
```

### Test App:
```
test_app/
└── vulnerable_app.py         # Intentionally vulnerable Flask app
```

### Scripts:
```
scripts/
├── test_dashboard.sh
├── test_waf_detection.sh
└── test_stored_xss.sh
```

---

## 🎯 En Hızlı Yol

Eğer hızlı bir şekilde test etmek istiyorsanız:

1. **Dosyaları tek tek kopyalayın:**
   - GitHub'da "Add file" > "Create new file" tıklayın
   - Her dosya için içeriği kopyalayıp yapıştırın
   - Dosya yolu ile birlikte oluşturun (örn: `backend/app/main.py`)

2. **requirements.txt dosyalarını ekleyin:**

### backend/requirements.txt:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
celery==5.3.4
redis==5.0.1
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

### workers/requirements.txt:
```
celery==5.3.4
redis==5.0.1
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
playwright==1.40.0
```

3. **.gitignore oluşturun:**
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
venv/
ENV/

# Database
*.db
*.sqlite3
data/

# Logs
*.log
logs/
*.pid

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
recordings/
```

---

## 📋 Özet: Tavsiye Edilen Yol

**En Kolay:**
1. Tüm dosya içeriklerini Claude Code'dan kopyalayın
2. GitHub web arayüzünden "Create new file" ile ekleyin
3. Commit edin

**En Profesyonel:**
1. GitHub'da boş repo oluşturun
2. Local'de clone edin
3. Dosyaları kopyalayın
4. `git add . && git commit && git push`

---

## 🆘 Yardım

Dosya içeriklerini görmek için:

```bash
# Herhangi bir dosyanın içeriğini görmek için
cat /home/user/penteaser/backend/app/main.py

# Tüm Python dosyalarını listelemek için
find /home/user/penteaser -name "*.py" -type f
```

Claude Code'da da dosyaları File Explorer'dan açıp kopyalayabilirsiniz!
