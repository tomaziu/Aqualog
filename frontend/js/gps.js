var adminMap = null;
var adminMarkers = {};
var adminRoutes = {};
var adminGpsIntervalo = null;

function carregarLeafletAdmin(callback) {
  if (window.L) { callback(); return; }
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

function adminMarkerIcon(cor) {
  return L.divIcon({
    className: 'tracking-marker-wrap',
    html: '<div class="tracking-marker" style="background:' + cor + ';box-shadow:0 2px 8px rgba(0,0,0,.4)"></div>',
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });
}

function gpsStatusBadge(status) {
  var mapa = {
    'aguardando_coleta': ['Aguardando', ''],
    'coletado': ['Coletado', ''],
    'em_rota': ['Em rota', 'rota'],
    'proximo_destino': ['Próximo', 'proximo'],
    'entregue': ['Entregue', ''],
    'cancelado': ['Cancelado', '']
  };
  var info = mapa[status] || [status, ''];
  return '<span class="gps-admin-badge ' + info[1] + '">' + info[0] + '</span>';
}

async function carregarGpsAdmin() {
  var dados1 = await apiGet('/deliveries?status=aguardando_coleta');
  var dados2 = await apiGet('/deliveries?status=coletado');
  var dados3 = await apiGet('/deliveries?status=em_rota');
  var dados4 = await apiGet('/deliveries?status=proximo_destino');

  var entregas = [].concat(
    Array.isArray(dados1) ? dados1 : [],
    Array.isArray(dados2) ? dados2 : [],
    Array.isArray(dados3) ? dados3 : [],
    Array.isArray(dados4) ? dados4 : []
  );

  var comLocalizacao = entregas.filter(function(e) {
    return e.entregador_latitude && e.entregador_longitude;
  });

  var emRota = entregas.filter(function(e) {
    return e.status === 'em_rota' || e.status === 'proximo_destino';
  }).length;

  var entregadoresAtivos = new Set(comLocalizacao.map(function(e) { return e.entregador_id; })).size;

  $('gpsEntregadoresAtivos').textContent = entregadoresAtivos;
  $('gpsEmRota').textContent = emRota;

  carregarLeafletAdmin(function() {
    var el = $('adminTrackingMap');
    if (!adminMap) {
      el.innerHTML = '';
      el.style.height = '520px';
      adminMap = L.map('adminTrackingMap', { zoomControl: true }).setView([-3.5, -43.5], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
      }).addTo(adminMap);
      setTimeout(function() { adminMap.invalidateSize(); }, 200);
    } else {
      setTimeout(function() { adminMap.invalidateSize(); }, 100);
    }

    var novosIds = {};
    comLocalizacao.forEach(function(e) {
      novosIds[e.id] = true;
      var lat = Number(e.entregador_latitude);
      var lng = Number(e.entregador_longitude);
      var cor = e.status === 'em_rota' || e.status === 'proximo_destino' ? '#f59e0b' : '#06b6d4';
      var label = '#' + e.id + ' - ' + (e.entregador_nome || 'Entregador');

      if (!adminMarkers[e.id]) {
        adminMarkers[e.id] = L.marker([lat, lng], { icon: adminMarkerIcon(cor), title: label }).addTo(adminMap);
        adminMarkers[e.id].bindPopup('<strong>' + label + '</strong><br>' + (e.destino_endereco || '') + '<br>' + gpsStatusBadge(e.status));
      } else {
        adminMarkers[e.id].setLatLng([lat, lng]);
        adminMarkers[e.id].setIcon(adminMarkerIcon(cor));
        adminMarkers[e.id].setPopupContent('<strong>' + label + '</strong><br>' + (e.destino_endereco || '') + '<br>' + gpsStatusBadge(e.status));
      }

      var coords = [
        [Number(e.origem_latitude), Number(e.origem_longitude)],
        [lat, lng],
        [Number(e.destino_latitude), Number(e.destino_longitude)]
      ].filter(function(c) { return c[0] && c[1]; });

      if (!adminRoutes[e.id]) {
        adminRoutes[e.id] = L.polyline(coords, { color: '#2563eb', weight: 4, opacity: .7, dashArray: '8,6' }).addTo(adminMap);
      } else {
        adminRoutes[e.id].setLatLngs(coords);
      }
    });

    Object.keys(adminMarkers).forEach(function(id) {
      if (!novosIds[id]) {
        adminMap.removeLayer(adminMarkers[id]);
        delete adminMarkers[id];
      }
      if (!novosIds[id] && adminRoutes[id]) {
        adminMap.removeLayer(adminRoutes[id]);
        delete adminRoutes[id];
      }
    });

    if (comLocalizacao.length) {
      var bounds = L.latLngBounds(comLocalizacao.map(function(e) {
        return [Number(e.entregador_latitude), Number(e.entregador_longitude)];
      }));
      adminMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  });

  var lista = $('gpsListaEntregas');
  if (!entregas.length) {
    lista.innerHTML = '<div class="tracking-map-empty">Nenhuma entrega ativa no momento.</div>';
    return;
  }
  lista.innerHTML = entregas.map(function(e) {
    var endereco = [e.destino_endereco, e.destino_latitude ? '(' + Number(e.destino_latitude).toFixed(4) + ', ' + Number(e.destino_longitude).toFixed(4) + ')' : ''].filter(Boolean).join(' ');
    var temGps = e.entregador_latitude ? 'Sim' : 'Não';
    return '<div class="gps-admin-card" onclick="focarEntregaAdmin(' + e.id + ', ' + Number(e.entregador_latitude || e.destino_latitude) + ', ' + Number(e.entregador_longitude || e.destino_longitude) + ')">' +
      '<strong>#' + e.id + ' - ' + escapeHtml(e.entregador_nome || 'Sem entregador') + '</strong>' +
      '<span>' + escapeHtml(e.cliente_nome || '') + ' | ' + escapeHtml(e.entregador_veiculo || '') + '</span>' +
      '<span>GPS: ' + temGps + '</span>' +
      gpsStatusBadge(e.status) +
    '</div>';
  }).join('');
}

function focarEntregaAdmin(id, lat, lng) {
  if (!adminMap || !lat || !lng) return;
  adminMap.setView([lat, lng], 16);
  if (adminMarkers[id]) {
    adminMarkers[id].openPopup();
  }
}

function iniciarGpsAdmin() {
  carregarGpsAdmin();
  if (adminGpsIntervalo) clearInterval(adminGpsIntervalo);
  adminGpsIntervalo = setInterval(carregarGpsAdmin, 8000);
}

function pararGpsAdmin() {
  if (adminGpsIntervalo) {
    clearInterval(adminGpsIntervalo);
    adminGpsIntervalo = null;
  }
}
