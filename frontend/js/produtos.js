let cacheProdutos = [];

async function carregarProdutos() {
  const dados = await apiGet('/produtos');
  if (!Array.isArray(dados)) return;
  cacheProdutos = dados;
  filtrarProdutos();

  $('pedidoProduto').innerHTML = dados
    .map(p => `<option value="${p.id}">${escapeHtml(p.nome)}</option>`)
    .join('');
}

function filtrarProdutos() {
  const q = ($('filtroProduto').value || '').toLowerCase();
  const dados = cacheProdutos.filter(p =>
    !q || p.nome.toLowerCase().includes(q)
  );
  $('listaProdutos').innerHTML = dados.map(p =>
    `<tr>
      <td>${p.id}</td>
      <td class="editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="nome">${escapeHtml(p.nome)}</td>
      <td class="editavel numero-editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="preco">${Number(p.preco).toFixed(2)}</td>
      <td class="editavel numero-editavel" contenteditable="true" data-linha="produto-${p.id}" data-campo="estoque">${p.estoque}</td>
      <td class="acoes">
        <button class="save" onclick="salvarProduto(${p.id})">Salvar</button>
        <button class="delete" onclick="excluirProduto(${p.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function salvarProduto(id) {
  const linha = `produto-${id}`;
  const produto = {
    nome: lerCelula(linha, 'nome'),
    preco: Number(lerCelula(linha, 'preco').replace(',', '.')),
    estoque: Number(lerCelula(linha, 'estoque'))
  };

  if (!produto.nome || produto.nome.length < 2 || produto.preco <= 0 || produto.estoque < 0) {
    alert('Dados inválidos para produto. Confira nome, preço e estoque.');
    return;
  }

  const resposta = await apiSend(`/produtos/${id}`, 'PUT', produto);
  if (resposta) {
    await carregarTudo();
    alert('Produto atualizado com sucesso!');
  }
}

async function excluirProduto(id) {
  if (!confirm('Deseja excluir este produto?')) return;
  if (await apiDelete(`/produtos/${id}`)) await carregarTudo();
}
