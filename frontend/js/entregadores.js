var cacheEntregadores = [];

async function carregarEntregadores() {
  var dados = await apiGet('/entregadores');
  if (!Array.isArray(dados)) return;
  cacheEntregadores = dados;
  filtrarEntregadores();
  $('pedidoEntregador').innerHTML =
    '<option value="">Sem entregador</option>' +
    dados.map(function(e) { return '<option value="' + e.id + '">' + escapeHtml(e.nome) + ' - ' + escapeHtml(e.status) + '</option>'; }).join('');
}

function filtrarEntregadores() {
  var q = ($('filtroEntregador').value || '').toLowerCase();
  var dados = cacheEntregadores.filter(function(e) {
    return !q || e.nome.toLowerCase().includes(q) || e.veiculo.toLowerCase().includes(q) || e.telefone.toLowerCase().includes(q);
  });
  var paginado = paginarDados('entregadores', dados);
  window.idsEntregadoresVisiveis = paginado.dados.map(function(e) { return e.id; });
  $('listaEntregadores').innerHTML = paginado.dados.map(function(e) {
    return '<tr>' +
      '<td class="bulk-cell">' + checkboxMassaHtml('entregadores', e.id, 'Selecionar entregador ' + e.nome) + '</td>' +
      '<td>' + e.id + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="entregador-' + e.id + '" data-campo="nome">' + escapeHtml(e.nome) + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="entregador-' + e.id + '" data-campo="telefone">' + escapeHtml(formatarTelefoneDisplay(e.telefone)) + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="entregador-' + e.id + '" data-campo="veiculo">' + escapeHtml(e.veiculo) + '</td>' +
      '<td class="codigo-cell" data-linha="entregador-' + e.id + '" data-campo="codigo_acesso">' +
        '<div style="font-size: 11px; color: #999; margin-bottom: 2px;">Cód: ********</div>' +
        '<input class="codigo-input" type="text" style="width: 80px; font-size: 12px;" placeholder="Novo">' +
      '</td>' +
      '<td>' +
        '<select class="select-inline" data-linha="entregador-' + e.id + '" data-campo="status">' +
          '<option value="disponivel"' + (e.status === 'disponivel' ? ' selected' : '') + '>Disponivel</option>' +
          '<option value="ocupado"' + (e.status === 'ocupado' ? ' selected' : '') + '>Ocupado</option>' +
        '</select>' +
        (e.status === 'ocupado' ? '<span class="badge" style="background:rgba(239,68,68,0.12);color:#f87171;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:6px;font-weight:600">ocupado</span>' : '<span class="badge" style="background:rgba(16,185,129,0.12);color:#34d399;margin-left:6px;font-size:11px;padding:2px 8px;border-radius:6px;font-weight:600">disponivel</span>') +
      '</td>' +
      '<td class="acoes">' +
        '<button class="save" onclick="salvarEntregador(' + e.id + ')">Salvar</button>' +
        '<button class="delete" onclick="excluirEntregador(' + e.id + ')">Excluir</button>' +
      '</td></tr>';
  }).join('') + renderPaginacao('entregadores');
  atualizarResumoSelecaoMassa('entregadores');
}

async function salvarEntregador(id) {
  var linha = 'entregador-' + id;
  var codigo = lerCelula(linha, 'codigo_acesso');
  var dados = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone').replace(/\D/g, ''),
    veiculo: lerCelula(linha, 'veiculo'),
    codigo_acesso: (codigo && codigo !== '********') ? codigo : '',
    status: lerSelect(linha, 'status') || 'disponivel'
  };
  var resposta = await apiSend('/entregadores/' + id, 'PUT', dados);
  if (resposta) {
    await carregarTudo();
    mostrarToast('sucesso', 'Entregador atualizado com sucesso!');
  }
}

async function excluirEntregador(id) {
  await mostrarConfirm('Excluir entregador', 'Deseja excluir este entregador?', async function() {
    if (await apiDelete('/entregadores/' + id)) {
      await carregarTudo();
      mostrarToast('sucesso', 'Entregador excluido com sucesso!');
    }
  });
}

async function excluirEntregadoresSelecionados() {
  await excluirSelecionadosMassa('entregadores', 'entregadores', '/entregadores', carregarTudo);
}
