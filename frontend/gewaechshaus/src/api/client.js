import axios from 'axios';

const defaultHeaders = {
  'Content-Type': 'application/json', 
  'Accept': 'application/json',     
};

const api = axios.create({
  baseURL: "http://100.82.182.52:8002",
  timeout: 10000,
  headers: defaultHeaders, 
});

export default api;