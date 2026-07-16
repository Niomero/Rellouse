# Бесплатный деплой Rellouse Messenger

Полное руководство по бесплатному развертыванию проекта

## 🆓 Бесплатные варианты деплоя

### Вариант 1: Render.com (Рекомендуется)

**Бесплатный план включает:**
- ✅ PostgreSQL: 1 GB storage (90 дней, потом удаляется)
- ✅ Web Service: 512 MB RAM (засыпает после 15 мин неактивности)
- ✅ Static Site: 100 GB bandwidth/месяц
- ⚠️ Ограничение: 750 часов/месяц на Web Service

**Как использовать бесплатно:**

1. **Создайте аккаунт на Render** (не требует карты)
   - https://dashboard.render.com/register

2. **Создайте сервисы вручную** (не через Blueprint):

#### PostgreSQL (бесплатно):
- New → PostgreSQL
- Name: `rellouse-db`
- Plan: **Free** (выберите Free, не Starter!)
- Create Database

#### Backend (бесплатно):
- New → Web Service
- Connect GitHub: `Niomero/Rellouse`
- Name: `rellouse-backend`
- Runtime: Python 3
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- Plan: **Free** (выберите Free!)
- Add Environment Variables (см. ниже)

#### Frontend (бесплатно):
- New → Static Site
- Connect GitHub: `Niomero/Rellouse`
- Name: `rellouse-frontend`
- Build Command: `cd frontend && npm install && npm run build`
- Publish Directory: `frontend/dist`
- Plan: **Free** (автоматически)

### Вариант 2: Railway.app

**Бесплатный план:**
- $5 кредитов/месяц (достаточно для тестирования)
- PostgreSQL включен
- Автоматический деплой из GitHub

**Инструкция:**
1. Зарегистрируйтесь на https://railway.app
2. New Project → Deploy from GitHub
3. Выберите репозиторий `Niomero/Rellouse`
4. Railway автоматически определит Python и Node.js
5. Добавьте PostgreSQL через Railway Dashboard
6. Настройте переменные окружения

### Вариант 3: Vercel (Frontend) + Supabase (Backend + DB)

**Полностью бесплатно:**

#### Frontend на Vercel:
1. Зарегистрируйтесь на https://vercel.com
2. Import Project → GitHub → `Niomero/Rellouse`
3. Root Directory: `frontend`
4. Build Command: `npm run build`
5. Output Directory: `dist`

#### Backend + DB на Supabase:
1. Зарегистрируйтесь на https://supabase.com
2. New Project → создайте PostgreSQL базу
3. Используйте Supabase Edge Functions для backend
4. Или деплойте backend на Railway/Render

### Вариант 4: Полностью локальный деплой

**Бесплатно, но требует свой сервер:**

#### Используя Docker:
```bash
# Создайте docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: rellouse_db
      POSTGRES_USER: rellouse_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://rellouse_user:your_password@postgres:5432/rellouse_db
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:80"

volumes:
  postgres_data:
```

## 🔧 Настройка бесплатного Render

### Environment Variables для Backend (Free):

```env
# Database (получите из Render PostgreSQL)
DATABASE_URL=<Internal Database URL из Render>

# Security (сгенерируйте)
SECRET_KEY=<нажмите "Generate" в Render>
ENCRYPTION_KEY=<нажмите "Generate" в Render>

# App Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME=Rellouse Messenger
APP_VERSION=1.0.0
DEBUG=false

# CORS (обновите после создания frontend)
ALLOWED_ORIGINS=https://rellouse-frontend.onrender.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS_PER_USER=5

# Owner Account
OWNER_USERNAME=Rellouse
OWNER_PASSWORD=none
OWNER_ADDITIONAL_USERNAMES=admin,user,test,none

# S3 (оставьте пустыми для бесплатного плана)
S3_ENDPOINT_URL=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_REGION=us-east-1
```

### Environment Variables для Frontend:

```env
VITE_API_URL=https://rellouse-backend.onrender.com
```

## ⚠️ Ограничения бесплатного плана Render

1. **Web Service засыпает** после 15 минут неактивности
   - Первый запрос после сна займет ~30 секунд
   - Решение: используйте UptimeRobot для пинга каждые 14 минут

2. **PostgreSQL удаляется** через 90 дней
   - Решение: экспортируйте данные регулярно
   - Или используйте платный план ($7/мес)

3. **750 часов/месяц** на Web Service
   - Достаточно для одного сервиса 24/7
   - Для нескольких сервисов нужен платный план

## 🚀 Пошаговая инструкция (Render Free)

### Шаг 1: PostgreSQL

1. Dashboard → New → PostgreSQL
2. Name: `rellouse-db`
3. Database: `rellouse_db`
4. User: `rellouse_user`
5. **Plan: Free** ⚠️
6. Create Database
7. Скопируйте **Internal Database URL**

### Шаг 2: Backend

1. Dashboard → New → Web Service
2. Connect Repository: `Niomero/Rellouse`
3. Name: `rellouse-backend`
4. Runtime: Python 3
5. Build Command: `cd backend && pip install -r requirements.txt`
6. Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Plan: Free** ⚠️
8. Advanced → Add Environment Variables:
   - `DATABASE_URL` = Internal Database URL из шага 1
   - `SECRET_KEY` = Generate
   - `ENCRYPTION_KEY` = Generate
   - Остальные из списка выше
9. Create Web Service

### Шаг 3: Frontend

1. Dashboard → New → Static Site
2. Connect Repository: `Niomero/Rellouse`
3. Name: `rellouse-frontend`
4. Build Command: `cd frontend && npm install && npm run build`
5. Publish Directory: `frontend/dist`
6. Add Environment Variable:
   - `VITE_API_URL` = URL вашего backend из шага 2
7. Create Static Site

### Шаг 4: Обновите CORS

1. Откройте Backend Service
2. Environment → Edit `ALLOWED_ORIGINS`
3. Укажите URL вашего frontend
4. Save Changes

### Шаг 5: Настройте Rewrite Rules (Frontend)

1. Откройте Frontend Static Site
2. Settings → Redirects/Rewrites
3. Add Rule:
   - Source: `/*`
   - Destination: `/index.html`
   - Action: Rewrite
4. Save

## 🔄 Предотвращение засыпания (опционально)

### Используйте UptimeRobot (бесплатно):

1. Зарегистрируйтесь на https://uptimerobot.com
2. Add New Monitor:
   - Type: HTTP(s)
   - URL: `https://rellouse-backend.onrender.com/health`
   - Interval: 14 minutes
3. Сервис будет пинговаться каждые 14 минут

## 💡 Советы по экономии

1. **Используйте один Web Service**
   - Объедините backend и frontend в один сервис
   - Или используйте только Static Site + Serverless Functions

2. **Минимизируйте build time**
   - Кешируйте зависимости
   - Используйте `.dockerignore` и `.gitignore`

3. **Оптимизируйте базу данных**
   - Регулярно очищайте старые данные
   - Используйте индексы
   - Ограничьте размер логов

## 📊 Сравнение бесплатных планов

| Платформа | PostgreSQL | Backend | Frontend | Ограничения |
|-----------|-----------|---------|----------|-------------|
| **Render** | 1 GB (90 дней) | 512 MB RAM | 100 GB/мес | Засыпает, 750 ч/мес |
| **Railway** | Включен | $5 кредитов/мес | Включен | Кредиты кончаются |
| **Vercel** | Нет | Нет | Безлимит | Только frontend |
| **Supabase** | 500 MB | Edge Functions | Нет | Ограничения API |

## 🎯 Рекомендация

**Для тестирования:** Render Free (самый простой)
**Для продакшена:** Railway ($5/мес) или Render Starter ($7/мес)
**Для обучения:** Локальный Docker

## ❓ Частые вопросы

**Q: Почему просит оплату?**
A: Вы выбрали план "Starter" вместо "Free". При создании сервиса выбирайте "Free" план.

**Q: Как долго работает Free план?**
A: PostgreSQL - 90 дней, Web Service - бесплатно всегда (с ограничениями).

**Q: Можно ли использовать без карты?**
A: Да, Render Free не требует карты.

**Q: Что делать когда база удалится?**
A: Экспортируйте данные через `pg_dump` или перейдите на платный план.

## 📞 Поддержка

- Render Docs: https://render.com/docs/free
- Community: https://community.render.com
- GitHub Issues: https://github.com/Niomero/Rellouse/issues
