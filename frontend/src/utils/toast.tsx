import toast, { Toaster } from 'react-hot-toast';
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

const toastStyles = {
  style: {
    background: 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(20px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    padding: '16px',
    boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)',
  },
  success: {
    icon: <CheckCircle className="w-5 h-5 text-green-500" />,
    style: {
      background: 'rgba(240, 253, 244, 0.9)',
    },
  },
  error: {
    icon: <XCircle className="w-5 h-5 text-red-500" />,
    style: {
      background: 'rgba(254, 242, 242, 0.9)',
    },
  },
  loading: {
    icon: <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />,
  },
};

export const showToast = {
  success: (message: string) => {
    toast.success(message, toastStyles.success);
  },
  error: (message: string) => {
    toast.error(message, toastStyles.error);
  },
  loading: (message: string) => {
    return toast.loading(message, toastStyles.loading);
  },
  info: (message: string) => {
    toast(message, {
      icon: <Info className="w-5 h-5 text-blue-500" />,
      ...toastStyles,
    });
  },
  warning: (message: string) => {
    toast(message, {
      icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
      ...toastStyles,
    });
  },
  dismiss: (toastId: string) => {
    toast.dismiss(toastId);
  },
};

export const ToastContainer = () => (
  <Toaster
    position="top-right"
    toastOptions={{
      duration: 4000,
      ...toastStyles,
    }}
  />
);
