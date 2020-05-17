import axios from "axios";

const SERVER_PORT = process.env.SERVER_HOST || "8000";

if (process.browser) {
  axios.defaults.baseURL = `http://localhost:${SERVER_PORT}/api`;
} else {
  axios.defaults.baseURL = `http://localhost:${SERVER_PORT}/api`;
}

export default axios;
