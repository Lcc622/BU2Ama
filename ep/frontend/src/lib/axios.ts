/**
 * Axios 配置
 */
import axios from 'axios';

const isTauriRuntime = (): boolean => {
  return typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);
};

// 动态获取 API 地址：如果通过 IP 访问前端，则后端也用相同 IP
const getApiBaseUrl = () => {
  // Tauri 桌面端固定走本机 sidecar。
  if (isTauriRuntime()) {
    return 'http://127.0.0.1:8000';
  }

  // 优先使用环境变量
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 如果是通过 IP 访问（非 localhost），则后端也用相同 IP
  // EP 前端 5173 → 后端 8001
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

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 统一错误处理：兼容字符串、detail/message/error 三种结构
    const data = error.response?.data;
    const message =
      (typeof data === 'string' ? data : undefined) ||
      data?.detail ||
      data?.message ||
      data?.error ||
      error.message ||
      '请求失败';
    console.error('API Error:', message);
    return Promise.reject(new Error(message));
  }
);
