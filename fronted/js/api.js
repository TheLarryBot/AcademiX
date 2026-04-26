/**
 * AcademiX — api.js
 * Cliente centralizado para todas las llamadas al backend Flask.
 */

const BASE_URL = '/api';

/* ─────────────────────────────────────────
   HELPER PRINCIPAL
───────────────────────────────────────── */

async function request(method, endpoint, body = null) {

  const token = localStorage.getItem("token");

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };

  const options = {
    method,
    headers
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, options);

  // 🔐 Si el token expiró o es inválido
  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    return;
  }

  if (!response.ok) {
    let errorMsg = `Error ${response.status}`;
    try {
      const errorData = await response.json();
      errorMsg = errorData.message || errorData.error || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  if (response.status === 204) return null;

  return response.json();
}

/* ─────────────────────────────────────────
   AUTH
───────────────────────────────────────── */

export const authAPI = {

  async login(credentials) {
    const data = await request('POST', '/auth/login', credentials);

    // Guardar token al iniciar sesión
    if (data.token) {
      localStorage.setItem("token", data.token);
    }

    return data;
  },

  async logout() {
    localStorage.removeItem("token");
    return request('POST', '/auth/logout');
  },

  async me() {
    return request('GET', '/auth/me');
  }
};

/* ─────────────────────────────────────────
   ACTIVIDADES
───────────────────────────────────────── */

export const actividadesAPI = {

  getAll(filters = {}) {
    const query = new URLSearchParams(filters).toString();
    return request('GET', `/actividades${query ? '?' + query : ''}`);
  },

  getOne(id) {
    return request('GET', `/actividades/${id}`);
  },

  create(data) {
    return request('POST', '/actividades', data);
  },

  update(id, data) {
    return request('PUT', `/actividades/${id}`, data);
  },

  delete(id) {
    return request('DELETE', `/actividades/${id}`);
  }
};

/* ─────────────────────────────────────────
   USUARIOS
───────────────────────────────────────── */

export const usuariosAPI = {

  getAll() {
    return request('GET', '/usuarios');
  },

  getOne(id) {
    return request('GET', `/usuarios/${id}`);
  },

  create(data) {
    return request('POST', '/usuarios', data);
  },

  update(id, data) {
    return request('PUT', `/usuarios/${id}`, data);
  },

  delete(id) {
    return request('DELETE', `/usuarios/${id}`);
  }
};

/* ─────────────────────────────────────────
   HISTORIAL
───────────────────────────────────────── */

export const historialAPI = {

  getAll() {
    return request('GET', '/historial');
  },

  getOne(id) {
    return request('GET', `/historial/${id}`);
  }
};

/* ─────────────────────────────────────────
   REPORTES
───────────────────────────────────────── */

export const reportesAPI = {

  get(tipo, params = {}) {
    const query = new URLSearchParams({ tipo, ...params }).toString();
    return request('GET', `/reportes?${query}`);
  },

  downloadCSV(tipo, params = {}) {
    const token = localStorage.getItem("token") ?? '';
    const query = new URLSearchParams({ tipo, ...params }).toString();
    window.open(`${BASE_URL}/reportes/csv?${query}`, '_blank');
  }
};

/* ─────────────────────────────────────────
   IA (Ollama)
───────────────────────────────────────── */

export const iaAPI = {

  generar(prompt) {
    return request('POST', '/ia/generar', { prompt });
  },

  sugerir(contexto) {
    return request('POST', '/ia/sugerir', { contexto });
  },

  estado() {
    return request('GET', '/ia/estado');
  }
};