var entregasRastreamento = [];
var entregaSelecionadaId = null;
var trackingLeafletMap = null;
var trackingMarkers = {};
var trackingRoute = null;
var trackingPendente = null;
var trackingOrigemAtual = null;

var DELIVERY_LABELS = {
  aguardando_coleta: 'Aguardando coleta',
  coletado: 'Coletado',
  em_rota: 'Em rota',
  proximo_destino: 'Próximo ao destino',
  entregue: 'Entregue',
  cancelado: 'Cancelado'
};

function statusEntregaTexto(status) {
  return DELIVERY_LABELS[status] || status || 'Sem status';
}

function formatarTempoEntrega(segundos) {
  if (!segundos && segundos !== 0) return '--';
  var min = Math.max(0, Math.round(Number(segundos) / 60));
  if (min < 60) return min + ' min';
  return Math.floor(min / 60) + 'h ' + String(min % 60).padStart(2, '0') + 'min';
}

function formatarDistanciaEntrega(metros) {
  if (!metros && metros !== 0) return '--';
  if (Number(metros) < 1000) return Math.round(Number(metros)) + ' m';
  return (Number(metros) / 1000).toFixed(1).replace('.', ',') + ' km';
}

async function carregarRastreamento() {
  if (!sessionStorage.getItem('token') || sessionStorage.getItem('tipo') !== 'admin') return;
  preencherEntregadoresEntrega();
  preencherPedidosEntrega();
  var status = $('filtroEntregaStatus') ? $('filtroEntregaStatus').value : '';
  var busca = $('filtroEntregaBusca') ? $('filtroEntregaBusca').value.trim() : '';
  var url = '/deliveries';
  var qs = [];
  if (status) qs.push('status=' + encodeURIComponent(status));
  if (busca) qs.push('q=' + encodeURIComponent(busca));
  if (qs.length) url += '?' + qs.join('&');
  entregasRastreamento = await apiGet(url);
  renderizarEntregasRastreamento(entregasRastreamento);
  if (entregaSelecionadaId) {
    var atual = entregasRastreamento.find(function(e) { return Number(e.id) === Number(entregaSelecionadaId); });
    if (atual) selecionarEntregaRastreamento(atual.id, false);
  }
}

function preencherEntregadoresEntrega() {
  var select = $('entregaEntregadorId');
  if (!select) return;
  var lista = (typeof cacheEntregadores !== 'undefined' && Array.isArray(cacheEntregadores)) ? cacheEntregadores : [];
  var atual = select.value;
  select.innerHTML = '<option value="">Sem entregador</option>' + lista.map(function(e) {
    return '<option value="' + e.id + '">' + escapeHtml(e.nome) + ' - ' + escapeHtml(e.veiculo || '') + '</option>';
  }).join('');
  select.value = atual;
}

function preencherPedidosEntrega() {
  var select = $('entregaPedidoId');
  if (!select) return;
  var lista = (typeof cachePedidos !== 'undefined' && Array.isArray(cachePedidos)) ? cachePedidos : [];
  var atual = select.value;
  var abertos = lista.filter(function(p) {
    return p.status !== 'entregue' && p.status !== 'cancelado';
  });
  select.innerHTML = '<option value="">Selecione o pedido</option>' + abertos.map(function(p) {
    var endereco = [p.endereco, p.numero_casa, p.bairro].filter(Boolean).join(', ');
    return '<option value="' + p.id + '" data-entregador="' + (p.entregador_id || '') + '">' +
      '#' + p.id + ' - ' + escapeHtml(p.cliente || 'Cliente') + ' • ' + escapeHtml(endereco) +
      '</option>';
  }).join('');
  select.value = atual;
}

function usarLocalizacaoOrigem() {
  var status = $('entregaOrigemStatus');
  if (!navigator.geolocation) {
    status.textContent = 'Seu navegador não permite capturar localização.';
    return;
  }
  status.textContent = 'Solicitando permissão de localização...';
  navigator.geolocation.getCurrentPosition(function(pos) {
    trackingOrigemAtual = {
      latitude: pos.coords.latitude,
      longitude: pos.coords.longitude,
      accuracy: pos.coords.accuracy
    };
    window._adminGeoAtual = trackingOrigemAtual;
    status.textContent = 'Origem capturada: ' + pos.coords.latitude.toFixed(5) + ', ' + pos.coords.longitude.toFixed(5);
  }, function(err) {
    trackingOrigemAtual = null;
    status.textContent = err.code === err.PERMISSION_DENIED
      ? 'Permissão negada. Não dá para criar rastreamento automático sem origem.'
      : 'Não foi possível capturar sua localização agora.';
  }, { enableHighAccuracy: true, maximumAge: 3000, timeout: 12000 });
}

function filtrarRastreamentoLocal() {
  clearTimeout(window._trackingFilterTimer);
  window._trackingFilterTimer = setTimeout(carregarRastreamento, 250);
}

function renderizarEntregasRastreamento(lista) {
  var box = $('listaEntregas');
  if (!box) return;
  if (!lista.length) {
    box.innerHTML = '<div class="tracking-empty">Nenhuma entrega encontrada.</div>';
    return;
  }
  box.innerHTML = lista.map(function(e) {
    var selected = Number(e.id) === Number(entregaSelecionadaId) ? ' tracking-item-active' : '';
    return '<button type="button" class="tracking-item' + selected + '" onclick="selecionarEntregaRastreamento(' + e.id + ')">' +
      '<span class="tracking-item-main">' +
        '<strong>Entrega #' + e.id + '</strong>' +
        '<em>' + escapeHtml(e.cliente_nome || 'Cliente') + '</em>' +
      '</span>' +
      '<span class="tracking-pill tracking-pill-' + escapeHtml(e.status || '') + '">' + statusEntregaTexto(e.status) + '</span>' +
      '<small>' + escapeHtml(e.entregador_nome || 'Sem entregador') + ' • ' + escapeHtml(e.destino_endereco || '') + '</small>' +
    '</button>';
  }).join('');
}

function selecionarEntregaRastreamento(id, deveRenderizar) {
  entregaSelecionadaId = Number(id);
  var entrega = entregasRastreamento.find(function(e) { return Number(e.id) === Number(id); });
  if (!entrega) return;
  if (deveRenderizar !== false) renderizarEntregasRastreamento(entregasRastreamento);
  atualizarPainelEntrega(entrega);
}

function atualizarPainelEntrega(e) {
  $('trackingTitulo').textContent = 'Entrega #' + e.id + ' • ' + (e.cliente_nome || 'Cliente');
  $('trackingSubtitulo').textContent = e.destino_endereco || 'Destino não informado';
  $('trackingStatus').textContent = statusEntregaTexto(e.status);
  $('trackingStatus').className = 'tracking-status tracking-pill-' + (e.status || '');
  $('trackingEta').textContent = formatarTempoEntrega(e.eta_seconds);
  $('trackingDistancia').textContent = formatarDistanciaEntrega(e.distance_meters);
  $('trackingDriver').textContent = e.entregador_nome ? e.entregador_nome + ' • ' + (e.entregador_veiculo || '') : 'Sem entregador';
  $('trackingDecorrido').textContent = e.started_at ? formatarTempoEntrega((Date.now() - new Date(e.started_at).getTime()) / 1000) : '--';
  $('trackingCoords').innerHTML =
    '<strong>Origem:</strong> ' + Number(e.origem_latitude).toFixed(5) + ', ' + Number(e.origem_longitude).toFixed(5) +
    ' <strong>Destino:</strong> ' + Number(e.destino_latitude).toFixed(5) + ', ' + Number(e.destino_longitude).toFixed(5) +
    (e.entregador_latitude ? ' <strong>Entregador:</strong> ' + Number(e.entregador_latitude).toFixed(5) + ', ' + Number(e.entregador_longitude).toFixed(5) : '');
  desenharMapaEntrega(e);
}

function desenharMapaEntrega(e) {
  var el = $('trackingMap');
  if (!el) return;
  if (!window.L) {
    trackingPendente = e;
    el.innerHTML = '<div class="tracking-map-empty">Carregando mapa gratuito OpenStreetMap...</div>';
    return;
  }
  if (!trackingLeafletMap) {
    el.innerHTML = '';
    trackingLeafletMap = L.map('trackingMap', { zoomControl: true }).setView([Number(e.destino_latitude), Number(e.destino_longitude)], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap'
    }).addTo(trackingLeafletMap);
  }
  atualizarMarcador('origem', [Number(e.origem_latitude), Number(e.origem_longitude)], 'Origem');
  atualizarMarcador('destino', [Number(e.destino_latitude), Number(e.destino_longitude)], 'Destino');
  if (e.entregador_latitude) {
    atualizarMarcador('entregador', [Number(e.entregador_latitude), Number(e.entregador_longitude)], 'Entregador');
  }
  desenharRotaEntrega(e);
}

function marcadorIcone(nome) {
  return L.divIcon({
    className: 'tracking-marker-wrap',
    html: '<div class="tracking-marker tracking-marker-' + nome + '"></div>',
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
}

function atualizarMarcador(nome, latLng, label) {
  if (!trackingMarkers[nome]) {
    trackingMarkers[nome] = L.marker(latLng, { icon: marcadorIcone(nome), title: label }).addTo(trackingLeafletMap);
    trackingMarkers[nome].bindTooltip(label);
  } else {
    trackingMarkers[nome].setLatLng(latLng);
  }
}

function desenharRotaEntrega(e) {
  if (!trackingLeafletMap) return;
  var coords = [
    [Number(e.origem_latitude), Number(e.origem_longitude)],
    e.entregador_latitude ? [Number(e.entregador_latitude), Number(e.entregador_longitude)] : null,
    [Number(e.destino_latitude), Number(e.destino_longitude)]
  ].filter(Boolean);
  if (!trackingRoute) {
    trackingRoute = L.polyline(coords, { color: '#2563eb', weight: 5, opacity: .82 }).addTo(trackingLeafletMap);
  } else {
    trackingRoute.setLatLngs(coords);
  }
  trackingLeafletMap.fitBounds(L.latLngBounds(coords), { padding: [48, 48], maxZoom: 15 });
}

function processarEventoEntrega(payload) {
  var entrega = payload.delivery;
  if (!entrega) return;
  var idx = entregasRastreamento.findIndex(function(e) { return Number(e.id) === Number(entrega.id); });
  if (idx >= 0) entregasRastreamento[idx] = entrega;
  else entregasRastreamento.unshift(entrega);
  renderizarEntregasRastreamento(entregasRastreamento);
  if (Number(entregaSelecionadaId) === Number(entrega.id)) atualizarPainelEntrega(entrega);
}

function carregarLeafletSePossivel() {
  if (window.L || document.getElementById('leaflet-script')) return;
  var css = document.createElement('link');
  css.rel = 'stylesheet';
  css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  document.head.appendChild(css);
  var script = document.createElement('script');
  script.id = 'leaflet-script';
  script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  script.onload = function() {
    if (trackingPendente) desenharMapaEntrega(trackingPendente);
  };
  document.head.appendChild(script);
}

document.addEventListener('DOMContentLoaded', function() {
  carregarLeafletSePossivel();
  var form = $('formEntrega');
  if (!form) return;
  var pedidoSelect = $('entregaPedidoId');
  if (pedidoSelect) {
    pedidoSelect.addEventListener('change', function() {
      var opt = pedidoSelect.options[pedidoSelect.selectedIndex];
      var entregadorId = opt ? opt.getAttribute('data-entregador') : '';
      if (entregadorId && $('entregaEntregadorId')) $('entregaEntregadorId').value = entregadorId;
    });
  }
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    if (!trackingOrigemAtual) {
      usarLocalizacaoOrigem();
      mostrarToast('erro', 'Permita a localização para capturar a origem automaticamente.');
      return;
    }
    var payload = {
      pedido_id: Number($('entregaPedidoId').value),
      entregador_id: $('entregaEntregadorId').value ? Number($('entregaEntregadorId').value) : null,
      origem_endereco: 'Local atual da distribuidora',
      origem_latitude: trackingOrigemAtual.latitude,
      origem_longitude: trackingOrigemAtual.longitude
    };
    var criada = await apiSend('/deliveries/from-pedido', 'POST', payload);
    if (criada) {
      mostrarToast('sucesso', 'Rastreamento criado automaticamente.');
      form.reset();
      trackingOrigemAtual = null;
      $('entregaOrigemStatus').textContent = 'A origem será capturada pelo navegador. O destino vem do endereço do cliente.';
      await carregarRastreamento();
      selecionarEntregaRastreamento(criada.id);
    }
  });
});
