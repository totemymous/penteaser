#!/bin/bash
# XSS Assistant - Durdurma Script'i

echo "🛑 XSS Assistant Durduruluyor..."
echo "=================================="

# Renk kodları
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Çalışma dizini
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. PID dosyalarından process'leri durdur
if [ -f "logs/vuln.pid" ]; then
    PID=$(cat logs/vuln.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN}✅ Vulnerable Test App durduruldu (PID: $PID)${NC}"
    fi
    rm logs/vuln.pid
fi

if [ -f "logs/backend.pid" ]; then
    PID=$(cat logs/backend.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN}✅ Backend API durduruldu (PID: $PID)${NC}"
    fi
    rm logs/backend.pid
fi

if [ -f "logs/worker.pid" ]; then
    PID=$(cat logs/worker.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo -e "${GREEN}✅ Celery Worker durduruldu (PID: $PID)${NC}"
    fi
    rm logs/worker.pid
fi

# 2. İsme göre process'leri durdur (PID dosyası yoksa)
echo ""
echo "📋 Kalan process'ler temizleniyor..."

pkill -f "vulnerable_app.py" 2>/dev/null && echo -e "${GREEN}✅ Vulnerable App process'leri temizlendi${NC}"
pkill -f "uvicorn" 2>/dev/null && echo -e "${GREEN}✅ Backend process'leri temizlendi${NC}"
pkill -f "celery" 2>/dev/null && echo -e "${GREEN}✅ Celery process'leri temizlendi${NC}"

sleep 2

# 3. Port kontrolü
echo ""
echo "📋 Port kontrolü yapılıyor..."

if lsof -ti:5000 > /dev/null 2>&1; then
    echo -e "${RED}⚠️  Port 5000 hala kullanımda, zorla kapatılıyor...${NC}"
    lsof -ti:5000 | xargs kill -9 2>/dev/null
fi

if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "${RED}⚠️  Port 8000 hala kullanımda, zorla kapatılıyor...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

echo -e "${GREEN}✅ Portlar temizlendi${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}✅ XSS Assistant Başarıyla Durduruldu${NC}"
echo "=================================="
echo ""
echo "🔄 Yeniden başlatmak için: ./start.sh"
echo ""
