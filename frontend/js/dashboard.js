var chartStatus = null;
var chartBairros = null;
var ultimoDashboard = null;

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

async function carregarDashboard() {
  var d = await apiGet('/dashboard');
  if (!d || Array.isArray(d)) return;

  // Verifica se os dados mudaram
  var dadosAtuais = JSON.stringify(d);
  if (ultimoDashboard === dadosAtuais) {
    return; // Dados não mudaram, não atualiza
  }
  ultimoDashboard = dadosAtuais;

  $('totalPedidos').textContent = d.total_pedidos ?? 0;
  $('tempoMedio').textContent = (d.tempo_medio_minutos ?? 0) + ' min';
  var indicadores = d.indicadores || {};
  $('pedidosAguardandoPix').textContent = indicadores.aguardando_pix ?? 0;
  $('pedidosPagos').textContent = indicadores.pagos ?? 0;
  $('pedidosSemEntregador').textContent = indicadores.sem_entregador ?? 0;
  $('pedidosPixExpirados').textContent = indicadores.pix_expirados ?? 0;
  var financeiro = d.financeiro || {};
  var estoqueBaixo = d.estoque_baixo || [];
  $('totalVendido').textContent = dinheiroAdmin(financeiro.total_vendido);
  $('ticketMedio').textContent = dinheiroAdmin(financeiro.ticket_medio);
  var periodos = d.financeiro_periodos || {};
  $('vendasHoje').textContent = dinheiroAdmin(periodos.hoje && periodos.hoje.total);
  $('vendasSemana').textContent = dinheiroAdmin(periodos.semana && periodos.semana.total);
  $('vendasMes').textContent = dinheiroAdmin(periodos.mes && periodos.mes.total);
  $('produtosEstoqueBaixo').textContent = estoqueBaixo.length;

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
