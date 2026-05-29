var API = window.location.origin;
var entregadorAtual = null;
var filtroAtual = 'todos';

function $(id) { return document.getElementById(id); }

function escapeHtml(texto) {
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(texto));
  return div.innerHTML;
}

function statusTexto(s) {
  var map = {
    'recebido': 'Recebido',
    'em_preparo': 'Em preparo',
    'saiu_para_entrega': 'Saiu p/ entrega',
    'entregue': 'Entregue',
    'cancelado': 'Cancelado'
  };
  return map[s] || s;
}

function statusClasse(s) {
  return 'status-' + s;
}

function formatarData(dataStr) {
  if (!dataStr) return '';
  var d = new Date(dataStr);
  return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

async function fazerLogin() {
  var codigo = $('input-codigo').value.trim();
  if (!codigo) return;
  $('erro-login').textContent = '';
  try {
    var r = await fetch(API + '/entregadores/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codigo_acesso: codigo })
    });
    if (!r.ok) {
      var erro = await r.json();
      $('erro-login').textContent = erro.detail || 'Código inválido';
      return;
    }
    entregadorAtual = await r.json();
    $('tela-login').style.display = 'none';
    $('tela-pedidos').style.display = 'block';
    $('info-entregador').textContent = entregadorAtual.nome + ' - ' + entregadorAtual.veiculo;
    carregarPedidos();
  } catch (e) {
    $('erro-login').textContent = 'Erro de conexão com o servidor';
  }
}

function sair() {
  entregadorAtual = null;
  filtroAtual = 'todos';
  $('input-codigo').value = '';
  $('tela-pedidos').style.display = 'none';
  $('tela-login').style.display = 'flex';
}

async function carregarPedidos() {
  if (!entregadorAtual) return;
  var url = API + '/entregadores/' + entregadorAtual.id + '/pedidos';
  if (filtroAtual !== 'todos') url += '?status=' + encodeURIComponent(filtroAtual);
  try {
    var r = await fetch(url);
    var dados = await r.json();
    if (!Array.isArray(dados)) dados = [];
    renderizar(dados);
  } catch (e) {
    $('lista-pedidos').innerHTML = '<div class="vazio">Erro ao carregar</div>';
  }
}

function filtrar(filtro) {
  filtroAtual = filtro;
  document.querySelectorAll('.filtros button').forEach(function(b) {
    b.classList.toggle('ativo', b.dataset.filtro === filtro);
  });
  carregarPedidos();
}

function renderizar(pedidos) {
  if (!pedidos.length) {
    $('lista-pedidos').innerHTML = '<div class="vazio">Nenhum pedido encontrado</div>';
    return;
  }
  $('lista-pedidos').innerHTML = pedidos.map(function(p) {
    var mostraSair = p.status === 'em_preparo' || p.status === 'recebido' || p.status === 'saiu_para_entrega';
    var mostraEntregue = p.status === 'saiu_para_entrega';
    var mostraVoltar = p.status === 'entregue';

    return '<div class="pedido-card">' +
      '<div class="topo-card">' +
        '<strong>#' + p.id + ' - ' + escapeHtml(p.cliente) + '</strong>' +
        '<span class="status-badge ' + statusClasse(p.status) + '">' + statusTexto(p.status) + '</span>' +
      '</div>' +
      '<div class="endereco">' + escapeHtml(p.endereco) + ', ' + escapeHtml(p.bairro) + '</div>' +
      '<div class="info">' + (p.referencia ? 'Ref: ' + escapeHtml(p.referencia) : '') + '</div>' +
      '<div class="info">' + escapeHtml(p.produto) + ' x' + p.quantidade + ' - R$ ' + p.forma_pagamento + '</div>' +
      '<div class="info">Tel: ' + escapeHtml(p.telefone) + ' - ' + formatarData(p.data_criacao) + '</div>' +
      '<div class="acoes-card">' +
        (mostraSair ? '<button class="btn-sair" onclick="mudarStatus(' + p.id + ',\'saiu_para_entrega\')">Saiu p/ entrega</button>' : '') +
        (mostraEntregue ? '<button class="btn-entregue" onclick="mudarStatus(' + p.id + ',\'entregue\')">Entregue</button>' : '') +
        (mostraVoltar ? '<button class="btn-voltar" onclick="mudarStatus(' + p.id + ',\'saiu_para_entrega\')">Voltar p/ rota</button>' : '') +
      '</div>' +
    '</div>';
  }).join('');
}

async function mudarStatus(id, status) {
  try {
    var r = await fetch(API + '/pedidos/' + id + '/status?status=' + encodeURIComponent(status), { method: 'PATCH' });
    if (!r.ok) {
      alert('Erro ao atualizar status');
      return;
    }
    carregarPedidos();
  } catch (e) {
    alert('Erro de conexão');
  }
}

$('input-codigo').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') fazerLogin();
});
