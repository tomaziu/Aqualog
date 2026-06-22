var chartStatus = null;
var chartBairros = null;
var ultimoDashboard = null;
var dashboardAnterior = null;
var lastUpdateTime = null;

function corStatus(status) {
  var mapa = {
    'recebido': '#ff9800',
    'aguardando_entregador': '#7e57c2',
    'separando': '#00acc1',
    'em_preparo': '#ffc107',
    'saiu_para_entrega': '#2196f3',
    'entregue': '#4caf50',
    'cancelado': '#f44336'
  };
  return mapa[status] || '#9e9e9e';
}

function statusLabel(s) {
  var mapa = {
    'recebido': 'Recebido',
    'aguardando_entregador': 'Aguard. entregador',
    'separando': 'Separando',
    'em_preparo': 'Em preparo',
    'saiu_para_entrega': 'Saiu p/ entrega',
    'entregue': 'Entregue',
    'cancelado': 'Cancelado'
  };
  return mapa[s] || s;
}

function dinheiroAdmin(valor) {
  return Number(valor || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function renderMetricList(id, dados, renderer, vazio) {
  var el = $(id);
  if (!el) return;
  if (!dados || !dados.length) {
    el.innerHTML = '<div class="metric-empty">' + escapeHtml(vazio) + '</div>';
    return;
  }
  el.innerHTML = dados.map(renderer).join('');
}

function iniciarSkeletonDashboard() {
  var ids = ['totalPedidos','pedidosSemEntregador','pedidosAguardandoPix','pedidosPagos','pedidosPixExpirados','totalVendido','vendasHoje','ticketMedio','vendasSemana','vendasMes','produtosEstoqueBaixo','tempoMedio'];
  ids.forEach(function(id) {
    var card = $(id);
    if (card && card.closest('.card')) {
      card.closest('.card').classList.add('card-skeleton');
    }
  });
}

function removerSkeletonDashboard() {
  document.querySelectorAll('.card-skeleton').forEach(function(c) {
    c.classList.remove('card-skeleton');
  });
}

function atualizarTrend(id, atual, anterior) {
  var el = $(id);
  if (!el) return;
  el.className = 'card-trend';
  if (anterior === undefined || anterior === null) return;
  var a = Number(atual) || 0;
  var b = Number(anterior) || 0;
  if (b === 0 && a === 0) return;
  if (b === 0) { el.classList.add('up'); el.textContent = '\u25B2 novo'; return; }
  var pct = ((a - b) / b) * 100;
  if (pct > 0) { el.classList.add('up'); el.textContent = '\u25B2 +' + Math.round(pct) + '%'; }
  else if (pct < 0) { el.classList.add('down'); el.textContent = '\u25BC ' + Math.round(pct) + '%'; }
  else { el.classList.add('neutral'); el.textContent = '\u2500 0%'; }
}

function atualizarLastUpdate() {
  var el = $('lastUpdate');
  if (!el || !lastUpdateTime) return;
  var diff = Math.floor((Date.now() - lastUpdateTime) / 1000);
  var texto;
  if (diff < 5) texto = 'Atualizado agora';
  else if (diff < 60) texto = 'Atualizado h\u00e1 ' + diff + 's';
  else texto = 'Atualizado h\u00e1 ' + Math.floor(diff / 60) + 'min';
  el.innerHTML = '<span class="dot"></span>' + texto;
}

setInterval(atualizarLastUpdate, 5000);

async function carregarDashboard() {
  iniciarSkeletonDashboard();
  var d = await apiGet('/dashboard');
  removerSkeletonDashboard();
  if (!d || Array.isArray(d)) return;

  var dadosAtuais = JSON.stringify(d);
  if (ultimoDashboard === dadosAtuais) return;
  dashboardAnterior = ultimoDashboard ? JSON.parse(ultimoDashboard) : null;
  ultimoDashboard = dadosAtuais;
  lastUpdateTime = Date.now();
  atualizarLastUpdate();

  var ids = ['totalPedidos','pedidosSemEntregador','pedidosAguardandoPix','pedidosPagos','pedidosPixExpirados','totalVendido','vendasHoje','ticketMedio','vendasSemana','vendasMes','produtosEstoqueBaixo','tempoMedio'];

  function setVal(id, val) {
    var el = $(id);
    if (!el) return;
    el.textContent = val;
    el.classList.remove('flash');
    void el.offsetWidth;
    el.classList.add('flash');
  }

  setVal('totalPedidos', d.total_pedidos ?? 0);
  setVal('tempoMedio', (d.tempo_medio_minutos ?? 0) + ' min');
  var indicadores = d.indicadores || {};
  setVal('pedidosAguardandoPix', indicadores.aguardando_pix ?? 0);
  setVal('pedidosPagos', indicadores.pagos ?? 0);
  setVal('pedidosSemEntregador', indicadores.sem_entregador ?? 0);
  setVal('pedidosPixExpirados', indicadores.pix_expirados ?? 0);
  var financeiro = d.financeiro || {};
  var estoqueBaixo = d.estoque_baixo || [];
  setVal('totalVendido', dinheiroAdmin(financeiro.total_vendido));
  setVal('ticketMedio', dinheiroAdmin(financeiro.ticket_medio));
  var periodos = d.financeiro_periodos || {};
  setVal('vendasHoje', dinheiroAdmin(periodos.hoje && periodos.hoje.total));
  setVal('vendasSemana', dinheiroAdmin(periodos.semana && periodos.semana.total));
  setVal('vendasMes', dinheiroAdmin(periodos.mes && periodos.mes.total));
  setVal('produtosEstoqueBaixo', estoqueBaixo.length);

  var ant = dashboardAnterior || {};
  var antInd = ant.indicadores || {};
  var antFin = ant.financeiro || {};
  var antPer = ant.financeiro_periodos || {};
  atualizarTrend('trendTotalPedidos', d.total_pedidos, ant.total_pedidos);
  atualizarTrend('trendSemEntregador', indicadores.sem_entregador, antInd.sem_entregador);
  atualizarTrend('trendAguardandoPix', indicadores.aguardando_pix, antInd.aguardando_pix);
  atualizarTrend('trendPagos', indicadores.pagos, antInd.pagos);
  atualizarTrend('trendExpirados', indicadores.pix_expirados, antInd.pix_expirados);
  atualizarTrend('trendTotalVendido', financeiro.total_vendido, antFin.total_vendido);
  atualizarTrend('trendVendasHoje', periodos.hoje && periodos.hoje.total, antPer.hoje && antPer.hoje.total);
  atualizarTrend('trendTicketMedio', financeiro.ticket_medio, antFin.ticket_medio);
  atualizarTrend('trendVendasSemana', periodos.semana && periodos.semana.total, antPer.semana && antPer.semana.total);
  atualizarTrend('trendVendasMes', periodos.mes && periodos.mes.total, antPer.mes && antPer.mes.total);
  atualizarTrend('trendEstoqueBaixo', estoqueBaixo.length, ant.estoque_baixo ? ant.estoque_baixo.length : undefined);
  atualizarTrend('trendTempoMedio', d.tempo_medio_minutos, ant.tempo_medio_minutos);

  renderMetricList('rankingProdutos', d.produtos_mais_vendidos || [], function(p, idx) {
    return '<div class="metric-row">' +
      '<span><b>' + (idx + 1) + '.</b> ' + escapeHtml(p.produto) + '</span>' +
      '<strong>' + Number(p.quantidade || 0) + ' un. | ' + dinheiroAdmin(p.total) + '</strong>' +
    '</div>';
  }, 'Nenhum produto pago ainda.');

  renderMetricList('listaEstoqueBaixo', estoqueBaixo, function(p) {
    return '<div class="metric-row stock-warning">' +
      '<span>' + escapeHtml(p.nome) + '</span>' +
      '<strong>' + Number(p.estoque || 0) + ' em estoque | mínimo ' + Number(p.estoque_minimo || 0) + '</strong>' +
    '</div>';
  }, 'Nenhum produto com estoque baixo.');

  renderMetricList('rankingCupons', d.cupons_relatorio || [], function(c, idx) {
    var ativo = Number(c.ativo) === 1 || c.ativo === true;
    var limite = c.limite_usos ? '/' + Number(c.limite_usos) : '';
    return '<div class="metric-row">' +
      '<span><b>' + (idx + 1) + '.</b> ' + escapeHtml(c.codigo) + ' <small>' + (ativo ? 'ativo' : 'inativo') + '</small></span>' +
      '<strong>' + Number(c.pedidos || 0) + ' pedidos | -' + dinheiroAdmin(c.desconto_total) + ' | ' + Number(c.usos || 0) + limite + ' usos</strong>' +
    '</div>';
  }, 'Nenhum cupom usado ainda.');

  renderMetricList('rankingEntregadores', d.entregadores_relatorio || [], function(e, idx) {
    return '<div class="metric-row">' +
      '<span><b>' + (idx + 1) + '.</b> ' + escapeHtml(e.nome) + '</span>' +
      '<strong>' + Number(e.entregas || 0) + ' entregas | ' + Number(e.tempo_medio || 0) + ' min</strong>' +
    '</div>';
  }, 'Nenhuma entrega finalizada ainda.');

  var statusData = (d.por_status ?? []).map(function(s) {
    return { label: statusLabel(s.status), value: s.total, color: corStatus(s.status) };
  });

  var bairroData = (d.roteirizacao_por_bairro ?? []).slice(0, 8).map(function(r) {
    return { label: r.bairro, value: r.entregas };
  });

  if (chartStatus) { chartStatus.destroy(); chartStatus = null; }
  if (chartBairros) { chartBairros.destroy(); chartBairros = null; }

  if (typeof Chart === 'undefined') {
    document.getElementById('graficoStatus').style.display = 'none';
    document.getElementById('graficoBairros').style.display = 'none';
    return;
  }

  var ctxStatus = document.getElementById('graficoStatus');
  var ctxBairros = document.getElementById('graficoBairros');

  try {
    if (ctxStatus && statusData.length) {
      chartStatus = new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
          labels: statusData.map(function(s) { return s.label; }),
          datasets: [{
            data: statusData.map(function(s) { return s.value; }),
            backgroundColor: statusData.map(function(s) { return s.color; }),
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { position: 'bottom', labels: { font: { size: 11 }, padding: 12 } }
          }
        }
      });
    }
  } catch (e) {
    console.error('Erro grafico status', e);
  }

  try {
    if (ctxBairros && bairroData.length) {
      chartBairros = new Chart(ctxBairros, {
        type: 'bar',
        data: {
          labels: bairroData.map(function(b) { return b.label; }),
          datasets: [{
            data: bairroData.map(function(b) { return b.value; }),
            backgroundColor: '#1565c0',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 11 } } },
            x: { ticks: { font: { size: 10 } } }
          }
        }
      });
    }
  } catch (e) {
    console.error('Erro grafico bairros', e);
  }
}
