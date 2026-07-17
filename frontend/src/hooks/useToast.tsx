import { create } from 'zustand'
import { Toast, ToastType } from '../components/ui/Toast'

interface ToastStore {
  toasts: Toast[]
  addToast: (type: ToastType, message: string, duration?: number) => void
  removeToast: (id: string) => void
  success: (message: string, duration?: number) => void
  error: (message: string, duration?: number) => void
  info: (message: string, duration?: number) => void
  warning: (message: string, duration?: number) => void
}

export const useToast = create<ToastStore>((set) => ({
  toasts: [],
  
  addToast: (type, message, duration = 5000) => {
    const id = Math.random().toString(36).substring(2, 9)
    const toast: Toast = { id, type, message, duration }
    
    set((state) => ({
      toasts: [...state.toasts, toast]
    }))
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id)
    }))
  },
  
  success: (message, duration) => {
    useToast.getState().addToast('success', message, duration)
  },
  
  error: (message, duration) => {
    useToast.getState().addToast('error', message, duration)
  },
  
  info: (message, duration) => {
    useToast.getState().addToast('info', message, duration)
  },
  
  warning: (message, duration) => {
    useToast.getState().addToast('warning', message, duration)
  },
}))
