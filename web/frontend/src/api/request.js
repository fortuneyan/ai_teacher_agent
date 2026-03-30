import axios from "axios";
import { ElMessage } from "element-plus";

const BASE_URL = "/api/v1";

const request = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  maxRedirects: 0, // 禁用自动重定向，手动处理
});

// 请求拦截器 - 注入 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      const authHeader = `Bearer ${token}`;
      // 使用 set 方法设置 header，确保能发送到后端
      config.headers["Authorization"] = authHeader;
      config.headers.set("Authorization", authHeader);
      console.log("Set Authorization header:", config.headers.Authorization);
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器 - 统一错误处理
request.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 处理 307/308 重定向，手动重试
    if (error.response?.status === 307 || error.response?.status === 308) {
      const redirectLocation = error.response.headers.location;
      if (redirectLocation) {
        // 直接使用新的 URL 重新请求（axios 会自动应用 baseURL）
        const newUrl = redirectLocation.replace(BASE_URL, "");
        // 保持原来的请求方法
        const method = error.config.method || "get";
        return request[method](newUrl);
      }
    }

    const status = error.response?.status;
    const message = error.response?.data?.detail || error.message || "请求失败";

    if (status === 401) {
      // localStorage.removeItem("token");
      // localStorage.removeItem("user");
      // window.location.href = "/login";
      return Promise.reject(error);
    }

    if (status === 403) {
      ElMessage.error("没有权限执行此操作");
    } else if (status === 404) {
      ElMessage.error("资源不存在");
    } else if (status === 422) {
      ElMessage.error("请求参数错误：" + message);
    } else if (status >= 500) {
      ElMessage.error("服务器错误，请稍后重试");
    } else {
      ElMessage.error(message);
    }

    return Promise.reject(error);
  },
);

export default request;
