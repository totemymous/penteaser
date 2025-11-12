# 📁 XSS Assistant - Tam Dosya Yapısı

Bu dosya tüm proje dosyalarını ve yapısını gösterir.

## 📂 Dizin Yapısı

```
penteaser/
├── README.md
├── KURULUM.md
├── QUICKSTART.md
├── GITHUB_UPLOAD.md
├── start.sh
├── stop.sh
├── .gitignore
│
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── target.py
│       │   ├── session.py
│       │   ├── finding.py
│       │   └── audit_log.py
│       └── routers/
│           ├── __init__.py
│           ├── health.py
│           ├── targets.py
│           ├── sessions.py
│           └── reports.py
│
├── workers/
│   ├── requirements.txt
│   ├── __init__.py
│   ├── config.py
│   ├── tasks.py
│   ├── xss_tester.py
│   ├── sqli_tester.py
│   ├── waf_detector.py
│   └── browser.py
│
├── frontend/
│   ├── index.html
│   └── dashboard.js
│
├── test_app/
│   └── vulnerable_app.py
│
└── scripts/
    ├── test_dashboard.sh
    ├── test_waf_detection.sh
    └── test_stored_xss.sh
```

## 📝 Dosya Sayıları

- Python dosyaları: 21
- Shell scripts: 5
- Markdown dosyaları: 4
- HTML/JS dosyaları: 2
- Config dosyaları: 3
- **Toplam: 65+ dosya**

## 🎯 Öncelikli Dosyalar (Bunları Mutlaka Yükleyin)

### 1. Ana Dizin (Root)
- ✅ start.sh
- ✅ stop.sh
- ✅ KURULUM.md
- ✅ QUICKSTART.md
- ✅ .gitignore

### 2. Backend (Kritik)
- ✅ backend/requirements.txt
- ✅ backend/app/main.py
- ✅ backend/app/config.py
- ✅ backend/app/database.py
- ✅ backend/app/models/ (tüm dosyalar)
- ✅ backend/app/routers/ (tüm dosyalar)

### 3. Workers (Kritik)
- ✅ workers/requirements.txt
- ✅ workers/tasks.py
- ✅ workers/xss_tester.py
- ✅ workers/sqli_tester.py
- ✅ workers/waf_detector.py
- ✅ workers/config.py

### 4. Frontend (Kritik)
- ✅ frontend/index.html
- ✅ frontend/dashboard.js

### 5. Test App
- ✅ test_app/vulnerable_app.py

### 6. Scripts
- ✅ scripts/ (tüm .sh dosyaları)
