var API = window.location.origin;
var API_PREFIX = '/api/v1';
var entregadorAtual = null;
var filtroAtual = 'todos';
var todosPedidos = [];
var intervaloRefresh = null;
var ultimoPedidosEntregador = null;

function statusClasse(s) {
  return 'status-' + s;
}

function salvarSessao() {
  if (entregadorAtual) {
    sessionStorage.setItem('entregador_id', entregadorAtual.id);
    sessionStorage.setItem('entregador_nome', entregadorAtual.nome);
    sessionStorage.setItem('entregador_veiculo', entregadorAtual.veiculo);
    sessionStorage.setItem('token', entregadorAtual.token);
    sessionStorage.setItem('tipo', 'entregador');
  }
}

function limparSessao() {
  sessionStorage.removeItem('entregador_id');
  sessionStorage.removeItem('entregador_nome');
  sessionStorage.removeItem('entregador_veiculo');
  sessionStorage.removeItem('token');
  sessionStorage.removeItem('tipo');
}

function sessaoValida() {
  return sessionStorage.getItem('entregador_id') !== null;
}

function iniciarAutoRefresh() {
  pararAutoRefresh();
  intervaloRefresh = setInterval(function() {
    carregarPedidos();
  }, 5000);
}

function pararAutoRefresh() {
  if (intervaloRefresh) {
    clearInterval(intervaloRefresh);
    intervaloRefresh = null;
  }
}

(function() {
  var id = sessionStorage.getItem('entregador_id');
  if (id) {
    entregadorAtual = {
      id: Number(id),
      nome: sessionStorage.getItem('entregador_nome'),
      veiculo: sessionStorage.getItem('entregador_veiculo'),
      token: sessionStorage.getItem('token')
    };
    mostrarMenu();
    carregarPedidos();
  }
})();

async function fazerLogin() {
  var codigo = $('input-codigo').value.trim();
  if (!codigo) return;
  $('erro-login').textContent = '';
  try {
    var r = await fetch(API + API_PREFIX + '/entregadores/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codigo_acesso: codigo })
    });
    if (!r.ok) {
      var erro = await r.json();
      $('erro-login').textContent = erro.detail || 'Codigo invalido';
      return;
    }
    var json = await r.json();
    entregadorAtual = {
      id: json.id,
      nome: json.nome,
      veiculo: json.veiculo,
      token: json.access_token
    };
    salvarSessao();
    mostrarMenu();
    carregarPedidos();
  } catch (e) {
    $('erro-login').textContent = 'Erro de conexao com o servidor';
  }
}

function sair() {
  limparSessao();
  entregadorAtual = null;
  pararAutoRefresh();
  $('input-codigo').value = '';
  $('tela-menu').style.display = 'none';
  $('tela-pedidos').style.display = 'none';
  $('tela-login').style.display = 'flex';
}

function mostrarMenu() {
  $('tela-login').style.display = 'none';
  $('tela-pedidos').style.display = 'none';
  $('tela-menu').style.display = 'block';
  $('info-entregador').textContent = entregadorAtual.nome + ' - ' + entregadorAtual.veiculo;
  $('msg-boas-vindas').textContent = 'Bom trabalho, ' + entregadorAtual.nome + '!';
  atualizarRelogio();
  if (!window.clockInterval) {
    window.clockInterval = setInterval(atualizarRelogio, 1000);
  }
  iniciarAutoRefresh();
}

function atualizarRelogio() {
  var agora = new Date();
  $('relogio').textContent = agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function atualizarUltimoPedido() {
  var entregues = todosPedidos.filter(function(p) { return p.status === 'entregue'; });
  if (entregues.length === 0) {
    $('msg-ultimo-pedido').textContent = 'Nenhum pedido entregue ainda';
    return;
  }
  var ultimo = entregues.reduce(function(a, b) {
    return new Date(a.data_criacao) > new Date(b.data_criacao) ? a : b;
  });
  var minAgo = Math.floor((Date.now() - new Date(ultimo.data_criacao)) / 60000);
  if (minAgo < 1) {
    $('msg-ultimo-pedido').textContent = 'Pedido #' + ultimo.id + ' entregue agora';
  } else {
    $('msg-ultimo-pedido').textContent = 'Pedido #' + ultimo.id + ' entregue ha ' + minAgo + 'min';
  }
}

function voltarMenu() {
  $('tela-pedidos').style.display = 'none';
  $('tela-menu').style.display = 'block';
}

function abrirPedidos(filtro) {
  filtroAtual = filtro;
  $('tela-menu').style.display = 'none';
  $('tela-pedidos').style.display = 'block';
  var titulos = {
    'todos': 'Todos os pedidos',
    'saiu_para_entrega': 'Em rota',
    'em_preparo': 'Preparando',
    'entregue': 'Entregues'
  };
  $('titulo-pedidos').textContent = titulos[filtro] || 'Pedidos';
  renderizar(todosPedidos);
}

async function carregarPedidos() {
  if (!entregadorAtual) return;
  var url = API + API_PREFIX + '/entregadores/' + entregadorAtual.id + '/pedidos';
  try {
    var r = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + (entregadorAtual.token || sessionStorage.getItem('token')) },
      cache: 'no-cache'
    });
    if (r.status === 401) {
      sair();
      return;
    }
    var dados = await r.json();
    if (!Array.isArray(dados)) dados = [];

    var dadosAtuais = JSON.stringify(dados);
    if (ultimoPedidosEntregador === dadosAtuais) {
      return; // Dados não mudaram
    }
    ultimoPedidosEntregador = dadosAtuais;
    todosPedidos = dados;
    atualizarContadores();
    if ($('tela-pedidos').style.display === 'block') {
      renderizar(todosPedidos);
    }
  } catch (e) {
    // silencioso para nao ficar alertando
  }
}

function atualizarContadores() {
  var total = todosPedidos.length;
  var rota = todosPedidos.filter(function(p) { return p.status === 'saiu_para_entrega'; }).length;
  var preparo = todosPedidos.filter(function(p) { return p.status === 'em_preparo' || p.status === 'recebido'; }).length;
  var entregues = todosPedidos.filter(function(p) { return p.status === 'entregue'; }).length;

  var qtdTodos = $('qtd-todos');
  var qtdRota = $('qtd-rota');
  var qtdPreparo = $('qtd-preparo');
  var qtdEntregues = $('qtd-entregues');
  if (qtdTodos) qtdTodos.textContent = total;
  if (qtdRota) qtdRota.textContent = rota + '/' + total;
  if (qtdPreparo) qtdPreparo.textContent = preparo + '/' + total;
  if (qtdEntregues) qtdEntregues.textContent = entregues + '/' + total;
  atualizarUltimoPedido();
}

function renderizar(pedidos) {
  var filtrados = filtroAtual === 'todos' ? pedidos : pedidos.filter(function(p) { return p.status === filtroAtual; });

  if (!filtrados.length) {
    $('lista-pedidos').innerHTML = '<div class="vazio">Nenhum pedido encontrado</div>';
    return;
  }
  $('lista-pedidos').innerHTML = filtrados.map(function(p) {
    var mostraSair = p.status === 'em_preparo' || p.status === 'recebido';
    var mostraEntregue = p.status === 'saiu_para_entrega';
    var mostraVoltar = p.status === 'entregue';
    var endereco = escapeHtml(p.endereco) + (p.numero_casa ? ', ' + escapeHtml(p.numero_casa) : '') + ', ' + escapeHtml(p.bairro);

    return '<div class="pedido-card">' +
      '<div class="topo-card">' +
        '<strong>#' + p.id + ' - ' + escapeHtml(p.cliente) + '</strong>' +
        '<span class="status-badge ' + statusClasse(p.status) + '">' + statusTexto(p.status) + '</span>' +
      '</div>' +
      '<div class="endereco">' + endereco + '</div>' +
      '<div class="info">' + (p.referencia ? 'Ref: ' + escapeHtml(p.referencia) : '') + '</div>' +
      '<div class="info">' + escapeHtml(p.produto) + ' - Total: R$ ' + Number(p.total || (p.preco * p.quantidade)).toFixed(2).replace('.', ',') + ' (' + escapeHtml(p.forma_pagamento) + ')</div>' +
      '<div class="info">Tel: ' + escapeHtml(p.telefone) + ' - ' + formatarData(p.data_criacao) + '</div>' +
      '<div class="acoes-card">' +
        (mostraSair ? '<button class="btn-sair" onclick="mudarStatus(event, ' + p.id + ',\'saiu_para_entrega\')">Saiu p/ entrega</button>' : '') +
        (mostraEntregue ? '<button class="btn-entregue" onclick="mudarStatus(event, ' + p.id + ',\'entregue\')">Entregue</button>' : '') +
        (mostraVoltar ? '<button class="btn-voltar" onclick="mudarStatus(event, ' + p.id + ',\'saiu_para_entrega\')">Voltar p/ rota</button>' : '') +
      '</div>' +
    '</div>';
  }).join('');
}

async function mudarStatus(event, id, status) {
  console.log('BOTAO CLICADO: Pedido ' + id + ' para status ' + status);
  var btn = event.target;
  var originalText = btn.textContent;

  var codigoEntrega = '';
  if (status === 'entregue') {
    codigoEntrega = prompt('Digite o código de entrega informado pelo cliente:') || '';
    codigoEntrega = codigoEntrega.replace(/\D/g, '');
    if (!codigoEntrega) return;
  }

  try {
    btn.disabled = true;
    btn.textContent = '...';

    var url = API + API_PREFIX + '/pedidos/' + id + '/status/entregador?status=' + encodeURIComponent(status);
    if (codigoEntrega) {
      url += '&codigo=' + encodeURIComponent(codigoEntrega);
    }

    var r = await fetch(url, {
      method: 'PATCH',
      headers: { 'Authorization': 'Bearer ' + (entregadorAtual.token || sessionStorage.getItem('token')) },
      cache: 'no-cache'
    });
    if (!r.ok) {
      var erro = await r.json().catch(() => ({}));
      alert('Erro ao atualizar status: ' + (erro.detail || 'Erro desconhecido'));
      btn.disabled = false;
      btn.textContent = originalText;
      return;
    }
    ultimoPedidosEntregador = null;
    await carregarPedidos();
  } catch (e) {
    alert('Erro de conexao');
    if(btn) { btn.disabled = false; btn.textContent = originalText; }
  }
}

$('input-codigo').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') fazerLogin();
});
