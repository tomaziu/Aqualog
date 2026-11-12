import re

with open(r'C:\Users\teste123\Downloads\aqualog_projeto\frontend\cliente.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove trackLink logic in renderPedidosSalvos
old_block = '''      box.innerHTML = pedidos.map(function(p) {
        var codigoResumo = p.codigo_entrega ? p.codigo_entrega : 'bloqueado';
        var trackLink = p.status === 'saiu_para_entrega'
          ? '<a href="rastreamento.html?entrega=' + encodeURIComponent(p.id) + '&telefone=' + encodeURIComponent(p.telefone) + '" target="_blank" onclick="event.stopPropagation()" style="color:#00e5ff;font-weight:700;text-decoration:none;margin-left:6px">Rastrear</a>'
          : '';
        return '<button class="saved-order" type="button" data-id="' + p.id + '" data-telefone="' + escapeHtml(p.telefone) + '" onclick="abrirPedidoSalvo(Number(this.dataset.id), this.dataset.telefone)">' +
          '<strong>Pedido #' + p.id + ' - ' + dinheiro(p.total) + trackLink + '</strong>' +
          '<span>' + escapeHtml(p.produto || 'Pedido') + ' | ' + formatarDataHora(p.criado_em) + ' | ' + escapeHtml(confirmacaoTexto(p.confirmacao_status)) + ' | C\u00f3digo: ' + escapeHtml(codigoResumo) + '</span>' +
        '</button>';
      }).join('');'''

new_block = '''      box.innerHTML = pedidos.map(function(p) {
        var codigoResumo = p.codigo_entrega ? p.codigo_entrega : 'bloqueado';
        return '<button class="saved-order" type="button" data-id="' + p.id + '" data-telefone="' + escapeHtml(p.telefone) + '" onclick="abrirPedidoSalvo(Number(this.dataset.id), this.dataset.telefone)">' +
          '<strong>Pedido #' + p.id + ' - ' + dinheiro(p.total) + '</strong>' +
          '<span>' + escapeHtml(p.produto || 'Pedido') + ' | ' + formatarDataHora(p.criado_em) + ' | ' + escapeHtml(confirmacaoTexto(p.confirmacao_status)) + ' | C\u00f3digo: ' + escapeHtml(codigoResumo) + '</span>' +
        '</button>';
      }).join('');'''

content = content.replace(old_block, new_block)

# 2. Remove trackUrl from renderAvisoRota
old_aviso = '''function renderAvisoRota(pedido) {
      if (!pedido || pedido.status !== 'saiu_para_entrega') return '';
      var trackUrl = 'rastreamento.html?entrega=' + encodeURIComponent(pedido.id) + '&telefone=' + encodeURIComponent(pedido.telefone || '');
      return '<div class="route-alert">' +
        '<div class="route-icon">&#10146;</div>' +
        '<div><strong>Entregador a caminho</strong><span>Seu pedido j\u00e1 saiu e est\u00e1 indo para o endere\u00e7o informado.</span>' +
        '<a href="' + trackUrl + '" target="_blank">Rastrear no mapa</a>' +
        '</div></div>';
    }'''

new_aviso = '''function renderAvisoRota(pedido) {
      if (!pedido || pedido.status !== 'saiu_para_entrega') return '';
      return '<div class="route-alert">' +
        '<div class="route-icon">&#10146;</div>' +
        '<div><strong>Entregador a caminho</strong><span>Seu pedido j\u00e1 saiu e est\u00e1 indo para o endere\u00e7o informado.</span>' +
        '</div></div>';
    }'''

content = content.replace(old_aviso, new_aviso)

# 3. Remove capturarLocalizacaoCliente function
old_capturar = '''    function capturarLocalizacaoCliente(forcarAviso) {
      if (!navigator.geolocation) {
        atualizarAvisoLocalizacao('indisponivel');
        return;
      }
      var geoNegado = localStorage.getItem('aqualog_geo_negado');
      if (geoNegado && !forcarAviso) {
        atualizarAvisoLocalizacao('negado');
        return;
      }
      if (forcarAviso) atualizarAvisoLocalizacao('pedir');
      navigator.geolocation.getCurrentPosition(function(pos) {
        clienteGeoAtual = {
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude
        };
        localStorage.removeItem('aqualog_geo_negado');
        atualizarAvisoLocalizacao('ok');
      }, function(err) {
        clienteGeoAtual = null;
        if (err && err.code === err.PERMISSION_DENIED) {
          localStorage.setItem('aqualog_geo_negado', '1');
          atualizarAvisoLocalizacao('negado');
        } else {
          atualizarAvisoLocalizacao('pedir');
        }
      }, { enableHighAccuracy: true, maximumAge: 60000, timeout: 10000 });
    }'''

content = content.replace(old_capturar, '')

# 4. Remove the call to capturarLocalizacaoCliente()
old_call = '''    restaurarDadosCliente();
    renderPedidosSalvos();
    prepararAutocompleteEnderecoCliente();
    capturarLocalizacaoCliente();
    abrirModoCliente('inicio');
    carregar();'''

new_call = '''    restaurarDadosCliente();
    renderPedidosSalvos();
    prepararAutocompleteEnderecoCliente();
    abrirModoCliente('inicio');
    carregar();'''

content = content.replace(old_call, new_call)

with open(r'C:\Users\teste123\Downloads\aqualog_projeto\frontend\cliente.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')