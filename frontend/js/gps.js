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

      if (!adminMarkers['entregador_' + e.id]) {
        adminMarkers['entregador_' + e.id] = L.marker([lat, lng], { icon: adminMarkerIcon(cor), title: label }).addTo(adminMap);
        adminMarkers['entregador_' + e.id].bindPopup('<strong>' + label + '</strong><br>' + (e.destino_endereco || '') + '<br>' + gpsStatusBadge(e.status));
      } else {
        adminMarkers['entregador_' + e.id].setLatLng([lat, lng]);
        adminMarkers['entregador_' + e.id].setIcon(adminMarkerIcon(cor));
        adminMarkers['entregador_' + e.id].setPopupContent('<strong>' + label + '</strong><br>' + (e.destino_endereco || '') + '<br>' + gpsStatusBadge(e.status));
      }

      if (e.cliente_atual_latitude && e.cliente_atual_longitude) {
        var cliLat = Number(e.cliente_atual_latitude);
        var cliLng = Number(e.cliente_atual_longitude);
        var cliLabel = 'Cliente - ' + (e.cliente_nome || '');
        if (!adminMarkers['cliente_' + e.id]) {
          adminMarkers['cliente_' + e.id] = L.marker([cliLat, cliLng], { icon: adminMarkerIcon('#10b981'), title: cliLabel }).addTo(adminMap);
          adminMarkers['cliente_' + e.id].bindPopup('<strong>' + cliLabel + '</strong><br>' + (e.destino_endereco || ''));
        } else {
          adminMarkers['cliente_' + e.id].setLatLng([cliLat, cliLng]);
        }
      }

      var coords = [
        [Number(e.origem_latitude), Number(e.origem_longitude)],
        [lat, lng],
        e.cliente_atual_latitude ? [Number(e.cliente_atual_latitude), Number(e.cliente_atual_longitude)] : null,
        [Number(e.destino_latitude), Number(e.destino_longitude)]
      ].filter(function(c) { return c && c[0] && c[1]; });

      if (!adminRoutes[e.id]) {
        adminRoutes[e.id] = L.polyline(coords, { color: '#2563eb', weight: 4, opacity: .7, dashArray: '8,6' }).addTo(adminMap);
      } else {
        adminRoutes[e.id].setLatLngs(coords);
      }
    });

    Object.keys(adminMarkers).forEach(function(key) {
      var id = key.split('_')[1];
      if (!novosIds[id]) {
        adminMap.removeLayer(adminMarkers[key]);
        delete adminMarkers[key];
      }
    });
    Object.keys(adminRoutes).forEach(function(id) {
      if (!novosIds[id]) {
        adminMap.removeLayer(adminRoutes[id]);
        delete adminRoutes[id];
      }
    });

    if (comLocalizacao.length) {
      var allCoords = [];
      comLocalizacao.forEach(function(e) {
        if (e.entregador_latitude) allCoords.push([Number(e.entregador_latitude), Number(e.entregador_longitude)]);
        if (e.cliente_atual_latitude) allCoords.push([Number(e.cliente_atual_latitude), Number(e.cliente_atual_longitude)]);
      });
      if (allCoords.length) {
        adminMap.fitBounds(L.latLngBounds(allCoords), { padding: [50, 50], maxZoom: 15 });
      }
    }
  });

  var lista = $('gpsListaEntregas');
  if (!entregas.length) {
    lista.innerHTML = '<div class="tracking-map-empty">Nenhuma entrega ativa no momento.</div>';
    return;
  }
  lista.innerHTML = entregas.map(function(e) {
    var temGpsEntregador = e.entregador_latitude ? 'Sim' : 'Não';
    var temGpsCliente = e.cliente_atual_latitude ? 'Sim' : 'Não';
    var latFoco = e.entregador_latitude || e.cliente_atual_latitude || e.destino_latitude;
    var lngFoco = e.entregador_longitude || e.cliente_atual_longitude || e.destino_longitude;
    return '<div class="gps-admin-card" onclick="focarEntregaAdmin(' + e.id + ', ' + Number(latFoco) + ', ' + Number(lngFoco) + ')">' +
      '<strong>#' + e.id + ' - ' + escapeHtml(e.cliente_nome || '') + '</strong>' +
      '<span>' + escapeHtml(e.entregador_nome || 'Sem entregador') + ' | ' + escapeHtml(e.entregador_veiculo || '') + '</span>' +
      '<span><i class="ph ph-motorcycle"></i> Entregador: ' + temGpsEntregador + ' | <i class="ph ph-user"></i> Cliente: ' + temGpsCliente + '</span>' +
      gpsStatusBadge(e.status) +
    '</div>';
  }).join('');
}

function focarEntregaAdmin(id, lat, lng) {
  if (!adminMap || !lat || !lng) return;
  adminMap.setView([lat, lng], 16);
  if (adminMarkers['entregador_' + id]) {
    adminMarkers['entregador_' + id].openPopup();
  } else if (adminMarkers['cliente_' + id]) {
    adminMarkers['cliente_' + id].openPopup();
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
