/**
 * API client — centralized axios instance.
 * Uses HttpOnly cookies for JWT authentication.
 */

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // sends HttpOnly cookies on every request
});

export default api;
