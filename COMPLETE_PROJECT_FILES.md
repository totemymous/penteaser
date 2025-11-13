# 🚀 XSS Assistant - Tüm Proje Dosyaları

Bu dosya, projenin tüm önemli dosyalarını içerir. Kopyalayıp yapıştırarak GitHub'a upload edebilirsiniz.

---

## 📋 Dosya İçerikleri

Aşağıdaki dosyaları GitHub'da oluşturup içeriklerini kopyalayın.

### En Kritik 15 Dosya:

1. **start.sh** - Tüm servisleri başlatır
2. **stop.sh** - Tüm servisleri durdurur
3. **backend/app/main.py** - FastAPI backend
4. **backend/requirements.txt** - Backend bağımlılıkları
5. **workers/tasks.py** - Celery task'ları
6. **workers/xss_tester.py** - XSS detection engine
7. **workers/sqli_tester.py** - SQL Injection tester
8. **workers/waf_detector.py** - WAF detection
9. **workers/requirements.txt** - Worker bağımlılıkları
10. **frontend/index.html** - Dashboard UI
11. **frontend/dashboard.js** - Dashboard logic
12. **test_app/vulnerable_app.py** - Test application
13. **KURULUM.md** - Türkçe kurulum
14. **QUICKSTART.md** - Hızlı başlangıç
15. **.gitignore** - Git ignore

---

## 📁 Dosya Yapısı (Oluşturmanız Gereken)

```
penteaser/
├── README.md
├── KURULUM.md
├── QUICKSTART.md
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

---

## 🎯 Yükleme Yöntemi

### GitHub Web Arayüzü ile:

1. https://github.com/totemymous/penteaser adresine gidin
2. Her dosya için:
   - "Add file" > "Create new file" tıklayın
   - Dosya adını yazın (örn: `start.sh`)
   - Aşağıdaki içeriği kopyalayıp yapıştırın
   - "Commit new file" tıklayın

### Dizin Oluşturma:

Örnek: `backend/app/main.py` oluşturmak için:
- Dosya adı: `backend/app/main.py` (otomatik dizin oluşturur)
- İçeriği yapıştırın
- Commit edin

---

Şimdi aşağıdaki bölümlerde tüm dosya içeriklerini bulabilirsiniz!
