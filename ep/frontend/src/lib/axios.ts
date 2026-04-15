import axios from 'axios';

const isTauriRuntime = (): boolean => {
  return typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);
};

const getApiBaseUrl = () => {
  // Use the local sidecar API when running inside Tauri.
  if (isTauriRuntime()) {
    return 'http://127.0.0.1:8000';
  }

  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  const hostname = window.location.hostname;
  if (hostname === 'tauri.localhost') {
    return 'http://127.0.0.1:8000';
  }
  if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:8001`;
  }

  return 'http://localhost:8001';
};

const API_BASE_URL = getApiBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const data = error.response?.data;
    const message =
      (typeof data === 'string' ? data : undefined) ||
      data?.detail ||
      data?.message ||
      data?.error ||
      error.message ||
      'Request failed';
    console.error('API Error:', message);
    return Promise.reject(new Error(message));
  }
);
