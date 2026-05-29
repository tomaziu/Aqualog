const API = window.location.origin;

const $ = (id) => document.getElementById(id);
let cacheClientes = [];
let cacheEntregadores = [];
let cacheProdutos = [];
let cachePedidos = [];

function valor(id) {
  const el = $(id);
  return el ? el.value.trim() : '';
}

function numero(id) {
  const n = Number(valor(id));
  return Number.isFinite(n) ? n : 0;
}

function mostrarTela(id) {
  document.querySelectorAll('.tela').forEach(t => t.classList.remove('ativa'));
  $(id).classList.add('ativa');
  carregarTudo();
}

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

async function carregarDashboard() {
  const d = await apiGet('/dashboard');
  if (!d || Array.isArray(d)) return;

  $('totalPedidos').textContent = d.total_pedidos ?? 0;
  $('tempoMedio').textContent = (d.tempo_medio_minutos ?? 0) + ' min';

  $('statusPedidos').innerHTML = (d.por_status ?? [])
    .map(s => `<p><span class="badge">${s.status}</span> ${s.total}</p>`)
    .join('');

  $('rotas').innerHTML = (d.roteirizacao_por_bairro ?? [])
    .map(r => `<p><span class="badge">${r.bairro}</span> ${r.entregas} entrega(s)</p>`)
    .join('');
}

function escapeHtml(valor) {
  return String(valor ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function lerCelula(idLinha, campo) {
  const el = document.querySelector(`[data-linha="${idLinha}"][data-campo="${campo}"]`);
  return el ? el.textContent.trim() : '';
}

function lerSelect(idLinha, campo) {
  const el = document.querySelector(`[data-linha="${idLinha}"][data-campo="${campo}"]`);
  return el ? el.value : '';
}

function renderCliente(c) {
  return `<tr>
    <td>${c.id}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="nome">${escapeHtml(c.nome)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="telefone">${escapeHtml(c.telefone)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="endereco">${escapeHtml(c.endereco)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="bairro">${escapeHtml(c.bairro)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="referencia">${escapeHtml(c.referencia || '')}</td>
    <td class="acoes">
      <button class="save" onclick="salvarCliente(${c.id})">Salvar</button>
      <button class="delete" onclick="excluirCliente(${c.id})">Excluir</button>
    </td>
  </tr>`;
}

async function carregarClientes() {
  const clientes = await apiGet('/clientes');
  if (!Array.isArray(clientes)) return;
  cacheClientes = clientes;
  filtrarClientes();

  $('pedidoCliente').innerHTML = clientes
    .map(c => `<option value="${c.id}">${escapeHtml(c.nome)} - ${escapeHtml(c.bairro)}</option>`)
    .join('');
}

function filtrarClientes() {
  const q = ($('filtroCliente').value || '').toLowerCase();
  const filtrados = cacheClientes.filter(c =>
    !q || c.nome.toLowerCase().includes(q) || c.bairro.toLowerCase().includes(q) || c.telefone.toLowerCase().includes(q)
  );
  $('listaClientes').innerHTML = filtrados.map(renderCliente).join('');
}

async function carregarEntregadores() {
  const dados = await apiGet('/entregadores');
  if (!Array.isArray(dados)) return;
  cacheEntregadores = dados;
  filtrarEntregadores();

  $('pedidoEntregador').innerHTML =
    '<option value="">Sem entregador</option>' +
    dados.map(e => `<option value="${e.id}">${escapeHtml(e.nome)} - ${escapeHtml(e.status)}</option>`).join('');
}

function filtrarEntregadores() {
  const q = ($('filtroEntregador').value || '').toLowerCase();
  const dados = cacheEntregadores.filter(e =>
    !q || e.nome.toLowerCase().includes(q) || e.veiculo.toLowerCase().includes(q) || e.telefone.toLowerCase().includes(q)
  );
  $('listaEntregadores').innerHTML = dados.map(e =>
    `<tr>
      <td>${e.id}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="nome">${escapeHtml(e.nome)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="telefone">${escapeHtml(e.telefone)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="veiculo">${escapeHtml(e.veiculo)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="codigo_acesso">${escapeHtml(e.codigo_acesso)}</td>
      <td>
        <select class="select-inline" data-linha="entregador-${e.id}" data-campo="status">
          <option value="disponivel" ${e.status === 'disponivel' ? 'selected' : ''}>Disponível</option>
          <option value="ocupado" ${e.status === 'ocupado' ? 'selected' : ''}>Ocupado</option>
        </select>
      </td>
      <td class="acoes">
        <button class="save" onclick="salvarEntregador(${e.id})">Salvar</button>
        <button class="delete" onclick="excluirEntregador(${e.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function carregarProdutos() {
  const dados = await apiGet('/produtos');
  if (!Array.isArray(dados)) return;
  cacheProdutos = dados;
  filtrarProdutos();

  $('pedidoProduto').innerHTML = dados
    .map(p => `<option value="${p.id}">${escapeHtml(p.nome)}</option>`)
    .join('');
}

function filtrarProdutos() {
  const q = ($('filtroProduto').value || '').toLowerCase();
  const dados = cacheProdutos.filter(p =>
    !q || p.nome.toLowerCase().includes(q)
  );
  $('listaProdutos').innerHTML = dados.map(p =>
    `<tr>
      <td>${p.id}</td>
      <td class="editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="nome">${escapeHtml(p.nome)}</td>
      <td class="editavel numero-editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="preco">${Number(p.preco).toFixed(2)}</td>
      <td class="editavel numero-editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="estoque">${p.estoque}</td>
      <td class="acoes">
        <button class="save" onclick="salvarProduto(${p.id})">Salvar</button>
        <button class="delete" onclick="excluirProduto(${p.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function carregarPedidos() {
  const dados = await apiGet('/pedidos');
  if (!Array.isArray(dados)) return;
  cachePedidos = dados;
  filtrarPedidos();
}

function formatarData(d) {
  if (!d) return '-';
  const dt = new Date(d);
  return dt.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusTexto(s) {
  const map = {
    'recebido': 'Recebido',
    'em_preparo': 'Em preparo',
    'saiu_para_entrega': 'Saiu p/ entrega',
    'entregue': 'Entregue',
    'cancelado': 'Cancelado'
  };
  return map[s] || s;
}

function filtrarPedidos() {
  const q = ($('filtroPedido').value || '').toLowerCase();
  const filtrados = cachePedidos.filter(p =>
    !q
    || (p.cliente && p.cliente.toLowerCase().includes(q))
    || (p.entregador && p.entregador.toLowerCase().includes(q))
    || (p.bairro && p.bairro.toLowerCase().includes(q))
    || (p.produto && p.produto.toLowerCase().includes(q))
    || (p.status && statusTexto(p.status).toLowerCase().includes(q))
  );
  $('listaPedidos').innerHTML = filtrados.map(p =>
    `<tr>
      <td>${p.id}</td>
      <td>${escapeHtml(p.cliente)}</td>
      <td>${escapeHtml(p.entregador || '-')}</td>
      <td>${escapeHtml(p.produto)}</td>
      <td>${escapeHtml(p.bairro)}</td>
      <td>${statusTexto(p.status)}</td>
      <td>${formatarData(p.data_criacao)}</td>
      <td class="acoes">
        <select onchange="mudarStatus(${p.id}, this.value)">
          <option value="">Alterar status</option>
          <option value="recebido">Recebido</option>
          <option value="em_preparo">Em preparo</option>
          <option value="saiu_para_entrega">Saiu p/ entrega</option>
          <option value="entregue">Entregue</option>
          <option value="cancelado">Cancelado</option>
        </select>
        <button class="delete" onclick="excluirPedido(${p.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function carregarTudo() {
  await carregarDashboard();
  await carregarClientes();
  await carregarEntregadores();
  await carregarProdutos();
  await carregarPedidos();
}

$('formCliente').onsubmit = async (e) => {
  e.preventDefault();

  const cliente = {
    nome: valor('clienteNome'),
    telefone: valor('clienteTelefone'),
    endereco: valor('clienteEndereco'),
    bairro: valor('clienteBairro'),
    referencia: valor('clienteReferencia') || null
  };

  const resposta = await apiSend('/clientes', 'POST', cliente);
  if (resposta) {
    $('formCliente').reset();
    await carregarTudo();
    alert('Cliente cadastrado com sucesso!');
  }
};

$('formEntregador').onsubmit = async (e) => {
  e.preventDefault();

  const entregador = {
    nome: valor('entregadorNome'),
    telefone: valor('entregadorTelefone'),
    veiculo: valor('entregadorVeiculo'),
    codigo_acesso: valor('entregadorCodigo'),
    status: valor('entregadorStatus') || 'disponivel'
  };

  const resposta = await apiSend('/entregadores', 'POST', entregador);
  if (resposta) {
    $('formEntregador').reset();
    await carregarTudo();
    alert('Entregador cadastrado com sucesso!');
  }
};

$('formProduto').onsubmit = async (e) => {
  e.preventDefault();

  const produto = {
    nome: valor('produtoNome'),
    preco: numero('produtoPreco'),
    estoque: numero('produtoEstoque')
  };

  const resposta = await apiSend('/produtos', 'POST', produto);
  if (resposta) {
    $('formProduto').reset();
    await carregarTudo();
    alert('Produto cadastrado com sucesso!');
  }
};

$('formPedido').onsubmit = async (e) => {
  e.preventDefault();

  const pedido = {
    cliente_id: numero('pedidoCliente'),
    entregador_id: valor('pedidoEntregador') ? numero('pedidoEntregador') : null,
    produto_id: numero('pedidoProduto'),
    quantidade: numero('pedidoQuantidade'),
    forma_pagamento: valor('pedidoPagamento')
  };

  const resposta = await apiSend('/pedidos', 'POST', pedido);
  if (resposta) {
    $('formPedido').reset();
    await carregarTudo();
    alert('Pedido criado com sucesso!');
  }
};

async function salvarCliente(id) {
  const linha = `cliente-${id}`;
  const cliente = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone'),
    endereco: lerCelula(linha, 'endereco'),
    bairro: lerCelula(linha, 'bairro'),
    referencia: lerCelula(linha, 'referencia') || null
  };

  const resposta = await apiSend(`/clientes/${id}`, 'PUT', cliente);
  if (resposta) {
    await carregarTudo();
    alert('Cliente atualizado com sucesso!');
  }
}

async function salvarEntregador(id) {
  const linha = `entregador-${id}`;
  const entregador = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone'),
    veiculo: lerCelula(linha, 'veiculo'),
    codigo_acesso: lerCelula(linha, 'codigo_acesso'),
    status: lerSelect(linha, 'status') || 'disponivel'
  };

  const resposta = await apiSend(`/entregadores/${id}`, 'PUT', entregador);
  if (resposta) {
    await carregarTudo();
    alert('Entregador atualizado com sucesso!');
  }
}

async function salvarProduto(id) {
  const linha = `produto-${id}`;
  const produto = {
    nome: lerCelula(linha, 'nome'),
    preco: Number(lerCelula(linha, 'preco').replace(',', '.')),
    estoque: Number(lerCelula(linha, 'estoque'))
  };

  if (!produto.nome || produto.nome.length < 2 || produto.preco <= 0 || produto.estoque < 0) {
    alert('Dados inválidos para produto. Confira nome, preço e estoque.');
    return;
  }

  const resposta = await apiSend(`/produtos/${id}`, 'PUT', produto);
  if (resposta) {
    await carregarTudo();
    alert('Produto atualizado com sucesso!');
  }
}

async function excluirCliente(id) {
  if (!confirm('Deseja excluir este cliente?')) return;
  if (await apiDelete(`/clientes/${id}`)) await carregarTudo();
}

async function excluirEntregador(id) {
  if (!confirm('Deseja excluir este entregador?')) return;
  if (await apiDelete(`/entregadores/${id}`)) await carregarTudo();
}

async function excluirProduto(id) {
  if (!confirm('Deseja excluir este produto?')) return;
  if (await apiDelete(`/produtos/${id}`)) await carregarTudo();
}

async function excluirPedido(id) {
  if (!confirm('Deseja excluir este pedido?')) return;
  if (await apiDelete(`/pedidos/${id}`)) await carregarTudo();
}

async function mudarStatus(id, status) {
  if (!status) return;
  const r = await fetch(`${API}/pedidos/${id}/status?status=${encodeURIComponent(status)}`, {method: 'PATCH'});
  if (!r.ok) alert('Não foi possível alterar o status.');
  await carregarTudo();
}

carregarTudo();
