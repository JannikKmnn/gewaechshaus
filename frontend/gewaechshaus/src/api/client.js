import axios from 'axios';

const defaultHeaders = {
  'Content-Type': 'application/json', 
  'Accept': 'application/json',     
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 20000,
  headers: defaultHeaders, 
});

export default api;