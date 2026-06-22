const $ = function(id) { return document.getElementById(id); };

function valor(id) {
  var el = $(id);
  return el ? el.value.trim() : '';
}

function numero(id) {
  var n = Number(valor(id));
  return Number.isFinite(n) ? n : 0;
}

function escapeHtml(valor) {
  return String(valor ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function lerCelula(idLinha, campo) {
  var el = document.querySelector('[data-linha="' + idLinha + '"][data-campo="' + campo + '"]');
  if (!el) return '';
  var inp = el.querySelector('input');
  return inp ? inp.value.trim() : el.textContent.trim();
}

function lerSelect(idLinha, campo) {
  var el = document.querySelector('[data-linha="' + idLinha + '"][data-campo="' + campo + '"]');
  return el ? el.value : '';
}

function formatarData(d) {
  if (!d) return '-';
  var dt = new Date(d);
  return dt.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusTexto(s) {
  var map = {
    'recebido': 'Recebido',
    'aguardando_entregador': 'Aguardando entregador',
    'separando': 'Separando',
    'em_preparo': 'Em preparo',
    'saiu_para_entrega': 'Saiu p/ entrega',
    'entregue': 'Entregue',
    'cancelado': 'Cancelado'
  };
  return map[s] || s;
}

function mostrarTela(id, recarregar) {
  document.querySelectorAll('.tela').forEach(function(t) { t.classList.remove('ativa'); });
  $(id).classList.add('ativa');
  document.querySelectorAll('.sidebar-nav button').forEach(function(btn) {
    btn.classList.remove('ativo');
    if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes("'" + id + "'")) {
      btn.classList.add('ativo');
    }
  });
  if (id === 'gps' && typeof iniciarGpsAdmin === 'function') {
    iniciarGpsAdmin();
  } else if (typeof pararGpsAdmin === 'function') {
    pararGpsAdmin();
  }
  if (recarregar !== false) {
    carregarTudo();
  }
}

function toggleSidebar() {
  var sidebar = document.getElementById('sidebar');
  if (sidebar.classList.contains('mobile-show')) {
    sidebar.classList.remove('mobile-show');
    sidebar.classList.add('mobile-hidden');
  } else {
    sidebar.classList.remove('mobile-hidden');
    sidebar.classList.add('mobile-show');
  }
}

function formatarTelefoneDisplay(tel) {
  var d = String(tel).replace(/\D/g, '');
  if (d.length === 11) return '(' + d.slice(0,2) + ') ' + d.slice(2,7) + '-' + d.slice(7);
  if (d.length === 10) return '(' + d.slice(0,2) + ') ' + d.slice(2,6) + '-' + d.slice(6);
  return tel;
}

var selecoesMassa = {};

function obterSelecaoMassa(grupo) {
  if (!selecoesMassa[grupo]) selecoesMassa[grupo] = {};
  return selecoesMassa[grupo];
}

function idsSelecionadosMassa(grupo) {
  return Object.keys(obterSelecaoMassa(grupo)).map(function(id) { return Number(id); });
}

function checkboxMassaHtml(grupo, id, rotulo) {
  var marcado = obterSelecaoMassa(grupo)[id] ? ' checked' : '';
  return '<input class="bulk-check" type="checkbox" data-grupo="' + grupo + '" data-id="' + id + '" aria-label="' + escapeHtml(rotulo) + '" onchange="alternarSelecaoMassa(\'' + grupo + '\', ' + id + ', this.checked)"' + marcado + '>';
}

function alternarSelecaoMassa(grupo, id, marcado) {
  var selecao = obterSelecaoMassa(grupo);
  if (marcado) {
    selecao[id] = true;
  } else {
    delete selecao[id];
  }
  atualizarResumoSelecaoMassa(grupo);
}

function alternarSelecaoVisivelMassa(grupo, ids, marcado) {
  var selecao = obterSelecaoMassa(grupo);
  (ids || []).forEach(function(id) {
    if (marcado) {
      selecao[id] = true;
    } else {
      delete selecao[id];
    }
  });
  document.querySelectorAll('input.bulk-check[data-grupo="' + grupo + '"]').forEach(function(input) {
    input.checked = !!selecao[input.dataset.id];
  });
  atualizarResumoSelecaoMassa(grupo);
}

function limparSelecaoMassa(grupo) {
  selecoesMassa[grupo] = {};
  atualizarResumoSelecaoMassa(grupo);
}

function atualizarResumoSelecaoMassa(grupo) {
  var ids = idsSelecionadosMassa(grupo);
  var contador = $('bulkCount-' + grupo);
  var botao = $('bulkDelete-' + grupo);
  var selecionarTodos = $('bulkAll-' + grupo);
  var visiveis = Array.from(document.querySelectorAll('input.bulk-check[data-grupo="' + grupo + '"]'));
  var visiveisSelecionados = visiveis.filter(function(input) {
    return !!obterSelecaoMassa(grupo)[input.dataset.id];
  }).length;

  if (contador) {
    contador.textContent = ids.length ? ids.length + ' selecionado' + (ids.length === 1 ? '' : 's') : 'Selecione 2 ou mais';
  }
  if (botao) {
    botao.disabled = ids.length < 2;
  }
  if (selecionarTodos) {
    selecionarTodos.checked = visiveis.length > 0 && visiveisSelecionados === visiveis.length;
    selecionarTodos.indeterminate = visiveisSelecionados > 0 && visiveisSelecionados < visiveis.length;
  }
}

async function excluirSelecionadosMassa(grupo, nomePlural, urlBase, aposExcluir, verboAcao) {
  var ids = idsSelecionadosMassa(grupo);
  var verbo = verboAcao || 'Excluir';
  if (ids.length < 2) {
    mostrarToast('erro', 'Selecione pelo menos 2 itens para excluir.');
    return;
  }
  mostrarConfirm(verbo + ' em massa', verbo + ' ' + ids.length + ' ' + nomePlural + '?', async function() {
    var excluidos = 0;
    var falhas = 0;
    document.body.classList.add('loading');
    try {
      for (var i = 0; i < ids.length; i++) {
        var r = await fetch(API + API_PREFIX + urlBase + '/' + ids[i], {
          method: 'DELETE',
          headers: getAuthHeaders()
        });
        if (r.ok) {
          excluidos++;
        } else {
          falhas++;
        }
      }
    } finally {
      document.body.classList.remove('loading');
    }

    limparSelecaoMassa(grupo);
    if (typeof aposExcluir === 'function') {
      await aposExcluir();
    } else {
      await carregarTudo();
    }
    if (excluidos) {
      var textoAcao = verbo === 'Inativar' ? 'inativado' : 'excluído';
      mostrarToast('sucesso', excluidos + ' item' + (excluidos === 1 ? '' : 's') + ' ' + textoAcao + (excluidos === 1 ? '' : 's') + '.');
    }
    if (falhas) {
      mostrarToast('erro', falhas + ' item' + (falhas === 1 ? '' : 's') + ' não puderam ser excluídos. Verifique se existem vínculos.');
    }
  });
}

function renderCliente(c) {
  return '<tr>' +
    '<td class="bulk-cell">' + checkboxMassaHtml('clientes', c.id, 'Selecionar cliente ' + c.nome) + '</td>' +
    '<td>' + c.id + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="nome">' + escapeHtml(c.nome) + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="telefone">' + escapeHtml(formatarTelefoneDisplay(c.telefone)) + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="endereco">' + escapeHtml(c.endereco) + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="numero_casa">' + escapeHtml(c.numero_casa || '') + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="bairro">' + escapeHtml(c.bairro) + '</td>' +
    '<td class="editavel" contenteditable="true" data-linha="cliente-' + c.id + '" data-campo="referencia">' + escapeHtml(c.referencia || '') + '</td>' +
    '<td class="acoes">' +
      '<button class="save" onclick="salvarCliente(' + c.id + ')">Salvar</button>' +
      '<button class="delete" onclick="excluirCliente(' + c.id + ')">Excluir</button>' +
    '</td></tr>';
}

var paginacaoEstado = {};
var paginacaoPaginaAtual = {};
var paginacaoPorPagina = {};

function paginarDados(grupo, dados) {
  var porPagina = Number(paginacaoPorPagina[grupo]) || 20;
  var pagina = Number(paginacaoPaginaAtual[grupo]) || 1;
  var total = dados.length;
  var totalPaginas = Math.max(1, Math.ceil(total / porPagina));
  if (pagina < 1) pagina = 1;
  if (pagina > totalPaginas) pagina = totalPaginas;
  paginacaoPaginaAtual[grupo] = pagina;
  var inicio = (pagina - 1) * porPagina;
  var fim = inicio + porPagina;
  var estado = {
    dados: dados.slice(inicio, fim),
    pagina: pagina,
    totalPaginas: totalPaginas,
    total: total,
    inicio: total ? inicio + 1 : 0,
    fim: Math.min(fim, total)
  };
  paginacaoEstado[grupo] = estado;
  return estado;
}

function renderPaginacao(grupo) {
  var estado = paginacaoEstado[grupo];
  if (!estado || estado.totalPaginas <= 1) return '';
  var html = '<tr class="pagination-row"><td colspan="99"><div class="pagination">';
  html += '<label class="pagination-size"><span>Por página</span><select onchange="alterarItensPorPagina(\'' + grupo + '\', this.value)">';
  [20, 50, 100].forEach(function(opcao) {
    html += '<option value="' + opcao + '"' + ((Number(paginacaoPorPagina[grupo]) || 20) === opcao ? ' selected' : '') + '>' + opcao + '</option>';
  });
  html += '</select></label>';
  html += '<button type="button" ' + (estado.pagina <= 1 ? 'disabled' : '') + ' onclick="irPagina(\'' + grupo + '\', ' + (estado.pagina - 1) + ')" title="Anterior">&#8249;</button>';

  var paginas = [];
  if (estado.totalPaginas <= 5) {
    for (var p = 1; p <= estado.totalPaginas; p++) paginas.push(p);
  } else if (estado.pagina <= 3) {
    paginas = [1, 2, 3, estado.totalPaginas];
  } else if (estado.pagina >= estado.totalPaginas - 2) {
    paginas = [1, estado.totalPaginas - 2, estado.totalPaginas - 1, estado.totalPaginas];
  } else {
    paginas = [1, estado.pagina, estado.pagina + 1, estado.pagina + 2, estado.totalPaginas];
  }

  var anterior = 0;
  for (var idx = 0; idx < paginas.length; idx++) {
    var i = paginas[idx];
    if (i <= 0 || i > estado.totalPaginas || i === anterior) continue;
    if (anterior && i > anterior + 1) html += '<span class="pagination-dots">...</span>';
    html += '<button type="button" class="' + (i === estado.pagina ? 'active' : '') + '" onclick="irPagina(\'' + grupo + '\', ' + i + ')">' + i + '</button>';
    anterior = i;
  }
  html += '<button type="button" ' + (estado.pagina >= estado.totalPaginas ? 'disabled' : '') + ' onclick="irPagina(\'' + grupo + '\', ' + (estado.pagina + 1) + ')" title="Proxima">&#8250;</button>';
  html += '<span class="pagination-info">' + estado.inicio + ' - ' + estado.fim + ' de ' + estado.total + '</span>';
  html += '</div></td></tr>';
  return html;
}

function irPagina(grupo, pagina) {
  var estado = paginacaoEstado[grupo];
  pagina = Number(pagina) || 1;
  if (estado) {
    pagina = Math.max(1, Math.min(pagina, estado.totalPaginas));
  }
  paginacaoPaginaAtual[grupo] = pagina;
  if (grupo === 'clientes') filtrarClientes();
  if (grupo === 'entregadores') filtrarEntregadores();
  if (grupo === 'produtos') filtrarProdutos();
  if (grupo === 'cupons') filtrarCupons();
}

function alterarItensPorPagina(grupo, valor) {
  paginacaoPorPagina[grupo] = Number(valor) || 20;
  paginacaoPaginaAtual[grupo] = 1;
  irPagina(grupo, 1);
}
