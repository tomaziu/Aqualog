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

async function buscarRotaOSRM(pontos) {
  if (pontos.length < 2) return null;
  var coords = pontos.map(function(p) { return p[1] + ',' + p[0]; }).join(';');
  try {
    var r = await fetch('https://router.project-osrm.org/route/v1/driving/' + coords + '?overview=full&geometries=geojson');
    var json = await r.json();
    if (json.code === 'Ok' && json.routes && json.routes[0]) {
      return json.routes[0].geometry.coordinates.map(function(c) { return [c[1], c[0]]; });
    }
  } catch (e) {}
  return null;
}

async function desenharRotaReal(entregaId, pontos) {
  if (adminRoutes[entregaId]) {
    adminMap.removeLayer(adminRoutes[entregaId]);
  }
  var rotaReal = await buscarRotaOSRM(pontos);
  if (rotaReal) {
    adminRoutes[entregaId] = L.polyline(rotaReal, { color: '#2563eb', weight: 5, opacity: .85 }).addTo(adminMap);
  } else {
    adminRoutes[entregaId] = L.polyline(pontos, { color: '#2563eb', weight: 4, opacity: .7, dashArray: '8,6' }).addTo(adminMap);
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

      var pontos = [
        [Number(e.origem_latitude), Number(e.origem_longitude)],
        [lat, lng],
        e.cliente_atual_latitude ? [Number(e.cliente_atual_latitude), Number(e.cliente_atual_longitude)] : null,
        [Number(e.destino_latitude), Number(e.destino_longitude)]
      ].filter(function(c) { return c && c[0] && c[1]; });

      desenharRotaReal(e.id, pontos);
    });

    Object.keys(adminMarkers).forEach(function(key) {
      var parts = key.split('_');
      var id = parseInt(parts[parts.length - 1]);
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
