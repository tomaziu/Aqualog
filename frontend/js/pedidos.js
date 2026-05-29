let cachePedidos = [];

async function carregarPedidos() {
  const dados = await apiGet('/pedidos');
  if (!Array.isArray(dados)) return;
  cachePedidos = dados;
  filtrarPedidos();
}

function filtrarPedidos() {
  const q = ($('filtroPedido').value || '').toLowerCase();
  const filtrados = cachePedidos.filter(p =>
    !q
    || (p.cliente && p.cliente.toLowerCase().includes(q))
    || (p.entregador && p.entregador.toLowerCase().includes(q))
    || (p.bairro && p.bairro.toLowerCase().includes(q))
    || (p.produto && p.produto.toLowerCase().includes(q))
    || (p.status && statusTexto(p.status).toLowerCase().includes(q))
  );
  $('listaPedidos').innerHTML = filtrados.map(p =>
    `<tr>
      <td>${p.id}</td>
      <td>${escapeHtml(p.cliente)}</td>
      <td>${escapeHtml(p.entregador || '-')}</td>
      <td>${escapeHtml(p.produto)}</td>
      <td>${escapeHtml(p.bairro)}</td>
      <td>${statusTexto(p.status)}</td>
      <td>${formatarData(p.data_criacao)}</td>
      <td class="acoes">
        <select onchange="mudarStatus(${p.id}, this.value)">
          <option value="">Alterar status</option>
          <option value="recebido">Recebido</option>
          <option value="em_preparo">Em preparo</option>
          <option value="saiu_para_entrega">Saiu p/ entrega</option>
          <option value="entregue">Entregue</option>
          <option value="cancelado">Cancelado</option>
        </select>
        <button class="delete" onclick="excluirPedido(${p.id})">Excluir</button>
      </td>
    </tr>`
  ).join('');
}

async function mudarStatus(id, status) {
  if (!status) return;
  const r = await fetch(`${API}/pedidos/${id}/status?status=${encodeURIComponent(status)}`, {method: 'PATCH'});
  if (!r.ok) alert('Não foi possível alterar o status.');
  await carregarTudo();
}

async function excluirPedido(id) {
  if (!confirm('Deseja excluir este pedido?')) return;
  if (await apiDelete(`/pedidos/${id}`)) await carregarTudo();
}
