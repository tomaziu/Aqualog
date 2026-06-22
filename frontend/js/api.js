const API = window.location.origin;
const API_PREFIX = '/api/v1';
const apiWriteLocks = {};

function getToken() {
  return sessionStorage.getItem('token') || null;
}

function getAuthHeaders() {
  const headers = {'Content-Type': 'application/json'};
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

async function apiGet(url) {
  document.body.classList.add('loading');
  try {
    const sep = url.includes('?') ? '&' : '?';
    const r = await fetch(API + API_PREFIX + url + sep + '_t=' + Date.now(), {
      headers: getAuthHeaders()
    });
    if (r.status === 401) {
      sessionStorage.clear();
      window.location.reload();
      return [];
    }
    if (!r.ok) throw new Error(await r.text());
    const json = await r.json();
    if (json && json.success !== undefined && json.success === false) {
      console.error('API error:', json.error);
      return [];
    }
    return json.data !== undefined ? json.data : json;
  } catch (erro) {
    console.error('Erro no GET', url, erro);
    return [];
  } finally {
    document.body.classList.remove('loading');
  }
}

function mensagemErroFastAPI(erro) {
  if (Array.isArray(erro.detail)) {
    return erro.detail.map(function(e) { return (e.loc || []).join('.') + ': ' + e.msg; }).join('\n');
  }
  if (erro.detail) return String(erro.detail);
  if (erro.error) return String(erro.error);
  return JSON.stringify(erro);
}

async function apiSend(url, method, data) {
  const chaveLock = method + ':' + url + ':' + JSON.stringify(data || {});
  if (apiWriteLocks[chaveLock]) return null;
  apiWriteLocks[chaveLock] = true;
  document.body.classList.add('loading');
  try {
    const r = await fetch(API + API_PREFIX + url, {
      method: method,
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    let resposta = {};
    try { resposta = await r.json(); } catch { resposta = {}; }
    if (!r.ok) {
      console.error('Erro na operacao:', method, url, data, resposta);
      mostrarToast('erro', mensagemErroFastAPI(resposta));
      return null;
    }
    return resposta.data !== undefined ? resposta.data : resposta;
  } finally {
    delete apiWriteLocks[chaveLock];
    document.body.classList.remove('loading');
  }
}

async function apiDelete(url) {
  const chaveLock = 'DELETE:' + url;
  if (apiWriteLocks[chaveLock]) return false;
  apiWriteLocks[chaveLock] = true;
  document.body.classList.add('loading');
  try {
    const r = await fetch(API + API_PREFIX + url, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (r.status === 401) {
      sessionStorage.clear();
      window.location.reload();
      return false;
    }
    if (!r.ok) {
      let erro = {};
      try { erro = await r.json(); } catch {}
      mostrarToast('erro', mensagemErroFastAPI(erro));
      return false;
    }
    return true;
  } finally {
    delete apiWriteLocks[chaveLock];
    document.body.classList.remove('loading');
  }
}

function mostrarToast(tipo, mensagem) {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + tipo;
  toast.textContent = mensagem;
  container.appendChild(toast);
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-20px)';
    setTimeout(function() { toast.remove(); }, 300);
  }, 4000);
}
