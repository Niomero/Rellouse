# Деплой Rellouse Messenger на Render

Полное руководство по развертыванию проекта на Render.com

## 📋 Предварительные требования

1. Аккаунт на [Render.com](https://render.com)
2. GitHub репозиторий с проектом
3. (Опционально) S3-совместимое хранилище для файлов

## 🚀 Быстрый деплой через Blueprint

### Шаг 1: Подготовка репозитория

1. **Создайте GitHub репозиторий**
```bash
cd rellouse-messenger
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/rellouse-messenger.git
git push -u origin main
```

2. **Убедитесь, что все файлы на месте:**
   - `render.yaml` в корне проекта
   - `backend/requirements.txt`
   - `frontend/package.json`

### Шаг 2: Деплой через Render Dashboard

1. **Войдите в Render Dashboard**
   - Перейдите на https://dashboard.render.com

2. **Создайте новый Blueprint**
   - Нажмите "New" → "Blueprint"
   - Подключите ваш GitHub репозиторий
   - Render автоматически обнаружит `render.yaml`

3. **Настройте переменные окружения**
   
   Render автоматически создаст большинство переменных, но вам нужно добавить:
   
   **Для S3 Storage (если используете):**
   - `S3_ENDPOINT_URL` - URL вашего S3 хранилища
   - `S3_ACCESS_KEY_ID` - Access Key
   - `S3_SECRET_ACCESS_KEY` - Secret Key
   - `S3_BUCKET_NAME` - Имя bucket

4. **Запустите деплой**
   - Нажмите "Apply"
   - Render создаст все сервисы автоматически

### Шаг 3: Обновите CORS настройки

После деплоя обновите переменную `ALLOWED_ORIGINS` в backend:

```
ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
```

## 🔧 Ручная настройка (альтернатива Blueprint)

### 1. Создание PostgreSQL базы данных

1. Dashboard → "New" → "PostgreSQL"
2. Имя: `rellouse-db`
3. Database: `rellouse_db`
4. User: `rellouse_user`
5. Region: выберите ближайший
6. Plan: Starter (бесплатный)
7. Создайте базу данных

### 2. Создание Backend сервиса

1. Dashboard → "New" → "Web Service"
2. Подключите GitHub репозиторий
3. Настройки:
   - **Name**: `rellouse-backend`
   - **Region**: тот же, что и база данных
   - **Branch**: `main`
   - **Root Directory**: оставьте пустым
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Starter

4. **Environment Variables** (добавьте все из списка ниже)

### 3. Создание Frontend сервиса

1. Dashboard → "New" → "Static Site"
2. Подключите тот же GitHub репозиторий
3. Настройки:
   - **Name**: `rellouse-frontend`
   - **Branch**: `main`
   - **Root Directory**: оставьте пустым
   - **Build Command**: 
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory**: `frontend/dist`

4. **Environment Variables**:
   - `VITE_API_URL` = `https://rellouse-backend.onrender.com`

5. **Rewrite Rules** (в настройках Static Site):
   - Source: `/*`
   - Destination: `/index.html`
   - Action: `Rewrite`

## 🔐 Переменные окружения для Backend

### Обязательные (автоматически)
```env
DATABASE_URL=<автоматически из PostgreSQL>
SECRET_KEY=<автоматически генерируется>
ENCRYPTION_KEY=<автоматически генерируется>
```

### Обязательные (настроить вручную)
```env
ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
```

### Опциональные (S3 Storage)
```env
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY_ID=your-key
S3_SECRET_ACCESS_KEY=your-secret
S3_BUCKET_NAME=rellouse-storage
S3_REGION=us-east-1
```

### Настройки приложения
```env
APP_NAME=Rellouse Messenger
APP_VERSION=1.0.0
DEBUG=false
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS_PER_USER=5
OWNER_USERNAME=Rellouse
OWNER_PASSWORD=none
OWNER_ADDITIONAL_USERNAMES=admin,user,test,none
```

## 🌐 Настройка кастомного домена (опционально)

### Для Frontend:
1. Перейдите в настройки Static Site
2. Settings → Custom Domain
3. Добавьте ваш домен (например, `rellouse.org`)
4. Настройте DNS записи как указано Render

### Для Backend:
1. Перейдите в настройки Web Service
2. Settings → Custom Domain
3. Добавьте поддомен (например, `api.rellouse.org`)
4. Обновите `ALLOWED_ORIGINS` и `VITE_API_URL`

## 📊 Мониторинг и логи

### Просмотр логов:
1. Откройте нужный сервис в Dashboard
2. Перейдите на вкладку "Logs"
3. Логи обновляются в реальном времени

### Метрики:
1. Вкладка "Metrics" показывает:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

## 🔄 Автоматические деплои

Render автоматически деплоит при push в main ветку:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render обнаружит изменения и автоматически пересоберет сервисы.

## 🐛 Решение проблем

### Backend не запускается

1. **Проверьте логи**:
   - Dashboard → Backend Service → Logs

2. **Проверьте переменные окружения**:
   - Все обязательные переменные установлены?
   - `DATABASE_URL` корректный?

3. **Проверьте Build Command**:
   ```bash
   cd backend && pip install -r requirements.txt
   ```

### Frontend не отображается

1. **Проверьте Build Command**:
   ```bash
   cd frontend && npm install && npm run build
   ```

2. **Проверьте Publish Directory**:
   - Должно быть: `frontend/dist`

3. **Проверьте Rewrite Rules**:
   - Source: `/*`
   - Destination: `/index.html`

### CORS ошибки

1. **Обновите `ALLOWED_ORIGINS`** в backend:
   ```
   ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
   ```

2. **Перезапустите backend сервис**

### WebSocket не работает

1. **Проверьте URL** в frontend:
   - Должен быть: `wss://your-backend-name.onrender.com/ws/chat`

2. **Render автоматически поддерживает WebSocket** на всех планах

### База данных недоступна

1. **Проверьте статус PostgreSQL**:
   - Dashboard → PostgreSQL → Status

2. **Проверьте `DATABASE_URL`**:
   - Должен начинаться с `postgresql+asyncpg://`

## 💰 Стоимость

### Бесплатный план (Starter):
- ✅ PostgreSQL: 1 GB storage
- ✅ Backend: 512 MB RAM, засыпает после 15 мин неактивности
- ✅ Frontend: 100 GB bandwidth/месяц
- ✅ Автоматические деплои
- ✅ SSL сертификаты

### Платные планы:
- **Starter Plus** ($7/мес): без засыпания, больше ресурсов
- **Standard** ($25/мес): 2 GB RAM, приоритетная поддержка
- **Pro** ($85/мес): 4 GB RAM, расширенные метрики

## 🔒 Безопасность

### После первого деплоя:

1. **Смените пароль Owner аккаунта**:
   - Логин: `Rellouse`
   - Пароль по умолчанию: `none`
   - ⚠️ Смените немедленно!

2. **Настройте S3 Storage**:
   - Для загрузки аватаров
   - Используйте AWS S3, Cloudflare R2, или MinIO

3. **Включите 2FA** на Render аккаунте

4. **Регулярно обновляйте зависимости**:
   ```bash
   pip list --outdated
   npm outdated
   ```

## 📝 Чеклист деплоя

- [ ] Создан GitHub репозиторий
- [ ] Загружен код проекта
- [ ] Создана PostgreSQL база данных на Render
- [ ] Создан Backend Web Service
- [ ] Создан Frontend Static Site
- [ ] Настроены все переменные окружения
- [ ] Настроены Rewrite Rules для frontend
- [ ] Обновлен `ALLOWED_ORIGINS` в backend
- [ ] Проверена работа регистрации/логина
- [ ] Проверена работа WebSocket
- [ ] Изменен пароль Owner аккаунта
- [ ] (Опционально) Настроен кастомный домен
- [ ] (Опционально) Настроен S3 Storage

## 🎉 Готово!

Ваш Rellouse Messenger теперь доступен по адресам:
- Frontend: `https://your-frontend-name.onrender.com`
- Backend API: `https://your-backend-name.onrender.com`
- API Docs: `https://your-backend-name.onrender.com/api/docs` (только в DEBUG режиме)

## 📞 Поддержка

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: создайте issue в вашем репозитории
