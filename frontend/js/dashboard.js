async function carregarDashboard() {
  const d = await apiGet('/dashboard');
  if (!d || Array.isArray(d)) return;

  $('totalPedidos').textContent = d.total_pedidos ?? 0;
  $('tempoMedio').textContent = (d.tempo_medio_minutos ?? 0) + ' min';

  $('statusPedidos').innerHTML = (d.por_status ?? [])
    .map(s => `<p><span class="badge">${s.status}</span> ${s.total}</p>`)
    .join('');

  $('rotas').innerHTML = (d.roteirizacao_por_bairro ?? [])
    .map(r => `<p><span class="badge">${r.bairro}</span> ${r.entregas} entrega(s)</p>`)
    .join('');
}
