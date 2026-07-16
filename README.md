# Rellouse Messenger

A modern, secure messaging platform with end-to-end encryption, built with FastAPI and React.

## 🚀 Features

- **Secure Authentication**: Registration without phone/email, only login and password
- **Username System**: Unique usernames starting with @ (4-16 characters)
- **User Roles**: User, Verified, Administrator, Owner with distinct badges
- **End-to-End Encryption**: All messages are encrypted using modern cryptography
- **Real-time Messaging**: WebSocket-based instant messaging
- **Bot System**: Built-in @Verify bot for verification requests
- **Verification System**: Users can request verified status
- **Modern UI**: Clean, responsive design with light/dark themes
- **Security First**: Rate limiting, CSRF protection, security logging

## 📋 System Requirements

### Backend
- Python 3.10+
- PostgreSQL 14+
- S3-compatible storage (AWS S3, MinIO, etc.)

### Frontend
- Node.js 18+
- npm or yarn

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
```bash
cd rellouse-messenger/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
# Create PostgreSQL database
createdb rellouse_db

# Run migrations (if using Alembic)
alembic upgrade head
```

6. **Start the server**
```bash
python main.py
# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd rellouse-messenger/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm run dev
```

4. **Build for production**
```bash
npm run build
```

## 🔧 Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rellouse_db

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# S3 Storage
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=rellouse-storage

# Application
ALLOWED_ORIGINS=https://rellouse.org,http://localhost:3000
```

### Frontend (vite.config.ts)

The frontend is configured to proxy API requests to the backend:
- API: `http://localhost:8000/api`
- WebSocket: `ws://localhost:8000/ws`

## 👤 Default Owner Account

On first run, the system automatically creates:
- **Username**: @Rellouse
- **Password**: none
- **Role**: Owner
- **Additional Usernames**: @admin, @user, @test, @none

**⚠️ IMPORTANT**: Change the default password immediately after first login!

## 🤖 Built-in Bots

### @Verify Bot (ID: ~1)
- Handles verification requests
- Sends confirmation messages
- Notifies administrators of new requests

## 📱 User Roles

| Role | Username Color | Badge | Permissions |
|------|---------------|-------|-------------|
| User | White | None | Basic messaging |
| Verified | Blue | ✓ | Verified badge |
| Administrator | Red | ✓ | Review verifications, manage users |
| Owner | Black | ✓ | Full system access, create bots |

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Access and refresh tokens
- **End-to-End Encryption**: Fernet symmetric encryption
- **Rate Limiting**: 60 requests/minute, 1000/hour
- **HTTPS/TLS**: Required in production
- **Security Headers**: XSS, CSRF, CSP protection
- **Security Logging**: All authentication events logged

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/search` - Search users
- `GET /api/users/{username}` - Get user profile
- `PUT /api/users/profile` - Update profile
- `PUT /api/users/username` - Update username

### Messages
- `POST /api/messages/send` - Send message
- `GET /api/messages/{message_id}` - Get message
- `GET /api/messages/conversation/{user_id}` - Get conversation
- `GET /api/messages/conversations/list` - List conversations

### Verification
- `POST /api/verification/submit` - Submit verification request
- `GET /api/verification/my-requests` - Get user's requests
- `GET /api/verification/pending` - Get pending requests (Admin)
- `POST /api/verification/review` - Review request (Admin)

### WebSocket
- `WS /ws/chat?token={access_token}` - Real-time messaging

## 🎨 Frontend Structure

```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/          # Page components
│   ├── store/          # Zustand state management
│   ├── services/       # API services
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   └── types/          # TypeScript types
```

## 🚀 Deployment

### Backend (Production)

1. **Use production WSGI server**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Set up reverse proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name rellouse.org;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

3. **Enable HTTPS with Let's Encrypt**
```bash
certbot --nginx -d rellouse.org
```

### Frontend (Production)

1. **Build the application**
```bash
npm run build
```

2. **Serve with Nginx**
```nginx
server {
    listen 80;
    server_name rellouse.org;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a private project. Contact the owner for contribution guidelines.

## 📧 Support

For support, contact: support@rellouse.org

## 🔄 Version

Current version: 1.0.0

---

Built with ❤️ using FastAPI, React, and modern web technologies.
