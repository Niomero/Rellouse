# Настройка Cloudflare R2 для Rellouse Messenger

Бесплатное S3-совместимое хранилище для загрузки аватаров

## 🆓 Что такое Cloudflare R2?

- **10 GB хранилища бесплатно** (навсегда)
- **10 миллионов запросов/месяц** бесплатно
- **Без платы за исходящий трафик** (egress)
- S3-совместимый API
- Быстрая глобальная CDN

## 📝 Пошаговая настройка

### Шаг 1: Создайте аккаунт Cloudflare

1. Перейдите на https://dash.cloudflare.com/sign-up
2. Зарегистрируйтесь (email + пароль)
3. Подтвердите email
4. **Не требует карты для бесплатного плана!**

### Шаг 2: Создайте R2 Bucket

1. **Войдите в Cloudflare Dashboard**
   - https://dash.cloudflare.com

2. **Перейдите в R2**
   - Левое меню → **R2**
   - Или: https://dash.cloudflare.com/?to=/:account/r2

3. **Создайте Bucket**
   - Нажмите **"Create bucket"**
   - **Bucket name**: `rellouse-storage` (или любое другое имя)
   - **Location**: Automatic (рекомендуется)
   - Нажмите **"Create bucket"**

### Шаг 3: Создайте API Token

1. **В R2 Dashboard**
   - Нажмите **"Manage R2 API Tokens"**
   - Или перейдите: Settings → API Tokens

2. **Создайте новый токен**
   - Нажмите **"Create API token"**
   - **Token name**: `rellouse-messenger`
   - **Permissions**: 
     - ✅ Object Read & Write
   - **TTL**: Forever (или выберите срок)
   - **Bucket**: `rellouse-storage` (выберите ваш bucket)
   - Нажмите **"Create API Token"**

3. **Сохраните учетные данные**
   
   Вы увидите экран с тремя важными значениями:
   
   ```
   Access Key ID: <ваш_access_key>
   Secret Access Key: <ваш_secret_key>
   Endpoint URL: https://<account_id>.r2.cloudflarestorage.com
   ```
   
   ⚠️ **ВАЖНО:** Сохраните эти данные! Secret Key показывается только один раз!

### Шаг 4: Настройте CORS (опционально, но рекомендуется)

1. **Откройте ваш bucket**
   - R2 → Buckets → `rellouse-storage`

2. **Перейдите в Settings**
   - Вкладка **"Settings"**

3. **Настройте CORS**
   - Найдите секцию **"CORS policy"**
   - Нажмите **"Edit"**
   - Добавьте правило:

```json
[
  {
    "AllowedOrigins": [
      "https://rellouse-frontend.onrender.com",
      "https://rellouse-backend.onrender.com"
    ],
    "AllowedMethods": [
      "GET",
      "PUT",
      "POST",
      "DELETE",
      "HEAD"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "ETag"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

4. **Сохраните**

### Шаг 5: Добавьте переменные в Render

1. **Откройте ваш Backend Service на Render**
   - Dashboard → `rellouse-backend`

2. **Environment → Add Environment Variable**

Добавьте следующие переменные:

```env
S3_ENDPOINT_URL=https://<ваш_account_id>.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=<ваш_access_key_из_шага_3>
S3_SECRET_ACCESS_KEY=<ваш_secret_key_из_шага_3>
S3_BUCKET_NAME=rellouse-storage
S3_REGION=auto
```

**Пример:**
```env
S3_ENDPOINT_URL=https://abc123def456.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=a1b2c3d4e5f6g7h8i9j0
S3_SECRET_ACCESS_KEY=k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
S3_BUCKET_NAME=rellouse-storage
S3_REGION=auto
```

3. **Save Changes**
   - Backend автоматически перезапустится

### Шаг 6: Проверьте работу

1. **Откройте ваш Rellouse Messenger**
   - https://rellouse-frontend.onrender.com

2. **Войдите в аккаунт**

3. **Перейдите в Profile**
   - Нажмите на ваш username в sidebar

4. **Загрузите аватар**
   - Нажмите на иконку камеры
   - Выберите изображение
   - Загрузите

5. **Проверьте в R2**
   - Cloudflare Dashboard → R2 → `rellouse-storage`
   - Вы должны увидеть загруженный файл

## 🔍 Структура файлов в R2

Backend автоматически организует файлы:

```
rellouse-storage/
├── avatars/
│   ├── user_1_<timestamp>.jpg
│   ├── user_2_<timestamp>.png
│   └── ...
└── (другие папки в будущем)
```

## 🔒 Безопасность

### Рекомендации:

1. **Используйте отдельный токен для каждого приложения**
   - Не используйте один токен для всех проектов

2. **Ограничьте права токена**
   - Только Object Read & Write
   - Только для конкретного bucket

3. **Регулярно ротируйте токены**
   - Создавайте новый токен каждые 3-6 месяцев
   - Удаляйте старые токены

4. **Не коммитьте токены в Git**
   - Используйте только Environment Variables
   - Добавьте `.env` в `.gitignore`

5. **Настройте CORS правильно**
   - Указывайте только ваши домены
   - Не используйте `*` в продакшене

## 💰 Лимиты бесплатного плана

### Что включено бесплатно:

- ✅ **10 GB хранилища**
- ✅ **10 миллионов Class A операций/месяц** (PUT, POST, LIST)
- ✅ **10 миллионов Class B операций/месяц** (GET, HEAD)
- ✅ **Безлимитный исходящий трафик** (egress)

### Что будет платно:

- Хранилище > 10 GB: **$0.015/GB/месяц**
- Class A операции > 10M: **$4.50 за миллион**
- Class B операции > 10M: **$0.36 за миллион**

### Для Rellouse Messenger:

**Примерный расчет:**
- 1000 пользователей
- Каждый загружает 1 аватар (500 KB)
- Итого: ~500 MB хранилища
- Операции: ~1000 PUT + ~10000 GET/месяц

**Стоимость: $0** (в пределах бесплатного плана)

## 🐛 Решение проблем

### Ошибка: "Access Denied"

**Причина:** Неправильные учетные данные

**Решение:**
1. Проверьте `S3_ACCESS_KEY_ID` и `S3_SECRET_ACCESS_KEY`
2. Убедитесь, что токен имеет права на bucket
3. Проверьте, что bucket name правильный

### Ошибка: "Bucket not found"

**Причина:** Неправильное имя bucket или endpoint

**Решение:**
1. Проверьте `S3_BUCKET_NAME` (должно совпадать с именем в R2)
2. Проверьте `S3_ENDPOINT_URL` (должен содержать ваш account ID)

### Ошибка: "CORS policy"

**Причина:** CORS не настроен или настроен неправильно

**Решение:**
1. Добавьте CORS правило в R2 bucket (см. Шаг 4)
2. Укажите правильные домены в `AllowedOrigins`
3. Перезапустите backend

### Файлы не загружаются

**Проверьте:**
1. Backend логи на Render
2. Browser Console (F12) на ошибки
3. Переменные окружения в Render
4. Права токена в Cloudflare

## 📊 Мониторинг использования

### Просмотр статистики:

1. **Cloudflare Dashboard → R2**
2. **Выберите ваш bucket**
3. **Вкладка "Metrics"**

Вы увидите:
- Использование хранилища
- Количество операций
- Исходящий трафик

## 🔄 Альтернативы Cloudflare R2

Если R2 не подходит:

### 1. Backblaze B2
- **10 GB бесплатно**
- **1 GB исходящего трафика/день**
- S3-совместимый
- https://www.backblaze.com/b2/cloud-storage.html

### 2. AWS S3
- **5 GB бесплатно** (первый год)
- **20,000 GET запросов**
- **2,000 PUT запросов**
- https://aws.amazon.com/s3/pricing/

### 3. MinIO (самохостинг)
- **Полностью бесплатно**
- Требует свой сервер
- S3-совместимый
- https://min.io/

## 📝 Чеклист настройки

- [ ] Создан аккаунт Cloudflare
- [ ] Создан R2 bucket (`rellouse-storage`)
- [ ] Создан API Token с правами Object Read & Write
- [ ] Сохранены Access Key ID и Secret Access Key
- [ ] Настроен CORS для bucket
- [ ] Добавлены переменные окружения в Render:
  - [ ] `S3_ENDPOINT_URL`
  - [ ] `S3_ACCESS_KEY_ID`
  - [ ] `S3_SECRET_ACCESS_KEY`
  - [ ] `S3_BUCKET_NAME`
  - [ ] `S3_REGION`
- [ ] Backend перезапущен
- [ ] Проверена загрузка аватара
- [ ] Файл появился в R2 bucket

## 🎉 Готово!

Теперь ваш Rellouse Messenger поддерживает загрузку аватаров через Cloudflare R2!

**Что работает:**
- ✅ Загрузка аватаров (PNG, JPG, GIF, WEBP)
- ✅ Автоматическое изменение размера
- ✅ Безопасное хранение в R2
- ✅ Быстрая доставка через CDN
- ✅ Бесплатно до 10 GB

## 📞 Поддержка

- Cloudflare Docs: https://developers.cloudflare.com/r2/
- Cloudflare Community: https://community.cloudflare.com/
- GitHub Issues: https://github.com/Niomero/Rellouse/issues
