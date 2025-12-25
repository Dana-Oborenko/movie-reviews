// Minimal Axios instance for FastAPI
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // FastAPI URL
  timeout: 15000,
})
