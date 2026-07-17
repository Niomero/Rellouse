import axios, { AxiosInstance, AxiosError } from 'axios';
import { showToast } from '../utils/toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const response = await axios.post(`${API_URL}/api/auth/refresh`, {
                refresh_token: refreshToken,
              });
              
              const { access_token } = response.data;
              localStorage.setItem('access_token', access_token);
              
              // Retry original request
              if (error.config) {
                error.config.headers.Authorization = `Bearer ${access_token}`;
                return this.api.request(error.config);
              }
            } catch (refreshError) {
              // Refresh failed, logout
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              window.location.href = '/login';
            }
          } else {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(login: string, password: string) {
    const response = await this.api.post('/api/auth/login', { login, password });
    return response.data;
  }

  async register(data: { login: string; password: string; username: string }) {
    const response = await this.api.post('/api/auth/register', data);
    return response.data;
  }

  async logout() {
    await this.api.post('/api/auth/logout');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Users
  async searchUsers(query: string, limit = 20) {
    const response = await this.api.get('/api/users/search', {
      params: { query, limit },
    });
    return response.data;
  }

  async getUserProfile(userId: number) {
    const response = await this.api.get(`/api/users/${userId}`);
    return response.data;
  }

  async getUserByUsername(username: string) {
    const response = await this.api.get(`/api/users/username/${username}`);
    return response.data;
  }

  async updateProfile(data: {
    display_name?: string;
    bio?: string;
    avatar_url?: string;
  }) {
    const response = await this.api.put('/api/users/profile', data);
    return response.data;
  }

  async getOnlineUsers() {
    const response = await this.api.get('/api/users/online/list');
    return response.data;
  }

  // Messages
  async sendMessage(recipientId: number, content: string, attachmentUrls?: string[]) {
    const response = await this.api.post('/api/messages/send', {
      recipient_id: recipientId,
      content,
      attachment_urls: attachmentUrls,
    });
    return response.data;
  }

  async getConversation(userId: number, limit = 50, offset = 0) {
    const response = await this.api.get(`/api/messages/conversation/${userId}`, {
      params: { limit, offset },
    });
    return response.data;
  }

  async getConversations() {
    const response = await this.api.get('/api/messages/conversations');
    return response.data;
  }

  async markAsRead(messageId: number) {
    const response = await this.api.put(`/api/messages/${messageId}/read`);
    return response.data;
  }

  async getUnreadCount() {
    const response = await this.api.get('/api/messages/unread/count');
    return response.data;
  }

  async uploadImage(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.api.post('/api/messages/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Channels
  async createChannel(data: {
    name: string;
    description?: string;
    avatar_url?: string;
    channel_type: 'public' | 'private';
    username?: string;
  }) {
    const response = await this.api.post('/api/channels/create', data);
    return response.data;
  }

  async getChannel(channelId: number) {
    const response = await this.api.get(`/api/channels/${channelId}`);
    return response.data;
  }

  async updateChannel(channelId: number, data: {
    name?: string;
    description?: string;
    avatar_url?: string;
  }) {
    const response = await this.api.put(`/api/channels/${channelId}`, data);
    return response.data;
  }

  async joinChannel(channelId: number, inviteCode?: string) {
    const response = await this.api.post(`/api/channels/${channelId}/join`, {
      invite_code: inviteCode,
    });
    return response.data;
  }

  async leaveChannel(channelId: number) {
    const response = await this.api.post(`/api/channels/${channelId}/leave`);
    return response.data;
  }

  async createPost(channelId: number, content: string, attachmentUrls?: string[]) {
    const response = await this.api.post(`/api/channels/${channelId}/posts`, {
      content,
      attachment_urls: attachmentUrls,
    });
    return response.data;
  }

  async getChannelPosts(channelId: number, limit = 50, offset = 0) {
    const response = await this.api.get(`/api/channels/${channelId}/posts`, {
      params: { limit, offset },
    });
    return response.data;
  }

  async getChannelMembers(channelId: number) {
    const response = await this.api.get(`/api/channels/${channelId}/members`);
    return response.data;
  }

  async getMyChannels() {
    const response = await this.api.get('/api/channels/list/my');
    return response.data;
  }

  // Verification
  async submitVerificationRequest(data: {
    description: string;
    telegram_links?: string[];
    social_links?: string[];
    website_links?: string[];
    additional_materials?: string;
  }) {
    const response = await this.api.post('/api/verification/submit', data);
    return response.data;
  }

  async getVerificationStatus() {
    const response = await this.api.get('/api/verification/status');
    return response.data;
  }
}

export const api = new ApiService();
