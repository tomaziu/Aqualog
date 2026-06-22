var API = window.location.origin;
var API_PREFIX = '/api/v1';
var entregadorAtual = null;
var filtroAtual = 'todos';
var todosPedidos = [];
var intervaloRefresh = null;
var ultimoPedidosEntregador = null;
var gpsWatchId = null;
var gpsIntervaloEnvio = null;
var gpsUltimaPosicao = null;
var gpsCompartilhando = false;
var gpsUltimoEnvio = 0;

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

function atualizarIndicadorGPS(estado, detalhe) {
  var badge = $('gpsStatus');
  var info = $('gpsDetalhe');
  if (!badge || !info) return;
  var textos = {
    active: 'Localização ativa',
    off: 'Localização desativada',
    weak: 'Sinal GPS fraco',
    offline: 'Sem conexão com a internet'
  };
  badge.textContent = textos[estado] || textos.off;
  badge.className = 'gps-badge gps-' + (estado === 'active' ? 'active' : estado === 'weak' ? 'weak' : estado === 'offline' ? 'offline' : 'off');
  info.textContent = detalhe || '';
}

function temPedidoEmRota() {
  return todosPedidos.some(function(p) {
    return p.status === 'saiu_para_entrega' || p.status === 'em_preparo' || p.status === 'recebido';
  });
}

function iniciarCompartilhamentoLocalizacao() {
  if (!navigator.geolocation) {
    atualizarIndicadorGPS('off', 'Seu navegador não oferece suporte à localização.');
    return;
  }
  if (!navigator.onLine) {
    atualizarIndicadorGPS('offline', 'Sem internet. A localização será enviada quando a conexão voltar.');
    return;
  }
  gpsCompartilhando = true;
  atualizarIndicadorGPS('weak', 'Solicitando permissão de localização...');
  if (gpsWatchId !== null) navigator.geolocation.clearWatch(gpsWatchId);
  gpsWatchId = navigator.geolocation.watchPosition(function(pos) {
    gpsUltimaPosicao = pos;
    var accuracy = pos.coords.accuracy || 0;
    atualizarIndicadorGPS(accuracy > 80 ? 'weak' : 'active', accuracy > 80 ? 'Localização recebida, mas o sinal está fraco.' : 'Localização ativa e pronta para rastreamento.');
    enviarLocalizacaoAtual(false);
  }, function(err) {
    gpsCompartilhando = false;
    if (err.code === err.PERMISSION_DENIED) {
      atualizarIndicadorGPS('off', 'Permissão negada. Não será possível iniciar entregas com rastreamento.');
    } else {
      atualizarIndicadorGPS('weak', 'Não foi possível obter a localização agora.');
    }
  }, { enableHighAccuracy: true, maximumAge: 4000, timeout: 12000 });

  if (gpsIntervaloEnvio) clearInterval(gpsIntervaloEnvio);
  gpsIntervaloEnvio = setInterval(function() {
    enviarLocalizacaoAtual(true);
  }, 5000);
}

function pararCompartilhamentoLocalizacao() {
  gpsCompartilhando = false;
  if (gpsWatchId !== null) {
    navigator.geolocation.clearWatch(gpsWatchId);
    gpsWatchId = null;
  }
  if (gpsIntervaloEnvio) {
    clearInterval(gpsIntervaloEnvio);
    gpsIntervaloEnvio = null;
  }
  atualizarIndicadorGPS('off', 'Compartilhamento finalizado pelo entregador.');
}

async function enviarLocalizacaoAtual(forcar) {
  if (!gpsCompartilhando || !gpsUltimaPosicao || !entregadorAtual) return;
  if (!navigator.onLine) {
    atualizarIndicadorGPS('offline', 'Sem conexão com a internet. Tentaremos novamente em alguns segundos.');
    return;
  }
  if (!forcar && Date.now() - gpsUltimoEnvio < 5000) return;
  var c = gpsUltimaPosicao.coords;
  gpsUltimoEnvio = Date.now();
  try {
    var r = await fetch(API + API_PREFIX + '/deliveries/driver/location', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (entregadorAtual.token || sessionStorage.getItem('token'))
      },
      body: JSON.stringify({
        latitude: c.latitude,
        longitude: c.longitude,
        accuracy: c.accuracy,
        heading: c.heading,
        speed: c.speed,
        source: 'browser-watchPosition'
      })
    });
    if (r.status === 404) {
      atualizarIndicadorGPS('weak', 'Localização ativa. Nenhuma entrega rastreável foi encontrada para envio.');
      return;
    }
    if (!r.ok) throw new Error('gps');
    atualizarIndicadorGPS((c.accuracy || 0) > 80 ? 'weak' : 'active', 'Último envio: ' + new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
  } catch (e) {
    atualizarIndicadorGPS('offline', 'Não foi possível enviar a localização agora.');
  }
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
  pararCompartilhamentoLocalizacao();
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
  if (navigator.geolocation && !gpsCompartilhando) {
    iniciarCompartilhamentoLocalizacao();
  }
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

var codigoEntregaPendente = null;
var codigoModalResolve = null;

function abrirCodigoModal() {
  return new Promise(function(resolve) {
    codigoModalResolve = resolve;
    var boxes = document.querySelectorAll('.codigo-box');
    boxes.forEach(function(b) { b.value = ''; b.classList.remove('filled'); });
    $('codigoModal').classList.add('ativo');
    setTimeout(function() { boxes[0].focus(); }, 100);
  });
}

function fecharCodigoModal() {
  $('codigoModal').classList.remove('ativo');
  if (codigoModalResolve) { codigoModalResolve(null); codigoModalResolve = null; }
}

function confirmarCodigoModal() {
  var boxes = document.querySelectorAll('.codigo-box');
  var codigo = '';
  boxes.forEach(function(b) { codigo += b.value; });
  $('codigoModal').classList.remove('ativo');
  if (codigoModalResolve) { codigoModalResolve(codigo.length === 6 ? codigo : null); codigoModalResolve = null; }
}

document.addEventListener('DOMContentLoaded', function() {
  var container = $('codigoInputs');
  if (!container) return;
  var boxes = container.querySelectorAll('.codigo-box');

  boxes.forEach(function(box, idx) {
    box.addEventListener('input', function(e) {
      var val = e.target.value.replace(/\D/g, '');
      e.target.value = val.slice(0, 1);
      if (val && idx < boxes.length - 1) {
        boxes[idx + 1].focus();
      }
      if (val) e.target.classList.add('filled');
      else e.target.classList.remove('filled');
      if (idx === boxes.length - 1 && val) {
        confirmarCodigoModal();
      }
    });

    box.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace' && !e.target.value && idx > 0) {
        boxes[idx - 1].focus();
        boxes[idx - 1].value = '';
        boxes[idx - 1].classList.remove('filled');
      }
      if (e.key === 'Enter') {
        confirmarCodigoModal();
      }
    });

    box.addEventListener('paste', function(e) {
      e.preventDefault();
      var texto = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '').slice(0, 6);
      texto.split('').forEach(function(ch, i) {
        if (boxes[i]) { boxes[i].value = ch; boxes[i].classList.add('filled'); }
      });
      if (texto.length > 0) boxes[Math.min(texto.length, boxes.length) - 1].focus();
      if (texto.length === 6) confirmarCodigoModal();
    });
  });
});

async function mudarStatus(event, id, status) {
  console.log('BOTAO CLICADO: Pedido ' + id + ' para status ' + status);
  var btn = event.target;
  var originalText = btn.textContent;

  var codigoEntrega = '';
  if (status === 'entregue') {
    codigoEntrega = await abrirCodigoModal();
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
      mostrarToast('erro', 'Erro ao atualizar status: ' + (erro.detail || 'Erro desconhecido'));
      btn.disabled = false;
      btn.textContent = originalText;
      return;
    }
    ultimoPedidosEntregador = null;
    await carregarPedidos();
  } catch (e) {
    mostrarToast('erro', 'Erro de conexao');
    if(btn) { btn.disabled = false; btn.textContent = originalText; }
  }
}

$('input-codigo').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') fazerLogin();
});
