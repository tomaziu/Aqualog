var _confirmCb = null;
var _promptCb = null;

function mostrarConfirm(titulo, mensagem, cb) {
  $('confirmTitle').textContent = titulo;
  $('confirmMsg').textContent = mensagem;
  _confirmCb = cb;
  $('confirmModal').style.zIndex = '10003';
  $('confirmModal').classList.add('ativo');
}

function fecharConfirm() {
  $('confirmModal').classList.remove('ativo');
  $('confirmModal').style.zIndex = '';
  _confirmCb = null;
}

function executarConfirm() {
  if (_confirmCb) _confirmCb();
  fecharConfirm();
}

function mostrarPrompt(titulo, mensagem, valorPadrao, cb) {
  $('promptTitle').textContent = titulo;
  $('promptMsg').textContent = mensagem;
  $('promptInput').value = valorPadrao || '';
  _promptCb = cb;
  $('promptModal').style.zIndex = '10003';
  $('promptModal').classList.add('ativo');
  $('promptInput').focus();
}

function fecharPrompt() {
  $('promptModal').classList.remove('ativo');
  $('promptModal').style.zIndex = '';
  _promptCb = null;
}

function executarPrompt() {
  var valor = $('promptInput').value;
  if (_promptCb) _promptCb(valor);
  fecharPrompt();
}

function salvarFiltro(id) {
  var el = $(id);
  if (el) localStorage.setItem('filtro_' + id, el.value);
}

function restaurarFiltros() {
  ['filtroCliente','filtroEntregador','filtroProduto','filtroPedido','filtroSuporte','filtroCupom'].forEach(function(id) {
    var el = $(id);
    var val = localStorage.getItem('filtro_' + id);
    if (el && val !== null) el.value = val;
  });
}

async function carregarTudo() {
  restaurarFiltros();
  if (typeof carregarConfiguracoes === 'function') {
    await carregarConfiguracoes();
  }
  await carregarDashboard();
  await carregarClientes();
  await carregarEntregadores();
  await carregarProdutos();
  await carregarPedidos();
  if (typeof carregarCupons === 'function') {
    await carregarCupons();
  }
  if (typeof carregarSuporte === 'function') {
    await carregarSuporte();
  }
}

async function carregarDadosNovoPedido(pedidoId) {
  if (pedidoId && typeof pedidoDestaqueId !== 'undefined') {
    pedidoDestaqueId = Number(pedidoId);
  }
  if (typeof mostrarTela === 'function' && $('pedidos') && !$('pedidos').classList.contains('ativa')) {
    mostrarTela('pedidos', false);
  }
  ultimoPedidos = null;
  ultimoClientes = null;
  await carregarDashboard();
  await carregarClientes();
  await carregarPedidos();
  if (typeof carregarSuporte === 'function') {
    await carregarSuporte();
  }
}

function mostrarAlertaSucesso(msg) {
  mostrarToast('sucesso', msg);
}

function limparTelefone(valor) {
  return valor.replace(/\D/g, '');
}

function formatarTelefone(input) {
  var digitos = input.value.replace(/\D/g, '').slice(0, 11);
  if (digitos.length <= 10) {
    input.value = digitos.replace(/^(\d{2})(\d{4})(\d{0,4})/, '($1) $2-$3');
  } else {
    input.value = digitos.replace(/^(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
  }
}

$('clienteTelefone').addEventListener('input', function() { formatarTelefone(this); });
$('entregadorTelefone').addEventListener('input', function() { formatarTelefone(this); });

$('formCliente').onsubmit = async function(e) {
  e.preventDefault();
  var cliente = {
    nome: valor('clienteNome'),
    telefone: limparTelefone(valor('clienteTelefone')),
    endereco: valor('clienteEndereco'),
    numero_casa: valor('clienteNumeroCasa') || null,
    bairro: valor('clienteBairro'),
    referencia: valor('clienteReferencia') || null
  };
  var resposta = await apiSend('/clientes', 'POST', cliente);
  if (resposta) {
    $('formCliente').reset();
    await carregarTudo();
    mostrarAlertaSucesso('Cliente cadastrado com sucesso!');
  }
};

$('formEntregador').onsubmit = async function(e) {
  e.preventDefault();
  var entregador = {
    nome: valor('entregadorNome'),
    telefone: limparTelefone(valor('entregadorTelefone')),
    veiculo: valor('entregadorVeiculo'),
    codigo_acesso: valor('entregadorCodigo'),
    status: valor('entregadorStatus') || 'disponivel'
  };
  var resposta = await apiSend('/entregadores', 'POST', entregador);
  if (resposta) {
    $('formEntregador').reset();
    await carregarTudo();
    mostrarAlertaSucesso('Entregador cadastrado com sucesso!');
  }
};

$('formProduto').onsubmit = async function(e) {
  e.preventDefault();
  var produto = {
    nome: valor('produtoNome'),
    preco: numero('produtoPreco'),
    estoque: numero('produtoEstoque'),
    estoque_minimo: numero('produtoEstoqueMinimo'),
    ativo: valor('produtoAtivo') === '1'
  };
  var resposta = await apiSend('/produtos', 'POST', produto);
  if (resposta) {
    $('formProduto').reset();
    $('produtoEstoqueMinimo').value = configAtual ? (configAtual.estoque_minimo_padrao ?? 5) : 5;
    $('produtoAtivo').value = '1';
    await carregarTudo();
    mostrarAlertaSucesso('Produto cadastrado com sucesso!');
  }
};

$('formPedido').onsubmit = async function(e) {
  e.preventDefault();
  var pedido = {
    cliente_id: numero('pedidoCliente'),
    entregador_id: valor('pedidoEntregador') ? numero('pedidoEntregador') : null,
    produto_id: numero('pedidoProduto'),
    quantidade: numero('pedidoQuantidade'),
    forma_pagamento: valor('pedidoPagamento')
  };
  var resposta = await apiSend('/pedidos', 'POST', pedido);
  if (resposta) {
    $('formPedido').reset();
    await carregarTudo();
    mostrarAlertaSucesso('Pedido criado com sucesso!');
  }
};

var adminEvtSource = null;
var timerExpiracaoPix = null;
var audioAvisoPedido = null;

function atualizarStatusSSE(estado, texto) {
  var el = $('sseStatus');
  if (!el) return;
  el.classList.remove('sse-online', 'sse-offline', 'sse-reconnecting');
  el.classList.add('sse-' + estado);
  var legenda = el.querySelector('em');
  if (legenda) legenda.textContent = texto;
}

function tocarSomAdmin(tipo) {
  if (configAtual && configAtual.som_novo_pedido === false) return;
  try {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    if (!audioAvisoPedido) audioAvisoPedido = new Ctx();
    if (audioAvisoPedido.state === 'suspended') audioAvisoPedido.resume();

    var padroes = {
      pedido: [{ f: 880, d: .18 }, { f: 1040, d: .2 }],
      pagamento: [{ f: 660, d: .12 }, { f: 880, d: .12 }, { f: 1175, d: .22 }],
      suporte: [{ f: 520, d: .16 }, { f: 520, d: .16 }],
      alerta: [{ f: 740, d: .18 }]
    };
    var notas = padroes[tipo] || padroes.alerta;
    var inicio = audioAvisoPedido.currentTime;
    notas.forEach(function(nota, idx) {
      var comeco = inicio + idx * .2;
      var fim = comeco + nota.d;
      var osc = audioAvisoPedido.createOscillator();
      var ganho = audioAvisoPedido.createGain();
      osc.type = tipo === 'pagamento' ? 'triangle' : 'sine';
      osc.frequency.setValueAtTime(nota.f, comeco);
      ganho.gain.setValueAtTime(0.001, comeco);
      ganho.gain.exponentialRampToValueAtTime(tipo === 'suporte' ? 0.08 : 0.12, comeco + 0.02);
      ganho.gain.exponentialRampToValueAtTime(0.001, fim);
      osc.connect(ganho);
      ganho.connect(audioAvisoPedido.destination);
      osc.start(comeco);
      osc.stop(fim + 0.02);
    });
  } catch (e) {}
}

function tocarAvisoNovoPedido() {
  tocarSomAdmin('pedido');
}

async function expirarPixAutomaticamente() {
  if (!sessionStorage.getItem('token') || sessionStorage.getItem('tipo') !== 'admin') return;
  try {
    var r = await fetch(API + API_PREFIX + '/pedidos/pix/expirar', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: '{}'
    });
    var json = await r.json().catch(function() { return {}; });
    var total = json && json.data ? Number(json.data.total_expirados || 0) : 0;
    if (r.ok && total > 0) {
      ultimoPedidos = null;
      ultimoDashboard = null;
      await carregarTudo();
      mostrarToast('sucesso', total + ' Pix expirado(s) automaticamente.');
    }
  } catch (e) {
    console.warn('Expiração Pix:', e);
  }
}

function iniciarExpiracaoPixAutomatica() {
  if (timerExpiracaoPix || !sessionStorage.getItem('token') || sessionStorage.getItem('tipo') !== 'admin') return;
  expirarPixAutomaticamente();
  timerExpiracaoPix = setInterval(expirarPixAutomaticamente, 60000);
}

function iniciarSSEAdmin() {
  if (adminEvtSource || !sessionStorage.getItem('token') || sessionStorage.getItem('tipo') !== 'admin') return;
  if (!window.EventSource) {
    atualizarStatusSSE('offline', 'Sem suporte');
    return;
  }

  atualizarStatusSSE('reconnecting', 'Conectando...');

  adminEvtSource = new EventSource(API + API_PREFIX + '/events?token=' + encodeURIComponent(sessionStorage.getItem('token')));

  adminEvtSource.onopen = function() {
    atualizarStatusSSE('online', 'Online');
  };

  adminEvtSource.onmessage = async function(e) {
    try {
      var msg = JSON.parse(e.data);
      if (msg.type === 'connected') {
        atualizarStatusSSE('online', 'Online');
        return;
      }
      if (msg.type === 'refresh') {
        var payload = msg.payload || {};
        if (payload.acao === 'pedido_site_criado' || (payload.acao === 'criar_pedido' && payload.origem === 'site')) {
          await carregarDadosNovoPedido(payload.pedido_id || payload.id);
          tocarSomAdmin('pedido');
          mostrarToast('sucesso', 'Novo pedido do site recebido.');
          return;
        }

        if (payload.acao === 'pagamento_atualizado') {
          if (payload.status === 'pago' || payload.confirmacao_status === 'confirmado') {
            tocarSomAdmin('pagamento');
            mostrarToast('sucesso', 'Pagamento Pix confirmado.');
          }
        }

        if (payload.acao === 'mensagem_suporte') {
          tocarSomAdmin('suporte');
          if (typeof carregarSuporte === 'function') {
            await carregarSuporte();
          }
          if (typeof abrirSuporte === 'function' && typeof suporteAtual !== 'undefined' && Number(suporteAtual) === Number(payload.pedido_id)) {
            await abrirSuporte(suporteAtual, true);
          }
          return;
        }

        if (payload.acao === 'suporte_apagado') {
          if (typeof suporteAtual !== 'undefined' && Number(suporteAtual) === Number(payload.pedido_id)) {
            suporteAtual = null;
            var detalheSuporte = document.getElementById('suporteDetalhe');
            if (detalheSuporte) detalheSuporte.innerHTML = '<div class="support-empty">Selecione uma conversa para responder.</div>';
          }
          if (typeof carregarSuporte === 'function') {
            await carregarSuporte();
          }
          return;
        }

        var active = document.activeElement;
        var isEditing = active && (active.isContentEditable || active.tagName === 'INPUT' || active.tagName === 'SELECT' || active.tagName === 'TEXTAREA');
        if (!isEditing) {
          ultimoPedidos = null;
          ultimoDashboard = null;
          carregarTudo().then(function() {
            mostrarToast('sucesso', 'Dados atualizados em tempo real.');
          });
        }
      }
    } catch (err) {
      console.error('SSE:', err);
    }
  };

  adminEvtSource.onerror = function() {
    atualizarStatusSSE('reconnecting', 'Reconectando...');
    console.warn('SSE connection error');
  };

  adminEvtSource.addEventListener('ping', function() {
    atualizarStatusSSE('online', 'Online');
  });
}

if (sessionStorage.getItem('token') && sessionStorage.getItem('tipo') === 'admin') {
  carregarTudo();
  iniciarSSEAdmin();
  iniciarExpiracaoPixAutomatica();
}
