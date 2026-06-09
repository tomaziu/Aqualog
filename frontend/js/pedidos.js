var cachePedidos = [];
var ultimoPedidos = null;
var pedidoDestaqueId = null;

function pagamentoTexto(status) {
  var mapa = {
    'pago': 'Pago',
    'aguardando_pix': 'Aguardando Pix',
    'recusado': 'Recusado',
    'expirado': 'Expirado',
    'pix_erro': 'Erro no Pix',
    'nao_aplicavel': 'No ato'
  };
  return mapa[status] || status || 'No ato';
}

function confirmacaoTexto(status) {
  var mapa = {
    'confirmado': 'Confirmado',
    'aguardando_confirmacao': 'Confirmar cliente',
    'aguardando_pagamento': 'Aguardando Pix'
  };
  return mapa[status] || status || 'Confirmado';
}

function confirmacaoClasse(status) {
  if (status === 'confirmado' || !status) return 'confirm-ok';
  if (status === 'aguardando_pagamento') return 'confirm-pay';
  return 'confirm-wait';
}

function pedidoConfirmado(p) {
  return (p.confirmacao_status || 'confirmado') === 'confirmado';
}

function pedidoFinalizado(p) {
  return p.status === 'entregue' || p.status === 'cancelado';
}

function pedidoPixPendente(p) {
  return (p.forma_pagamento || '').toLowerCase() === 'pix' && p.pagamento_status === 'aguardando_pix' && !pedidoFinalizado(p);
}

function renderConfirmacao(p) {
  var status = p.confirmacao_status || 'confirmado';
  var html = '<span class="confirm-badge ' + confirmacaoClasse(status) + '">' + confirmacaoTexto(status) + '</span>';
  if (status === 'aguardando_confirmacao' && p.status !== 'entregue' && p.status !== 'cancelado') {
    html += '<button class="confirm-action" onclick="confirmarPedido(' + p.id + ')" title="Confirmar que o cliente quer o pedido">&#10003; Confirmar</button>';
  }
  return html;
}

function renderCodigoEntrega(p) {
  if (!pedidoConfirmado(p)) {
    return '<span class="delivery-code locked" title="Código liberado só após confirmação ou Pix pago">Bloqueado</span>';
  }
  return '<span class="delivery-code ready" title="Código liberado para conferência na entrega"><span>Liberado</span><strong>' + escapeHtml(p.codigo_entrega || '-') + '</strong></span>';
}

async function carregarPedidos() {
  var dados = await apiGet('/pedidos');
  if (!Array.isArray(dados)) return;

  var dadosAtuais = JSON.stringify(dados);
  if (ultimoPedidos === dadosAtuais) {
    return; // Dados não mudaram
  }
  ultimoPedidos = dadosAtuais;
  cachePedidos = dados;
  filtrarPedidos();
}

function filtrarPedidos() {
  var q = ($('filtroPedido').value || '').toLowerCase();
  var filtrados = cachePedidos.filter(function(p) {
    return !q ||
      (p.cliente && p.cliente.toLowerCase().includes(q)) ||
      (p.entregador && p.entregador.toLowerCase().includes(q)) ||
      (p.bairro && p.bairro.toLowerCase().includes(q)) ||
      (p.produto && p.produto.toLowerCase().includes(q)) ||
      (p.status && statusTexto(p.status).toLowerCase().includes(q));
  });

  function classePedido(s) {
    var mapa = {
      'aguardando_entregador': 'pedido-card-waiting',
      'separando': 'pedido-card-separating',
      'saiu_para_entrega': 'pedido-card-delivery',
      'em_preparo': 'pedido-card-prep',
      'entregue': 'pedido-card-done',
      'cancelado': 'pedido-card-canceled'
    };
    return mapa[s] || 'pedido-card-new';
  }

  function mostraOcupado(p) {
    if (p.entregador_status !== 'ocupado') return '';
    if (p.status === 'entregue' || p.status === 'cancelado') return '';
    return ' <span class="badge" style="background:#ffebee;color:#c62828;font-size:11px;padding:2px 8px">ocupado</span>';
  }

  function selectEntregador(p) {
    var desabilitado = p.status === 'entregue' || p.status === 'cancelado' || !pedidoConfirmado(p);
    var titulo = !pedidoConfirmado(p) ? 'Confirme o pedido antes de escolher entregador' : '';
    var atual = p.entregador_id ? String(p.entregador_id) : '';
    var opcoes = '<option value="">Sem entregador</option>' + cacheEntregadores.map(function(e) {
      var selected = String(e.id) === atual ? ' selected' : '';
      return '<option value="' + e.id + '"' + selected + '>' + escapeHtml(e.nome) + ' - ' + escapeHtml(e.status) + '</option>';
    }).join('');
    return '<div class="order-control-stack"><select class="select-inline select-entregador" onchange="atribuirEntregador(' + p.id + ', this.value)" title="' + titulo + '"' + (desabilitado ? ' disabled' : '') + '>' + opcoes + '</select>' + mostraOcupado(p) + '</div>';
  }

  function pagamentoTexto(status) {
    var mapa = {
      'pago': 'Pago',
      'aguardando_pix': 'Aguardando Pix',
      'recusado': 'Recusado',
      'expirado': 'Expirado',
      'pix_erro': 'Erro no Pix',
      'nao_aplicavel': 'No ato'
    };
    return mapa[status] || status || 'No ato';
  }

  function pagamentoClasse(status) {
    if (status === 'pago') return 'pay-ok';
    if (status === 'aguardando_pix') return 'pay-wait';
    if (status === 'recusado' || status === 'expirado' || status === 'pix_erro') return 'pay-bad';
    return 'pay-manual';
  }

  function renderPagamento(p) {
    var status = p.pagamento_status || 'nao_aplicavel';
    var html = '<div class="order-control-stack"><span class="payment-badge ' + pagamentoClasse(status) + '">' + escapeHtml(p.forma_pagamento || '-') + ' - ' + pagamentoTexto(status) + '</span>';
    if ((p.forma_pagamento || '').toLowerCase() === 'pix' && p.mp_order_id && status === 'aguardando_pix' && !pedidoFinalizado(p)) {
      html += '<button class="edit verify-payment" onclick="atualizarPagamento(' + p.id + ')">&#8635; Verificar</button>';
    }
    if (Number(p.comprovantes || 0) > 0) {
      html += '<button class="secondary-action proof-btn" onclick="abrirComprovantesPedido(' + p.id + ')">Comprovante ' + Number(p.comprovantes || 0) + '</button>';
    }
    return html + '</div>';
  }

  function opcoesStatus(p) {
    var opcoes = [
      ['recebido', 'Recebido'],
      ['aguardando_entregador', 'Aguardando entregador'],
      ['separando', 'Separando'],
      ['em_preparo', 'Em preparo'],
      ['saiu_para_entrega', 'Saiu p/ entrega'],
      ['entregue', 'Entregue'],
      ['cancelado', 'Cancelado']
    ];
    if (!pedidoConfirmado(p)) {
      opcoes = [
        ['recebido', 'Recebido'],
        ['cancelado', 'Cancelado']
      ];
    }
    return opcoes.map(function(op) {
      return '<option value="' + op[0] + '">' + op[1] + '</option>';
    }).join('');
  }

  if (!filtrados.length) {
    window.idsPedidosVisiveis = [];
    $('listaPedidos').innerHTML = '<div class="empty-list">Nenhum pedido encontrado.</div>';
    atualizarResumoSelecaoMassa('pedidos');
    return;
  }

  window.idsPedidosVisiveis = filtrados.map(function(p) { return p.id; });
  $('listaPedidos').innerHTML = filtrados.map(function(p) {
    var statusBloqueado = pedidoFinalizado(p);
    var destaque = Number(p.id) === Number(pedidoDestaqueId) ? ' pedido-card-highlight' : '';
    var cancelarTexto = pedidoPixPendente(p) ? 'Cancelar Pix' : 'Cancelar pedido';
    var cancelarBotao = statusBloqueado ? '' : '<button class="secondary-action danger-soft" onclick="cancelarPedido(' + p.id + ')">' + cancelarTexto + '</button>';
    var totalPedido = Number(p.total || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    var desconto = Number(p.desconto_valor || 0);
    var descontoTexto = desconto > 0 ? ' | Cupom ' + escapeHtml(p.cupom_codigo || '') + ': -' + desconto.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : '';
    return '<article class="pedido-card ' + classePedido(p.status) + destaque + '" data-pedido-id="' + p.id + '">' +
      '<div class="pedido-head">' +
        '<label class="pedido-id">' + checkboxMassaHtml('pedidos', p.id, 'Selecionar pedido ' + p.id) + '<strong>#' + p.id + '</strong></label>' +
        '<div class="pedido-main"><strong>' + escapeHtml(p.cliente || '-') + '</strong><span>' + escapeHtml(p.produto || '-') + ' | Total: ' + totalPedido + descontoTexto + '</span></div>' +
        '<div class="pedido-date"><span>Data</span><strong>' + formatarData(p.data_criacao) + '</strong></div>' +
      '</div>' +
      '<div class="pedido-grid">' +
        '<div class="pedido-info pedido-entregador"><span>Entregador</span>' + selectEntregador(p) + '</div>' +
        '<div class="pedido-info"><span>Pagamento</span>' + renderPagamento(p) + '</div>' +
        '<div class="pedido-info"><span>Confirmação</span><div class="order-control-stack">' + renderConfirmacao(p) + '</div></div>' +
        '<div class="pedido-info"><span>Bairro</span><strong>' + escapeHtml(p.bairro || '-') + '</strong></div>' +
        '<div class="pedido-info"><span>Código</span>' + renderCodigoEntrega(p) + '</div>' +
        '<div class="pedido-info"><span>Status</span><strong>' + statusTexto(p.status) + '</strong></div>' +
      '</div>' +
      '<div class="pedido-actions">' +
        '<select onchange="mudarStatus(' + p.id + ', this.value)"' + (statusBloqueado ? ' disabled' : '') + '>' +
          '<option value="">Alterar status</option>' +
          opcoesStatus(p) +
        '</select>' +
        '<button class="secondary-action" onclick="abrirHistoricoPedido(' + p.id + ')">Histórico</button>' +
        cancelarBotao +
        '<button class="delete" onclick="excluirPedido(' + p.id + ')">Excluir</button>' +
      '</div>' +
    '</article>';
  }).join('');
  atualizarResumoSelecaoMassa('pedidos');

  if (pedidoDestaqueId) {
    setTimeout(function() {
      var card = document.querySelector('[data-pedido-id="' + pedidoDestaqueId + '"]');
      if (card && typeof card.scrollIntoView === 'function') {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 80);
  }
}

async function confirmarPedido(id) {
  var resposta = await apiSend('/pedidos/' + id + '/confirmacao', 'PATCH', {});
  if (resposta) {
    ultimoPedidos = null;
    await carregarTudo();
    mostrarToast('sucesso', resposta.mensagem || 'Pedido confirmado.');
  }
}

async function atualizarPagamento(id) {
  var resposta = await apiSend('/pedidos/' + id + '/pagamento/atualizar', 'PATCH', {});
  if (resposta) {
    ultimoPedidos = null;
    await carregarTudo();
    mostrarToast('sucesso', 'Pagamento atualizado: ' + pagamentoTexto(resposta.pagamento_status));
  }
}

async function cancelarPedido(id) {
  var motivo = prompt('Motivo do cancelamento:', 'Cliente desistiu');
  if (motivo === null) return;
  if (!confirm('Cancelar este pedido e devolver o estoque?')) return;
  var resposta = await apiSend('/pedidos/' + id + '/cancelar', 'PATCH', { motivo: motivo });
  if (resposta) {
    ultimoPedidos = null;
    await carregarTudo();
    mostrarToast('sucesso', resposta.mensagem || 'Pedido cancelado.');
  }
}

async function abrirComprovantesPedido(id) {
  var modal = $('historicoModal');
  var titulo = $('historicoTitulo');
  var conteudo = $('historicoConteudo');
  if (!modal || !conteudo) return;
  if (titulo) titulo.textContent = 'Comprovantes do pedido #' + id;
  conteudo.innerHTML = '<div class="empty-list">Carregando comprovantes...</div>';
  modal.classList.add('ativo');
  modal.setAttribute('aria-hidden', 'false');

  var comprovantes = await apiGet('/pedidos/' + id + '/comprovantes');
  if (!Array.isArray(comprovantes) || !comprovantes.length) {
    conteudo.innerHTML = '<div class="empty-list">Nenhum comprovante enviado.</div>';
    return;
  }
  conteudo.innerHTML = comprovantes.map(function(c) {
    var texto = String(c.conteudo || '');
    var preview = texto.startsWith('data:image/')
      ? '<img class="proof-preview" src="' + texto + '" alt="Comprovante Pix">'
      : '<pre class="proof-text">' + escapeHtml(texto) + '</pre>';
    return '<div class="history-item proof-item">' +
      '<strong>' + escapeHtml(c.arquivo_nome || 'Comprovante') + '</strong>' +
      '<span>' + formatarData(c.criado_em) + '</span>' +
      preview +
    '</div>';
  }).join('');
}

async function atribuirEntregador(id, valorEntregador) {
  var entregadorId = valorEntregador ? Number(valorEntregador) : null;
  var resposta = await apiSend('/pedidos/' + id + '/entregador', 'PATCH', { entregador_id: entregadorId });
  if (resposta) {
    ultimoPedidos = null;
    await carregarTudo();
    mostrarToast('sucesso', entregadorId ? 'Entregador atribuido ao pedido.' : 'Pedido sem entregador.');
  }
}

async function mudarStatus(id, status) {
  if (!status) return;
  var resposta = await apiSend('/pedidos/' + id + '/status?status=' + encodeURIComponent(status), 'PATCH', {});
  if (resposta) {
    mostrarToast('sucesso', resposta.mensagem || 'Status atualizado!');
  }
  await carregarTudo();
}

async function excluirPedido(id) {
  if (!confirm('Deseja excluir este pedido?')) return;
  if (await apiDelete('/pedidos/' + id)) {
    await carregarTudo();
    mostrarToast('sucesso', 'Pedido excluido com sucesso!');
  }
}

async function excluirPedidosSelecionados() {
  await excluirSelecionadosMassa('pedidos', 'pedidos', '/pedidos', async function() {
    ultimoPedidos = null;
    await carregarTudo();
  });
}

async function expirarPixPendentes() {
  var resposta = await apiSend('/pedidos/pix/expirar', 'POST', {});
  if (resposta) {
    ultimoPedidos = null;
    ultimoDashboard = null;
    await carregarTudo();
    mostrarToast('sucesso', resposta.total_expirados ? resposta.total_expirados + ' Pix expirado(s).' : 'Nenhum Pix antigo para expirar.');
  }
}

async function limparPedidosAntigos() {
  if (!confirm('Remover pedidos entregues/cancelados com mais de 30 dias?')) return;
  var ok = await apiDelete('/pedidos/limpeza/finalizados?dias=30');
  if (ok) {
    ultimoPedidos = null;
    ultimoDashboard = null;
    await carregarTudo();
    mostrarToast('sucesso', 'Limpeza concluída.');
  }
}

async function abrirHistoricoPedido(id) {
  var modal = $('historicoModal');
  var titulo = $('historicoTitulo');
  var conteudo = $('historicoConteudo');
  if (!modal || !conteudo) return;
  if (titulo) titulo.textContent = 'Histórico do pedido #' + id;
  conteudo.innerHTML = '<div class="empty-list">Carregando histórico...</div>';
  modal.classList.add('ativo');
  modal.setAttribute('aria-hidden', 'false');

  var historico = await apiGet('/pedidos/' + id + '/historico');
  if (!Array.isArray(historico) || !historico.length) {
    conteudo.innerHTML = '<div class="empty-list">Nenhum histórico registrado.</div>';
    return;
  }
  conteudo.innerHTML = historico.map(function(item) {
    var movimento = escapeHtml((item.status_anterior || 'novo') + ' -> ' + (item.status_novo || '-'));
    return '<div class="history-item">' +
      '<strong>' + movimento + '</strong>' +
      '<span>' + escapeHtml(item.observacao || 'Sem observação') + '</span>' +
      '<span>' + formatarData(item.criado_em) + '</span>' +
    '</div>';
  }).join('');
}

function fecharHistoricoPedido() {
  var modal = $('historicoModal');
  if (!modal) return;
  modal.classList.remove('ativo');
  modal.setAttribute('aria-hidden', 'true');
}
