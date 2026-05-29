let cacheEntregadores = [];

async function carregarEntregadores() {
  const dados = await apiGet('/entregadores');
  if (!Array.isArray(dados)) return;
  cacheEntregadores = dados;
  filtrarEntregadores();

  $('pedidoEntregador').innerHTML =
    '<option value="">Sem entregador</option>' +
    dados.map(e => `<option value="${e.id}">${escapeHtml(e.nome)} - ${escapeHtml(e.status)}</option>`).join('');
}

function filtrarEntregadores() {
  const q = ($('filtroEntregador').value || '').toLowerCase();
  const dados = cacheEntregadores.filter(e =>
    !q || e.nome.toLowerCase().includes(q) || e.veiculo.toLowerCase().includes(q) || e.telefone.toLowerCase().includes(q)
  );
  $('listaEntregadores').innerHTML = dados.map(e =>
    `<tr>
      <td>${e.id}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="nome">${escapeHtml(e.nome)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="telefone">${escapeHtml(e.telefone)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="veiculo">${escapeHtml(e.veiculo)}</td>
      <td class="editavel" contenteditable="true" data-linha="entregador-${e.id}" data-campo="codigo_acesso">${escapeHtml(e.codigo_acesso)}</td>
      <td>
        <select class="select-inline" data-linha="entregador-${e.id}" data-campo="status">
          <option value="disponivel" ${e.status === 'disponivel' ? 'selected' : ''}>Disponível</option>
          <option value="ocupado" ${e.status === 'ocupado' ? 'selected' : ''}>Ocupado</option>
        </select>
      </td>
      <td class="acoes">
        <button class="save" onclick="salvarEntregador(${e.id})">Salvar</button>
        <button class="delete" onclick="excluirEntregador(${e.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function salvarEntregador(id) {
  const linha = `entregador-${id}`;
  const entregador = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone'),
    veiculo: lerCelula(linha, 'veiculo'),
    codigo_acesso: lerCelula(linha, 'codigo_acesso'),
    status: lerSelect(linha, 'status') || 'disponivel'
  };

  const resposta = await apiSend(`/entregadores/${id}`, 'PUT', entregador);
  if (resposta) {
    await carregarTudo();
    alert('Entregador atualizado com sucesso!');
  }
}

async function excluirEntregador(id) {
  if (!confirm('Deseja excluir este entregador?')) return;
  if (await apiDelete(`/entregadores/${id}`)) await carregarTudo();
}
