const API = window.location.origin;

async function apiGet(url) {
  try {
    const r = await fetch(API + url);
    if (!r.ok) throw new Error(await r.text());
    return await r.json();
  } catch (erro) {
    console.error('Erro no GET', url, erro);
    return [];
  }
}

function mensagemErroFastAPI(erro) {
  if (Array.isArray(erro.detail)) {
    return erro.detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('\n');
  }
  if (erro.detail) return String(erro.detail);
  return JSON.stringify(erro);
}

async function apiSend(url, method, data) {
  const r = await fetch(API + url, {
    method,
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });

  let resposta = {};
  try {
    resposta = await r.json();
  } catch {
    resposta = {};
  }

  if (!r.ok) {
    console.error('Erro na operação:', method, url, data, resposta);
    alert('Erro na operação:\n' + mensagemErroFastAPI(resposta));
    return null;
  }

  return resposta;
}

async function apiDelete(url) {
  const r = await fetch(API + url, { method: 'DELETE' });
  if (!r.ok) {
    let erro = {};
    try { erro = await r.json(); } catch {}
    alert('Não foi possível excluir.\n' + mensagemErroFastAPI(erro));
    return false;
  }
  return true;
}
