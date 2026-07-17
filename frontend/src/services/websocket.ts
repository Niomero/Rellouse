import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(token: string) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

    this.socket = io(wsUrl, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: this.reconnectDelay,
      reconnectionAttempts: this.maxReconnectAttempts,
    });

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on(event: string, callback: (...args: any[]) => void) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event: string, callback?: (...args: any[]) => void) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }

  // Message events
  onNewMessage(callback: (message: any) => void) {
    this.on('new_message', callback);
  }

  onTyping(callback: (data: { userId: number; isTyping: boolean }) => void) {
    this.on('typing_indicator', callback);
  }

  onReadReceipt(callback: (data: { messageId: number; readerId: number }) => void) {
    this.on('read_receipt', callback);
  }

  onStatusChange(callback: (data: { userId: number; status: string }) => void) {
    this.on('status_change', callback);
  }

  // Send events
  sendTyping(recipientId: number, isTyping: boolean) {
    this.emit('typing', { recipient_id: recipientId, is_typing: isTyping });
  }

  markAsRead(messageId: number) {
    this.emit('read', { message_id: messageId });
  }

  sendHeartbeat() {
    this.emit('ping', {});
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const wsService = new WebSocketService();
