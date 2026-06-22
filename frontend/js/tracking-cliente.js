var clienteEntregaAtual = null;
var clienteWs = null;
var clienteMap = null;
var clienteMarkers = {};
var clienteRoute = null;
var clienteGpsWatchId = null;
var clienteGpsIntervalo = null;
var clienteGpsCompartilhando = false;

function clienteStatusTexto(status) {
  var labels = {
    aguardando_coleta: 'Aguardando coleta',
    coletado: 'Coletado',
    em_rota: 'Em rota',
    proximo_destino: 'Próximo ao destino',
    entregue: 'Entregue',
    cancelado: 'Cancelado'
  };
  return labels[status] || status || '--';
}

function clienteTempo(segundos) {
  if (!segundos && segundos !== 0) return '--';
  var min = Math.round(Number(segundos) / 60);
  return min < 60 ? min + ' min' : Math.floor(min / 60) + 'h ' + String(min % 60).padStart(2, '0') + 'min';
}

function clienteDistancia(metros) {
  if (!metros && metros !== 0) return '--';
  return Number(metros) < 1000 ? Math.round(Number(metros)) + ' m' : (Number(metros) / 1000).toFixed(1).replace('.', ',') + ' km';
}

async function buscarEntregaCliente(id, telefone) {
  $('clienteTrackingErro').textContent = '';
  var r = await fetch(window.location.origin + '/api/v1/site/deliveries/' + encodeURIComponent(id) + '?telefone=' + encodeURIComponent(telefone), { cache: 'no-cache' });
  var json = await r.json().catch(function() { return {}; });
  if (!r.ok) {
    $('clienteTrackingErro').textContent = json.detail || 'Não foi possível abrir essa entrega.';
    return;
  }
  clienteEntregaAtual = json.data;
  clienteEntregaAtual._telefone = telefone;
  renderClienteEntrega(clienteEntregaAtual);
  conectarClienteWs(id, telefone);
  iniciarClienteGps(id, telefone);
}

function renderClienteEntrega(e) {
  $('clienteTrackingTitulo').textContent = 'Entrega #' + e.id;
  $('clienteTrackingStatus').textContent = clienteStatusTexto(e.status);
  $('clienteTrackingDriver').textContent = e.entregador_nome || 'Aguardando entregador';
  $('clienteTrackingVeiculo').textContent = e.entregador_veiculo || '--';
  $('clienteTrackingEta').textContent = clienteTempo(e.eta_seconds);
  $('clienteTrackingDistancia').textContent = clienteDistancia(e.distance_meters);
  $('clienteTrackingDestino').textContent = e.destino_endereco || '--';
  desenharMapaCliente(e);
}

function carregarLeafletCliente(callback) {
  if (window.L) {
    callback();
    return;
  }
  if (!document.getElementById('leaflet-css')) {
    var css = document.createElement('link');
    css.id = 'leaflet-css';
    css.rel = 'stylesheet';
    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(css);
  }
  var script = document.getElementById('leaflet-script');
  if (!script) {
    script = document.createElement('script');
    script.id = 'leaflet-script';
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.onload = callback;
    document.head.appendChild(script);
  } else {
    script.addEventListener('load', callback, { once: true });
  }
}

function clienteIcone(nome) {
  return L.divIcon({
    className: 'tracking-marker-wrap',
    html: '<div class="tracking-marker tracking-marker-' + nome + '"></div>',
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
}

function atualizarMarcadorCliente(nome, latLng, label) {
  if (!clienteMarkers[nome]) {
    clienteMarkers[nome] = L.marker(latLng, { icon: clienteIcone(nome), title: label }).addTo(clienteMap);
    clienteMarkers[nome].bindTooltip(label);
  } else {
    clienteMarkers[nome].setLatLng(latLng);
  }
}

function desenharMapaCliente(e) {
  carregarLeafletCliente(function() {
    var el = $('clienteTrackingMap');
    if (!clienteMap) {
      el.innerHTML = '';
      clienteMap = L.map('clienteTrackingMap').setView([Number(e.destino_latitude), Number(e.destino_longitude)], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
      }).addTo(clienteMap);
    }
    atualizarMarcadorCliente('origem', [Number(e.origem_latitude), Number(e.origem_longitude)], 'Loja');
    atualizarMarcadorCliente('destino', [Number(e.destino_latitude), Number(e.destino_longitude)], 'Destino');
    if (e.entregador_latitude) {
      atualizarMarcadorCliente('entregador', [Number(e.entregador_latitude), Number(e.entregador_longitude)], 'Entregador');
    }
    if (e.cliente_atual_latitude) {
      atualizarMarcadorCliente('cliente', [Number(e.cliente_atual_latitude), Number(e.cliente_atual_longitude)], 'Você');
    }
    var pontos = [
      [Number(e.origem_latitude), Number(e.origem_longitude)],
      e.entregador_latitude ? [Number(e.entregador_latitude), Number(e.entregador_longitude)] : null,
      e.cliente_atual_latitude ? [Number(e.cliente_atual_latitude), Number(e.cliente_atual_longitude)] : null,
      [Number(e.destino_latitude), Number(e.destino_longitude)]
    ].filter(function(c) { return c && c[0] && c[1]; });

    desenharRotaCliente(pontos);
  });
}

async function desenharRotaCliente(pontos) {
  if (clienteRoute) {
    clienteMap.removeLayer(clienteRoute);
    clienteRoute = null;
  }
  if (pontos.length < 2) return;
  var coords = pontos.map(function(p) { return p[1] + ',' + p[0]; }).join(';');
  try {
    var r = await fetch('https://router.project-osrm.org/route/v1/driving/' + coords + '?overview=full&geometries=geojson');
    var json = await r.json();
    if (json.code === 'Ok' && json.routes && json.routes[0]) {
      var rota = json.routes[0].geometry.coordinates.map(function(c) { return [c[1], c[0]]; });
      clienteRoute = L.polyline(rota, { color: '#2563eb', weight: 5, opacity: .85 }).addTo(clienteMap);
    } else {
      clienteRoute = L.polyline(pontos, { color: '#2563eb', weight: 5, opacity: .82 }).addTo(clienteMap);
    }
  } catch (err) {
    clienteRoute = L.polyline(pontos, { color: '#2563eb', weight: 5, opacity: .82 }).addTo(clienteMap);
  }
  if (pontos.length) {
    clienteMap.fitBounds(L.latLngBounds(pontos), { padding: [44, 44], maxZoom: 15 });
  }
}

function iniciarClienteGps(deliveryId, telefone) {
  if (!navigator.geolocation || clienteGpsCompartilhando) return;
  clienteGpsCompartilhando = true;
  if (clienteGpsWatchId !== null) navigator.geolocation.clearWatch(clienteGpsWatchId);
  clienteGpsWatchId = navigator.geolocation.watchPosition(function(pos) {
    enviarLocalizacaoCliente(deliveryId, telefone, pos.coords);
  }, function() {}, { enableHighAccuracy: true, maximumAge: 5000, timeout: 12000 });
  if (clienteGpsIntervalo) clearInterval(clienteGpsIntervalo);
  clienteGpsIntervalo = setInterval(function() {
    if (clienteEntregaAtual) {
      navigator.geolocation.getCurrentPosition(function(pos) {
        enviarLocalizacaoCliente(deliveryId, telefone, pos.coords);
      }, function() {}, { enableHighAccuracy: true, timeout: 8000 });
    }
  }, 6000);
}

async function enviarLocalizacaoCliente(deliveryId, telefone, coords) {
  try {
    await fetch(window.location.origin + '/api/v1/site/deliveries/' + encodeURIComponent(deliveryId) + '/client-location?telefone=' + encodeURIComponent(telefone), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy
      })
    });
  } catch (e) {}
}

function conectarClienteWs(id, telefone) {
  if (!window.WebSocket) return;
  if (clienteWs) clienteWs.close();
  var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
  clienteWs = new WebSocket(proto + location.host + '/api/v1/deliveries/ws/' + encodeURIComponent(id) + '?telefone=' + encodeURIComponent(telefone));
  clienteWs.onmessage = function(event) {
    try {
      var payload = JSON.parse(event.data);
      if (payload.delivery) renderClienteEntrega(payload.delivery);
    } catch (e) {}
  };
  clienteWs.onopen = function() {
    clienteWs.send('online');
  };
}

document.addEventListener('DOMContentLoaded', function() {
  var params = new URLSearchParams(location.search);
  if (params.get('entrega') && params.get('telefone')) {
    $('clienteTrackingId').value = params.get('entrega');
    $('clienteTrackingTelefone').value = params.get('telefone');
    buscarEntregaCliente(params.get('entrega'), params.get('telefone'));
  }
  $('clienteTrackingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    buscarEntregaCliente($('clienteTrackingId').value, $('clienteTrackingTelefone').value);
  });
});
