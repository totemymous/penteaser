#!/bin/bash
# XSS Assistant - Hızlı Başlatma Script'i

echo "🚀 XSS Assistant Başlatılıyor..."
echo "=================================="

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Çalışma dizini
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. Eski process'leri temizle
echo ""
echo "📋 1. Eski process'ler temizleniyor..."
pkill -f "vulnerable_app.py" 2>/dev/null
pkill -f "uvicorn" 2>/dev/null
pkill -f "celery" 2>/dev/null
sleep 2
echo -e "${GREEN}✅ Temizlik tamamlandı${NC}"

# 2. Redis kontrolü
echo ""
echo "📋 2. Redis kontrolü yapılıyor..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠️  Redis çalışmıyor, başlatılıyor...${NC}"
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis başlatıldı${NC}"
    else
        echo -e "${RED}❌ Redis başlatılamadı! Lütfen manuel olarak başlatın:${NC}"
        echo "   redis-server --daemonize yes"
        exit 1
    fi
fi

# 3. Virtual environment kontrolü
echo ""
echo "📋 3. Virtual environment kontrolü..."
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment bulunamadı, oluşturuluyor...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment oluşturuldu${NC}"
fi

# 4. Bağımlılıkları kontrol et
echo ""
echo "📋 4. Bağımlılıklar kontrol ediliyor..."
source .venv/bin/activate

if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Backend bağımlılıkları yükleniyor...${NC}"
    pip install -r backend/requirements.txt > /dev/null 2>&1
fi

if ! python -c "import celery" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Worker bağımlılıkları yükleniyor...${NC}"
    pip install -r workers/requirements.txt > /dev/null 2>&1
fi
echo -e "${GREEN}✅ Bağımlılıklar hazır${NC}"

# Log dosyaları için dizin
mkdir -p logs

# 5. Servisleri başlat
echo ""
echo "📋 5. Servisler başlatılıyor..."

# Vulnerable App (Port 5000)
echo "   🔧 Vulnerable Test App başlatılıyor..."
python test_app/vulnerable_app.py > logs/vulnerable_app.log 2>&1 &
VULN_PID=$!
sleep 2

# Backend API (Port 8000)
echo "   🔧 Backend API başlatılıyor..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 3

# Celery Worker
echo "   🔧 Celery Worker başlatılıyor..."
python -m celery -A workers.tasks worker --loglevel=info --concurrency=1 > logs/worker.log 2>&1 &
WORKER_PID=$!
sleep 3

# 6. Servis kontrolü
echo ""
echo "📋 6. Servisler kontrol ediliyor..."

# Vulnerable App kontrolü
if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Vulnerable Test App: http://localhost:5000/${NC}"
else
    echo -e "   ${RED}❌ Vulnerable Test App başlatılamadı${NC}"
    cat logs/vulnerable_app.log | tail -5
fi

# Backend kontrolü
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Backend API: http://localhost:8000/${NC}"
else
    echo -e "   ${RED}❌ Backend API başlatılamadı${NC}"
    cat logs/backend.log | tail -5
fi

# Worker kontrolü
if ps -p $WORKER_PID > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Celery Worker: Çalışıyor${NC}"
else
    echo -e "   ${RED}❌ Celery Worker başlatılamadı${NC}"
    cat logs/worker.log | tail -5
fi

# 7. PID'leri kaydet
echo "$VULN_PID" > logs/vuln.pid
echo "$BACKEND_PID" > logs/backend.pid
echo "$WORKER_PID" > logs/worker.pid

echo ""
echo "=================================="
echo -e "${GREEN}🎉 XSS Assistant Başarıyla Başlatıldı!${NC}"
echo "=================================="
echo ""
echo "📊 ERİŞİM BİLGİLERİ:"
echo "   🌐 Dashboard:        http://localhost:8000/"
echo "   📖 API Docs:         http://localhost:8000/docs"
echo "   🎯 Vulnerable App:   http://localhost:5000/"
echo "   🔍 Health Check:     http://localhost:8000/health"
echo ""
echo "🧪 TEST ENDPOINTS:"
echo "   XSS Test:            http://localhost:5000/search?q=test"
echo "   SQL Injection Test:  http://localhost:5000/login?username=admin"
echo "   Stored XSS Test:     http://localhost:5000/guestbook"
echo ""
echo "📝 LOG DOSYALARI:"
echo "   Vulnerable App:      tail -f logs/vulnerable_app.log"
echo "   Backend:             tail -f logs/backend.log"
echo "   Worker:              tail -f logs/worker.log"
echo ""
echo "🛑 DURDURMAK İÇİN:"
echo "   ./stop.sh"
echo ""
echo -e "${YELLOW}⚠️  Not: Dashboard'a erişmek için tarayıcınızda http://localhost:8000/ adresini açın${NC}"
echo ""
