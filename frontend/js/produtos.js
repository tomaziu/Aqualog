var cacheProdutos = [];
var ultimoProdutos = null;

async function carregarProdutos() {
  var dados = await apiGet('/produtos');
  if (!Array.isArray(dados)) return;

  var dadosAtuais = JSON.stringify(dados);
  if (ultimoProdutos === dadosAtuais) {
    return; // Dados não mudaram
  }
  ultimoProdutos = dadosAtuais;
  cacheProdutos = dados;
  filtrarProdutos();
  var ativos = dados.filter(function(p) { return p.ativo !== false && Number(p.ativo) !== 0; });
  $('pedidoProduto').innerHTML = ativos
    .map(function(p) { return '<option value="' + p.id + '">' + escapeHtml(p.nome) + '</option>'; })
    .join('');
}

function filtrarProdutos() {
  var q = ($('filtroProduto').value || '').toLowerCase();
  var status = $('filtroProdutoStatus') ? $('filtroProdutoStatus').value : 'todos';
  var dados = cacheProdutos.filter(function(p) {
    var ativo = p.ativo !== false && Number(p.ativo) !== 0;
    var bateNome = !q || p.nome.toLowerCase().includes(q);
    var bateStatus = status === 'todos' || (status === 'ativos' && ativo) || (status === 'inativos' && !ativo);
    return bateNome && bateStatus;
  });
  window.idsProdutosVisiveis = dados.map(function(p) { return p.id; });
  $('listaProdutos').innerHTML = dados.map(function(p) {
    var baixo = Number(p.estoque) <= Number(p.estoque_minimo || 0);
    var ativo = p.ativo !== false && Number(p.ativo) !== 0;
    return '<tr class="' + (ativo ? '' : 'inactive-row ') + (baixo && ativo ? 'stock-low-row' : '') + '">' +
      '<td class="bulk-cell">' + checkboxMassaHtml('produtos', p.id, 'Selecionar produto ' + p.nome) + '</td>' +
      '<td>' + p.id + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="nome">' + escapeHtml(p.nome) + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="preco">' + Number(p.preco).toFixed(2) + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="estoque">' + p.estoque + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="estoque_minimo">' + (p.estoque_minimo ?? 5) + '</td>' +
      '<td><select class="select-inline" data-linha="produto-' + p.id + '" data-campo="ativo">' +
        '<option value="1"' + (ativo ? ' selected' : '') + '>Ativo</option>' +
        '<option value="0"' + (!ativo ? ' selected' : '') + '>Inativo</option>' +
      '</select></td>' +
      '<td class="acoes">' +
        (!ativo ? '<span class="status-muted">inativo</span>' : (baixo ? '<span class="stock-alert">baixo</span>' : '')) +
        '<button class="save" onclick="salvarProduto(' + p.id + ')">Salvar</button>' +
        '<button class="delete" onclick="excluirProduto(' + p.id + ')">Inativar</button>' +
      '</td></tr>';
  }).join('');
  atualizarResumoSelecaoMassa('produtos');
}

async function salvarProduto(id) {
  var linha = 'produto-' + id;
  var produto = {
    nome: lerCelula(linha, 'nome'),
    preco: Number(lerCelula(linha, 'preco').replace(',', '.')),
    estoque: Number(lerCelula(linha, 'estoque')),
    estoque_minimo: Number(lerCelula(linha, 'estoque_minimo')),
    ativo: lerSelect(linha, 'ativo') === '1'
  };
  if (!produto.nome || produto.nome.length < 2 || produto.preco <= 0 || produto.estoque < 0 || produto.estoque_minimo < 0) {
    mostrarToast('erro', 'Dados invalidos para produto.');
    return;
  }
  var resposta = await apiSend('/produtos/' + id, 'PUT', produto);
  if (resposta) {
    await carregarTudo();
    mostrarToast('sucesso', 'Produto atualizado com sucesso!');
  }
}

async function excluirProduto(id) {
  if (!confirm('Inativar este produto? Ele sairá da loja do cliente, mas os pedidos antigos continuam salvos.')) return;
  if (await apiDelete('/produtos/' + id)) {
    await carregarTudo();
    mostrarToast('sucesso', 'Produto inativado com sucesso!');
  }
}

async function excluirProdutosSelecionados() {
  await excluirSelecionadosMassa('produtos', 'produtos selecionados', '/produtos', async function() {
    ultimoProdutos = null;
    await carregarTudo();
  }, 'Inativar');
}
