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

function iconEntregador() {
  return L.divIcon({
    className: 'tracking-marker-wrap',
    html: '<div class="gps-icon-entregador"><i class="ph ph-motorcycle"></i></div>',
    iconSize: [36, 36],
    iconAnchor: [18, 18]
  });
}

function iconCliente() {
  return L.divIcon({
    className: 'tracking-marker-wrap',
    html: '<div class="gps-icon-cliente"><i class="ph ph-user"></i></div>',
    iconSize: [36, 36],
    iconAnchor: [18, 18]
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

async function buscarRotaOSRM(lat1, lng1, lat2, lng2) {
  try {
    var r = await fetch('https://router.project-osrm.org/route/v1/driving/' + lng1 + ',' + lat1 + ';' + lng2 + ',' + lat2 + '?overview=full&geometries=geojson');
    var json = await r.json();
    if (json.code === 'Ok' && json.routes && json.routes[0]) {
      return json.routes[0].geometry.coordinates.map(function(c) { return [c[1], c[0]]; });
    }
  } catch (e) {}
  return null;
}

async function desenharRotaEntrega(entregaId, lat1, lng1, lat2, lng2) {
  if (adminRoutes[entregaId]) {
    adminMap.removeLayer(adminRoutes[entregaId]);
    delete adminRoutes[entregaId];
  }
  var rotaReal = await buscarRotaOSRM(lat1, lng1, lat2, lng2);
  if (rotaReal) {
    adminRoutes[entregaId] = L.polyline(rotaReal, { color: '#06b6d4', weight: 5, opacity: .9 }).addTo(adminMap);
  } else {
    adminRoutes[entregaId] = L.polyline([[lat1, lng1], [lat2, lng2]], { color: '#06b6d4', weight: 4, opacity: .7, dashArray: '8,6' }).addTo(adminMap);
  }
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

  var comEntregador = entregas.filter(function(e) {
    return e.entregador_latitude && e.entregador_longitude;
  });

  var emRota = entregas.filter(function(e) {
    return e.status === 'em_rota' || e.status === 'proximo_destino';
  }).length;

  var entregadoresAtivos = new Set(comEntregador.map(function(e) { return e.entregador_id; })).size;

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

    var novosEntregador = {};
    var novosCliente = {};

    comEntregador.forEach(function(e) {
      var latE = Number(e.entregador_latitude);
      var lngE = Number(e.entregador_longitude);
      var labelE = (e.entregador_nome || 'Entregador') + ' #' + e.id;

      novosEntregador[e.id] = true;
      if (!adminMarkers['entregador_' + e.id]) {
        adminMarkers['entregador_' + e.id] = L.marker([latE, lngE], { icon: iconEntregador(), title: labelE }).addTo(adminMap);
        adminMarkers['entregador_' + e.id].bindPopup('<strong><i class="ph ph-motorcycle"></i> ' + labelE + '</strong><br>' + (e.entregador_veiculo || '') + '<br>' + gpsStatusBadge(e.status));
      } else {
        adminMarkers['entregador_' + e.id].setLatLng([latE, lngE]);
        adminMarkers['entregador_' + e.id].setPopupContent('<strong><i class="ph ph-motorcycle"></i> ' + labelE + '</strong><br>' + (e.entregador_veiculo || '') + '<br>' + gpsStatusBadge(e.status));
      }

      var latC = e.cliente_atual_latitude ? Number(e.cliente_atual_latitude) : Number(e.destino_latitude);
      var lngC = e.cliente_atual_latitude ? Number(e.cliente_atual_longitude) : Number(e.destino_longitude);
      var labelC = (e.cliente_nome || 'Cliente');

      novosCliente[e.id] = true;
      if (!adminMarkers['cliente_' + e.id]) {
        adminMarkers['cliente_' + e.id] = L.marker([latC, lngC], { icon: iconCliente(), title: labelC }).addTo(adminMap);
        adminMarkers['cliente_' + e.id].bindPopup('<strong><i class="ph ph-user"></i> ' + labelC + '</strong><br>' + (e.destino_endereco || ''));
      } else {
        adminMarkers['cliente_' + e.id].setLatLng([latC, lngC]);
        adminMarkers['cliente_' + e.id].setPopupContent('<strong><i class="ph ph-user"></i> ' + labelC + '</strong><br>' + (e.destino_endereco || ''));
      }

      desenharRotaEntrega(e.id, latE, lngE, latC, lngC);
    });

    Object.keys(adminMarkers).forEach(function(key) {
      var parts = key.split('_');
      var tipo = parts[0];
      var id = parseInt(parts[parts.length - 1]);
      if (tipo === 'entregador' && !novosEntregador[id]) {
        adminMap.removeLayer(adminMarkers[key]);
        delete adminMarkers[key];
      }
      if (tipo === 'cliente' && !novosCliente[id]) {
        adminMap.removeLayer(adminMarkers[key]);
        delete adminMarkers[key];
      }
    });
    Object.keys(adminRoutes).forEach(function(id) {
      if (!novosEntregador[id]) {
        adminMap.removeLayer(adminRoutes[id]);
        delete adminRoutes[id];
      }
    });

    if (comEntregador.length) {
      var allCoords = [];
      comEntregador.forEach(function(e) {
        allCoords.push([Number(e.entregador_latitude), Number(e.entregador_longitude)]);
        var latC = e.cliente_atual_latitude ? Number(e.cliente_atual_latitude) : Number(e.destino_latitude);
        var lngC = e.cliente_atual_latitude ? Number(e.cliente_atual_longitude) : Number(e.destino_longitude);
        allCoords.push([latC, lngC]);
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
      '<button class="gps-admin-delete" onclick="event.stopPropagation();deletarEntregaGps(' + e.id + ')" title="Remover rastreamento">&times;</button>' +
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

async function deletarEntregaGps(id) {
  mostrarConfirm('Remover rastreamento', 'Removerá o rastreamento da entrega #' + id + ' do mapa. Continuar?', async function() {
    var r = await apiSend('/deliveries/' + id, 'DELETE');
    if (r) {
      if (adminMarkers['entregador_' + id]) { adminMap.removeLayer(adminMarkers['entregador_' + id]); delete adminMarkers['entregador_' + id]; }
      if (adminMarkers['cliente_' + id]) { adminMap.removeLayer(adminMarkers['cliente_' + id]); delete adminMarkers['cliente_' + id]; }
      if (adminRoutes[id]) { adminMap.removeLayer(adminRoutes[id]); delete adminRoutes[id]; }
      mostrarToast('sucesso', 'Entrega #' + id + ' removida do mapa.');
      carregarGpsAdmin();
    }
  });
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

async function limparEntregasAntigasGps() {
  mostrarConfirm('Limpar rastreamentos antigos', 'Removerá todas as entregas finalizadas ou canceladas e seu histórico de localização. Continuar?', async function() {
    var r = await apiSend('/deliveries/old', 'DELETE');
    if (r) {
      mostrarToast('sucesso', r.entregas_removidas + ' entregas, ' + r.localizacoes_removidas + ' localizações e ' + r.historico_removido + ' registros de histórico removidos.');
      carregarGpsAdmin();
    }
  });
}
