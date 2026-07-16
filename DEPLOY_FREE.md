# Бесплатный деплой Rellouse Messenger

Полное руководство по бесплатному развертыванию проекта

## 🆓 Бесплатные варианты деплоя

### Вариант 1: Render.com (Рекомендуется)

**Бесплатный план включает:**
- ✅ PostgreSQL: 1 GB storage (90 дней, потом удаляется)
- ✅ Web Service: 512 MB RAM (засыпает после 15 мин неактивности)
- ✅ Static Site: 100 GB bandwidth/месяц
- ⚠️ Ограничение: 750 часов/месяц на Web Service

## 🚀 Быстрый деплой (у вас уже есть база данных)

### Шаг 1: Backend Service

1. **Dashboard → New → Web Service**
2. Connect Repository: `Niomero/Rellouse`
3. **Настройки:**
   - Name: `rellouse-backend`
   - Runtime: **Python 3**
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan: Free** ⚠️ (выберите Free, не Starter!)

4. **Environment Variables** (нажмите "Add Environment Variable"):

```env
# Database (ваша существующая база)
DATABASE_URL=postgresql://niomero:MOXUCpO1XEu0gX3eb9jRn2rBrTwSwv0g@dpg-d9794s6q1p3s738kbbqg-a.oregon-postgres.render.com/ghost_db_vh94

# Security (нажмите "Generate" для каждой)
SECRET_KEY=<нажмите Generate>
ENCRYPTION_KEY=<нажмите Generate>

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

# S3 (оставьте пустыми)
S3_ENDPOINT_URL=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
S3_REGION=us-east-1
```

5. **Create Web Service**

### Шаг 2: Frontend Static Site

1. **Dashboard → New → Static Site**
2. Connect Repository: `Niomero/Rellouse`
3. **Настройки:**
   - Name: `rellouse-frontend`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
   - Plan: **Free** (автоматически)

4. **Environment Variable:**
   - Key: `VITE_API_URL`
   - Value: `https://rellouse-backend.onrender.com` (замените на ваш backend URL)

5. **Create Static Site**

### Шаг 3: Настройте Rewrite Rules (Frontend)

1. Откройте ваш Frontend Static Site
2. **Settings → Redirects/Rewrites**
3. **Add Rule:**
   - Source: `/*`
   - Destination: `/index.html`
   - Action: **Rewrite**
4. **Save**

### Шаг 4: Обновите CORS (Backend)

1. Откройте ваш Backend Web Service
2. **Environment → найдите `ALLOWED_ORIGINS`**
3. **Edit** и замените на реальный URL вашего frontend
   - Например: `https://rellouse-frontend.onrender.com`
4. **Save Changes**
5. Backend автоматически перезапустится

### Шаг 5: Проверьте деплой

1. **Откройте ваш frontend URL**
   - Например: `https://rellouse-frontend.onrender.com`

2. **Проверьте регистрацию:**
   - Создайте новый аккаунт
   - Войдите в систему

3. **Смените пароль Owner:**
   - Логин: `Rellouse`
   - Пароль по умолчанию: `none`
   - ⚠️ **ВАЖНО:** Смените пароль сразу!

## ⚠️ Важные замечания

### О вашей базе данных:

Вы используете базу данных `ghost_db_vh94`. Убедитесь, что:
- ✅ База данных пустая или вы готовы к миграции
- ✅ У вас есть доступ к базе данных
- ✅ База данных находится на Free плане Render

### Первый запуск:

При первом запуске backend автоматически:
1. Создаст все таблицы в базе данных
2. Создаст Owner аккаунт (@Rellouse)
3. Создаст @Verify бота
4. Зарезервирует системные username

## 🔄 Предотвращение засыпания (опционально)

Backend на Free плане засыпает после 15 минут неактивности.

### Используйте UptimeRobot (бесплатно):

1. Зарегистрируйтесь на https://uptimerobot.com
2. **Add New Monitor:**
   - Type: **HTTP(s)**
   - URL: `https://rellouse-backend.onrender.com/health`
   - Monitoring Interval: **14 minutes**
3. **Create Monitor**

Теперь ваш backend будет пинговаться каждые 14 минут и не будет засыпать!

## 📊 Что вы получите

### Backend API:
- URL: `https://rellouse-backend.onrender.com`
- API Docs: `https://rellouse-backend.onrender.com/docs` (только если DEBUG=true)
- Health Check: `https://rellouse-backend.onrender.com/health`

### Frontend:
- URL: `https://rellouse-frontend.onrender.com`
- Responsive дизайн
- Light/Dark тема
- Real-time чат через WebSocket

### База данных:
- Ваша существующая PostgreSQL
- Автоматические миграции при первом запуске
- Все таблицы создаются автоматически

## 🐛 Решение проблем

### Backend не запускается

**Проверьте логи:**
1. Dashboard → Backend Service → **Logs**
2. Ищите ошибки подключения к базе данных

**Проверьте DATABASE_URL:**
- Должен начинаться с `postgresql://` (не `postgresql+asyncpg://`)
- Backend автоматически преобразует в `postgresql+asyncpg://`

### Frontend не отображается

**Проверьте Build Logs:**
1. Dashboard → Frontend Static Site → **Logs**
2. Убедитесь, что build завершился успешно

**Проверьте Rewrite Rules:**
- Source: `/*`
- Destination: `/index.html`
- Action: Rewrite

### CORS ошибки

**Обновите ALLOWED_ORIGINS:**
1. Backend → Environment → `ALLOWED_ORIGINS`
2. Укажите точный URL frontend (без слеша в конце)
3. Например: `https://rellouse-frontend.onrender.com`

### WebSocket не работает

**Проверьте URL в браузере:**
- Должен быть: `wss://rellouse-backend.onrender.com/ws/chat`
- Render автоматически поддерживает WebSocket

**Проверьте CORS:**
- WebSocket использует те же CORS настройки

### База данных недоступна

**Проверьте статус:**
1. Dashboard → PostgreSQL → **Status**
2. Должен быть: "Available"

**Проверьте подключение:**
```bash
# Используйте psql для проверки
psql postgresql://niomero:MOXUCpO1XEu0gX3eb9jRn2rBrTwSwv0g@dpg-d9794s6q1p3s738kbbqg-a.oregon-postgres.render.com/ghost_db_vh94
```

## 💰 Стоимость (Free план)

### Что бесплатно:
- ✅ PostgreSQL: 1 GB storage (90 дней)
- ✅ Backend: 512 MB RAM, 750 часов/месяц
- ✅ Frontend: 100 GB bandwidth/месяц
- ✅ SSL сертификаты
- ✅ Автоматические деплои из GitHub

### Ограничения:
- ⚠️ Backend засыпает после 15 мин
- ⚠️ PostgreSQL удаляется через 90 дней
- ⚠️ 750 часов/месяц (достаточно для 1 сервиса 24/7)

### Когда нужен платный план:
- Нужно больше 750 часов/месяц
- Нужно несколько Web Services
- Нужна постоянная база данных
- Нужно больше RAM/CPU

## 🔒 Безопасность

### После первого деплоя:

1. **Смените пароль Owner:**
   - Логин: `Rellouse`
   - Пароль: `none`
   - ⚠️ **КРИТИЧНО:** Смените немедленно!

2. **Проверьте переменные окружения:**
   - `SECRET_KEY` и `ENCRYPTION_KEY` должны быть уникальными
   - Не используйте одинаковые значения

3. **Настройте CORS правильно:**
   - Укажите только ваш frontend домен
   - Не используйте `*` в продакшене

4. **Регулярно обновляйте зависимости:**
   ```bash
   cd backend && pip list --outdated
   cd frontend && npm outdated
   ```

## 📝 Чеклист деплоя

- [x] База данных уже создана
- [ ] Создан Backend Web Service (Free план)
- [ ] Добавлены все Environment Variables
- [ ] Создан Frontend Static Site
- [ ] Настроены Rewrite Rules для frontend
- [ ] Обновлен `ALLOWED_ORIGINS` в backend
- [ ] Обновлен `VITE_API_URL` в frontend
- [ ] Проверена работа регистрации/логина
- [ ] Проверена работа WebSocket чата
- [ ] Изменен пароль Owner аккаунта
- [ ] (Опционально) Настроен UptimeRobot

## 🎉 Готово!

Ваш Rellouse Messenger теперь доступен:
- **Frontend:** `https://rellouse-frontend.onrender.com`
- **Backend API:** `https://rellouse-backend.onrender.com`
- **Health Check:** `https://rellouse-backend.onrender.com/health`

## 📞 Поддержка

- Render Docs: https://render.com/docs/free
- Render Community: https://community.render.com
- GitHub: https://github.com/Niomero/Rellouse
- Issues: https://github.com/Niomero/Rellouse/issues

---

## 🔄 Альтернативные варианты (если Render не подходит)

### Railway.app ($5 кредитов/месяц)

1. Зарегистрируйтесь на https://railway.app
2. New Project → Deploy from GitHub
3. Выберите `Niomero/Rellouse`
4. Railway автоматически определит Python и Node.js
5. Добавьте PostgreSQL через Railway Dashboard
6. Настройте переменные окружения

### Vercel (только Frontend)

1. Зарегистрируйтесь на https://vercel.com
2. Import Project → GitHub → `Niomero/Rellouse`
3. Root Directory: `frontend`
4. Build Command: `npm run build`
5. Output Directory: `dist`
6. Environment Variable: `VITE_API_URL`

### Локальный Docker

```bash
# Создайте docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://niomero:MOXUCpO1XEu0gX3eb9jRn2rBrTwSwv0g@dpg-d9794s6q1p3s738kbbqg-a.oregon-postgres.render.com/ghost_db_vh94

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      VITE_API_URL: http://localhost:8000
```

Запуск:
```bash
docker-compose up -d
```