# 🚀 Rellouse Messenger

A modern, beautiful, and secure messaging platform built with FastAPI and React, featuring a stunning Liquid Glass design inspired by Telegram Messenger.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.2+-blue.svg)

## ✨ Features

### 🎨 Modern UI/UX
- **Liquid Glass Design System** - Stunning glassmorphism effects with blur, transparency, and smooth animations
- **Dark/Light Mode** - Seamless theme switching with system preference detection
- **Responsive Design** - Perfect experience on desktop, tablet, and mobile devices
- **Smooth Animations** - Framer Motion powered transitions and micro-interactions
- **Toast Notifications** - Beautiful, non-intrusive notifications for user feedback

### 💬 Messaging
- **Real-time Chat** - Direct messaging between users
- **Rich Media Support** - Send images with preview before sending
- **Emoji Picker** - Full emoji support with search functionality
- **Message History** - Persistent message storage with pagination
- **Read Receipts** - Track message delivery and read status
- **User Profiles** - Detailed user profiles with avatars, bio, and status

### 📢 Channels
- **Public Channels** - Create discoverable channels with custom usernames
- **Private Channels** - Invite-only channels with secure invite links
- **Channel Posts** - Publish text and image posts to channel members
- **Member Management** - View members, assign roles (Owner, Admin, Member)
- **Rich Channel Info** - Custom avatars, descriptions, and member counts

### 🔐 Security & Authentication
- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - Bcrypt password encryption
- **Session Management** - Secure session handling with refresh tokens
- **Rate Limiting** - Protection against brute force attacks
- **Security Headers** - Comprehensive security headers on all responses

### 👤 User Features
- **User Search** - Find users by username, @username, or display name
- **User Profiles** - View detailed profiles with online status
- **Verification System** - Request and manage verified badges
- **Multiple Usernames** - Support for up to 4 additional usernames
- **Avatar Upload** - Custom profile pictures with automatic optimization
- **Online Status** - Real-time online/offline indicators

### 🤖 System Bots
- **@Verify Bot** - Official verification bot for badge requests
- **Bot Profiles** - Bots appear as full users with profiles and avatars
- **Bot Integration** - Easy integration for future automated services

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── database.py            # Database connection & session
├── models.py              # SQLAlchemy models
├── auth.py                # Authentication logic
├── security.py            # Security utilities
├── init_system.py         # System initialization
├── routers/               # API endpoints
│   ├── auth_router.py     # Authentication endpoints
│   ├── user_router.py     # User management
│   ├── message_router.py  # Messaging endpoints
│   ├── channel_router.py  # Channel management
│   ├── upload_router.py   # File upload handling
│   ├── bot_router.py      # Bot interactions
│   ├── verification_router.py  # Verification system
│   └── websocket_router.py     # WebSocket connections
└── uploads/               # User uploaded files
    ├── images/
    ├── videos/
    ├── audio/
    ├── files/
    └── thumbnails/
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   ├── components/        # Reusable components
│   │   ├── ui/            # UI primitives
│   │   │   ├── Toast.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Avatar.tsx
│   │   ├── Layout.tsx
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── EmojiPicker.tsx
│   │   ├── ImageUpload.tsx
│   │   └── ProtectedRoute.tsx
│   ├── pages/             # Page components
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── ChatPage.tsx
│   │   ├── SearchPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── ChannelPage.tsx
│   │   ├── CreateChannelPage.tsx
│   │   ├── SettingsPage.tsx
│   │   └── VerificationPage.tsx
│   ├── services/          # API services
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/             # State management (Zustand)
│   │   ├── authStore.ts
│   │   └── themeStore.ts
│   ├── hooks/             # Custom React hooks
│   │   └── useToast.tsx
│   ├── utils/             # Utility functions
│   │   ├── cn.ts
│   │   └── toast.tsx
│   └── styles/            # Styling
│       ├── liquid-glass.css
│       └── design-system.css
└── public/                # Static assets
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- npm or yarn

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rellouse-messenger.git
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
Create a `.env` file in the backend directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/rellouse_db

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Owner Account (First Run)
OWNER_USERNAME=admin
OWNER_PASSWORD=your-secure-password

# Application
APP_NAME=Rellouse Messenger
APP_VERSION=2.0.0
DEBUG=False
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

5. **Initialize database**
```bash
# Create database
createdb rellouse_db

# Run migrations (if using Alembic)
alembic upgrade head
```

6. **Start the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/api/docs` (if DEBUG=True)

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Configure environment**
Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

4. **Start development server**
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:5173`

## 📖 Usage Guide

### First Time Setup

1. **Access the application** at `http://localhost:5173`
2. **Register a new account** or login with owner credentials
3. **Complete your profile** with avatar and bio
4. **Start messaging** by searching for users

### Creating a Channel

1. Navigate to **Channels** section
2. Click **Create Channel**
3. Choose channel type:
   - **Public**: Anyone can find and join (requires unique @username)
   - **Private**: Join by invite link only
4. Fill in channel details:
   - Name (required)
   - Description (optional)
   - Avatar (optional)
5. Click **Create Channel**

### Sending Messages

1. **Search for a user** in the search page
2. Click on the user to view their profile
3. Click **Send Message** button
4. Type your message and press Enter or click Send
5. **Add images** by clicking the image icon
6. **Add emojis** by clicking the emoji icon

### Channel Management

**For Channel Owners/Admins:**
- Post text and images to the channel
- View and manage members
- Update channel information
- Generate invite links (private channels)

**For Channel Members:**
- View channel posts
- See member list
- Leave channel

### User Verification

1. Navigate to **Verification** page
2. Fill out the verification form:
   - Description of why you should be verified
   - Social media links
   - Website links
   - Additional materials
3. Submit request
4. Wait for admin review
5. Receive notification when approved/rejected

## 🎨 Design System

### Liquid Glass Components

The application uses a custom Liquid Glass design system with:

- **Glass Effects**: Semi-transparent backgrounds with backdrop blur
- **Smooth Shadows**: Multi-layered shadows for depth
- **Rounded Corners**: Consistent border radius scale
- **Gradient Accents**: Subtle gradients for visual interest
- **Micro-interactions**: Hover, press, and focus states
- **Fluid Animations**: Smooth transitions using Framer Motion

### Color Palette

**Light Mode:**
- Primary: Blue (#2196F3)
- Background: Neutral 50 (#FAFAFA)
- Surface: White with transparency
- Text: Neutral 900 (#212121)

**Dark Mode:**
- Primary: Blue (#2196F3)
- Background: Neutral 900 (#0F0F0F)
- Surface: Neutral 800 with transparency
- Text: Neutral 100 (#E5E5E5)

### Typography

- **Font Family**: System fonts (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Font Sizes**: 12px - 32px scale
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users/search` - Search users
- `GET /api/users/{user_id}` - Get user profile
- `GET /api/users/username/{username}` - Get user by username
- `PUT /api/users/profile` - Update own profile
- `GET /api/users/online/list` - Get online users

### Messages
- `GET /api/messages` - Get message history
- `POST /api/messages` - Send message
- `PUT /api/messages/{message_id}` - Edit message
- `DELETE /api/messages/{message_id}` - Delete message

### Channels
- `GET /api/channels` - Get user's channels
- `POST /api/channels` - Create channel
- `GET /api/channels/{channel_id}` - Get channel details
- `PUT /api/channels/{channel_id}` - Update channel
- `POST /api/channels/{channel_id}/join` - Join channel
- `POST /api/channels/{channel_id}/leave` - Leave channel
- `GET /api/channels/{channel_id}/members` - Get members
- `GET /api/channels/{channel_id}/posts` - Get posts
- `POST /api/channels/{channel_id}/posts` - Create post

### Uploads
- `POST /api/upload/image` - Upload image
- `POST /api/upload/avatar` - Upload avatar
- `POST /api/upload/video` - Upload video
- `POST /api/upload/audio` - Upload audio
- `POST /api/upload/file` - Upload file

### Verification
- `POST /api/verification/request` - Submit verification request
- `GET /api/verification/requests` - Get all requests (admin)
- `PUT /api/verification/requests/{request_id}` - Review request (admin)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

## 📦 Deployment

### Backend Deployment (Production)

1. **Set production environment variables**
2. **Use production database**
3. **Disable debug mode** (`DEBUG=False`)
4. **Use production WSGI server** (Gunicorn + Uvicorn workers)
5. **Set up reverse proxy** (Nginx)
6. **Enable HTTPS** with SSL certificates
7. **Configure CORS** for production domain

### Frontend Deployment

1. **Build production bundle**
```bash
npm run build
# or
yarn build
```

2. **Deploy to static hosting** (Vercel, Netlify, etc.)
3. **Configure environment variables** for production API URL
4. **Set up CDN** for optimal performance

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Design inspired by Telegram Messenger
- Built with FastAPI and React
- UI components powered by Tailwind CSS and Framer Motion
- Icons from Lucide React

## 📞 Support

For support, email support@rellouse.com or open an issue on GitHub.

## 🗺️ Roadmap

- [ ] Voice messages
- [ ] Video messages
- [ ] File sharing
- [ ] Group chats
- [ ] End-to-end encryption
- [ ] Mobile applications (iOS/Android)
- [ ] Desktop applications (Electron)
- [ ] Message reactions
- [ ] Message forwarding
- [ ] Stickers and GIFs
- [ ] Voice/Video calls

---

Made with ❤️ by the Rellouse Team
