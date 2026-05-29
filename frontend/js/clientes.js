let cacheClientes = [];

async function carregarClientes() {
  const clientes = await apiGet('/clientes');
  if (!Array.isArray(clientes)) return;
  cacheClientes = clientes;
  filtrarClientes();

  $('pedidoCliente').innerHTML = clientes
    .map(c => `<option value="${c.id}">${escapeHtml(c.nome)} - ${escapeHtml(c.bairro)}</option>`)
    .join('');
}

function filtrarClientes() {
  const q = ($('filtroCliente').value || '').toLowerCase();
  const filtrados = cacheClientes.filter(c =>
    !q || c.nome.toLowerCase().includes(q) || c.bairro.toLowerCase().includes(q) || c.telefone.toLowerCase().includes(q)
  );
  $('listaClientes').innerHTML = filtrados.map(renderCliente).join('');
}

async function salvarCliente(id) {
  const linha = `cliente-${id}`;
  const cliente = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone'),
    endereco: lerCelula(linha, 'endereco'),
    bairro: lerCelula(linha, 'bairro'),
    referencia: lerCelula(linha, 'referencia') || null
  };

  const resposta = await apiSend(`/clientes/${id}`, 'PUT', cliente);
  if (resposta) {
    await carregarTudo();
    alert('Cliente atualizado com sucesso!');
  }
}

async function excluirCliente(id) {
  if (!confirm('Deseja excluir este cliente?')) return;
  if (await apiDelete(`/clientes/${id}`)) await carregarTudo();
}
