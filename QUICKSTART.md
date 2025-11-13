# ⚡ Quick Start Guide - XSS Assistant

Bu branch'te yeni eklenen özellikleri hemen test etmek için hızlı başlangıç rehberi.

## 🎯 Bu Branch'teki Yeni Özellikler

✅ **Stored (Persistent) XSS Detection**
✅ **Real-time Web Dashboard** (Bootstrap 5)
✅ **WAF Detection** (9 major firewall)
✅ **SQL Injection Testing** (Error-based, Boolean-based, Time-based)
✅ **OWASP A03:2021** - Injection coverage

## 🚀 30 Saniyede Başlat

### 1. Repository'yi İndirin

```bash
git clone https://github.com/totemymous/penteaser.git
cd penteaser
git checkout claude/understand-project-setup-011CUrZipvJfQfTcwLgJAYtz
```

### 2. Tek Komutla Başlatın

```bash
chmod +x start.sh stop.sh
./start.sh
```

**Bu kadar!** 🎉

## 🌐 Erişim Adresleri

Servisler başladıktan sonra:

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Dashboard** | http://localhost:8000/ | Ana dashboard |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Test App** | http://localhost:5000/ | Vulnerable test app |

## 🎨 Dashboard'u Kullanma

### 1. Hedef Ekleyin

Dashboard'da "Add Target" butonuna tıklayın:

**Önerilen Test Hedefi:**
- **Name:** Local Test App
- **URL:** http://localhost:5000/
- **Description:** Intentionally vulnerable test application

### 2. Tarama Başlatın

1. **Targets** tab'ine gidin
2. Eklediğiniz hedefin yanındaki **"Start Scan"** butonuna tıklayın
3. **Sessions** tab'inde taramayı izleyin (auto-refresh 30 saniye)
4. Status **"completed"** olunca **"View Report"** ile bulguları görün

### 3. Sonuçları İnceleyin

Beklenen bulgular:

- ✅ **2x Reflected XSS** (HIGH) - `search` ve `comment` formları
- ✅ **1x SQL Injection** (CRITICAL) - `login` formu
- ✅ **WAF Detection** (INFO) - "No WAF detected"

## 🧪 Manuel Test (API ile)

### Hedef Ekle

```bash
curl -X POST http://localhost:8000/api/v1/targets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Target",
    "url": "http://localhost:5000/",
    "description": "My test target"
  }'
```

### Tarama Başlat

```bash
# Response'dan target ID'yi alın (örn: 1)
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": 1,
    "name": "Security Scan",
    "description": "Full scan"
  }'
```

### Rapor Al

```bash
# Response'dan session ID'yi alın (örn: 1)
# 15-20 saniye bekleyin, sonra:
curl http://localhost:8000/api/v1/reports/sessions/1 | python3 -m json.tool
```

## 🔍 Test Edilebilecek Vulnerabilities

### XSS Testing

**Reflected XSS (GET):**
```
http://localhost:5000/search?q=<script>alert('XSS')</script>
```

**Reflected XSS (POST):**
```
http://localhost:5000/comment
# Form: author=<script>alert('XSS')</script>
```

**Stored XSS (Persistent):**
```
http://localhost:5000/guestbook
# Form: name=Hacker&message=<script>alert('Stored')</script>
```

### SQL Injection Testing

**Error-based SQL Injection:**
```
http://localhost:5000/login?username=admin' OR '1'='1
```

**Expected:** SQL error veya unauthorized access

## 🛑 Servisleri Durdurma

```bash
./stop.sh
```

## 📊 Dashboard Özellikleri

### Ana Metrikler (Üst kısım):
- **Total Targets:** Eklenen hedef sayısı
- **Total Sessions:** Çalıştırılan tarama sayısı
- **Active Scans:** Devam eden taramalar
- **Total Vulnerabilities:** Bulunan toplam zafiyet

### Tabs:

**1. Targets Tab:**
- Tüm hedefleri listeler
- "Add Target" butonu
- Her hedef için "Start Scan" butonu

**2. Sessions Tab:**
- Tüm taramaları listeler
- Status göstergesi (pending, running, completed)
- Duration bilgisi
- "View Report" butonu

**3. Findings Tab:**
- Tüm bulguları listeler
- Severity-based renklendirme:
  - 🔴 CRITICAL (kırmızı)
  - 🟠 HIGH (turuncu)
  - 🟡 MEDIUM (sarı)
  - 🔵 LOW (mavi)
  - ⚪ INFO (gri)
- Payload ve evidence detayları
- Remediation önerileri

## 🐛 Sorun Giderme

### Port zaten kullanımda

```bash
# Port 5000'i temizle
lsof -ti:5000 | xargs kill -9

# Port 8000'i temizle
lsof -ti:8000 | xargs kill -9

# Sonra yeniden başlat
./start.sh
```

### Redis hatası

```bash
# Redis'i kontrol et
redis-cli ping

# Redis başlat
redis-server --daemonize yes

# Sonra yeniden başlat
./start.sh
```

### Worker çalışmıyor

```bash
# Logları kontrol et
tail -f logs/worker.log

# Worker'ı manuel başlat
source .venv/bin/activate
python -m celery -A workers.tasks worker --loglevel=info
```

### Dashboard yüklenmiyor

```bash
# Backend loglarını kontrol et
tail -f logs/backend.log

# Health check
curl http://localhost:8000/health
```

## 📝 Log Dosyaları

Sorun yaşarsanız logları kontrol edin:

```bash
# Tüm loglar logs/ dizininde
tail -f logs/vulnerable_app.log  # Test app logs
tail -f logs/backend.log          # Backend API logs
tail -f logs/worker.log           # Celery worker logs
```

## 🎯 İlk Test Senaryosu

### Adım 1: Servisleri Başlat
```bash
./start.sh
# Tüm servisler yeşil tick almalı ✅
```

### Adım 2: Dashboard'a Gir
```
http://localhost:8000/
```

### Adım 3: Hedef Ekle
- "Add Target" butonuna tıkla
- Name: Test Target
- URL: http://localhost:5000/
- Description: Test
- "Add Target" ile kaydet

### Adım 4: Tarama Başlat
- Targets tab'inde hedefin yanındaki "Start Scan" butonuna tıkla
- Otomatik olarak Sessions tab'ine yönlendirileceksiniz

### Adım 5: Taramayı İzle
- Session status "running" → "completed" olacak (~10-15 saniye)
- "View Report" butonuna tıkla

### Adım 6: Bulguları İncele
Göreceğiniz bulgular:
```
✅ 2x Reflected XSS (HIGH)
   - /search?q= parameter
   - /comment form author field

✅ 1x SQL Injection (CRITICAL)
   - /login?username= parameter

✅ WAF Detection (INFO)
   - No WAF detected
```

## 🎓 Vulnerability Detayları

### XSS Bulgularında:
- **Payload:** Kullanılan XSS payload
- **Evidence:** Response'daki reflection
- **Status Code:** HTTP response code
- **Method:** GET veya POST
- **Remediation:** Düzeltme önerileri

### SQL Injection Bulgularında:
- **Payload:** Kullanılan SQL injection payload
- **Evidence:** SQL error message veya behavior
- **Injection Type:** Error-based, Boolean-based, Time-based
- **Remediation:** Parameterized queries önerisi

## 📊 Beklenen Performans

- **Tarama Süresi:** ~10-15 saniye (local test app için)
- **Bulunan Vulnerabilities:** 3 (2 XSS + 1 SQLi)
- **False Positive Rate:** ~0% (intentionally vulnerable app)

## 🔄 Yeniden Test Etme

Aynı hedefi tekrar test etmek için:

1. Targets tab'ine git
2. Hedefin yanındaki "Start Scan" butonuna tekrar tıkla
3. Yeni bir session oluşturulacak
4. Sessions tab'inden tüm geçmiş taramaları görebilirsiniz

## 🌍 Gerçek Hedefleri Test Etme

**⚠️ ÖNEMLİ:** Sadece **yetkiniz olan** sistemleri test edin!

**Yasal Test Siteleri:**
- http://testphp.vulnweb.com/ (Acunetix test site)
- http://testhtml5.vulnweb.com/ (HTML5 test site)
- https://juice-shop.herokuapp.com/ (OWASP Juice Shop)

Bu siteleri dashboard'dan hedef olarak ekleyip test edebilirsiniz.

## 🎉 Başarılı Kurulum Göstergeleri

Eğer aşağıdakileri görebiliyorsanız, kurulum başarılı:

```
✅ Dashboard yüklendi (http://localhost:8000/)
✅ Metrics gösteriliyor (targets, sessions, findings)
✅ "Add Target" butonu çalışıyor
✅ Tarama başlatılabiliyor
✅ Session tamamlanıyor (completed status)
✅ Report görüntülenebiliyor
✅ Bulgular listelenebiliyor
```

## 📞 Yardım

Sorun yaşarsanız:

1. **Logları kontrol edin:** `tail -f logs/*.log`
2. **Servisleri yeniden başlatın:** `./stop.sh && ./start.sh`
3. **Redis'i kontrol edin:** `redis-cli ping`
4. **Port çakışması:** `lsof -ti:5000,8000 | xargs kill -9`

---

**Dashboard:** http://localhost:8000/
**Detaylı Kurulum:** `KURULUM.md` dosyasına bakın
**Tam Dokümantasyon:** `README.md` dosyasına bakın

🚀 İyi testler!
