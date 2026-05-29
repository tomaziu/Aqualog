function gerarRelatorioPDF() {
  const total = cachePedidos.length;
  const entregues = cachePedidos.filter(p => p.status === 'entregue').length;
  const pendentes = cachePedidos.filter(p => p.status !== 'entregue' && p.status !== 'cancelado').length;

  const porStatus = {};
  cachePedidos.forEach(p => { porStatus[p.status] = (porStatus[p.status] || 0) + 1; });

  const porBairro = {};
  cachePedidos.forEach(p => { porBairro[p.bairro] = (porBairro[p.bairro] || 0) + 1; });

  const agora = new Date().toLocaleString('pt-BR');

  let html = `
  <!DOCTYPE html>
  <html><head><meta charset="UTF-8">
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; padding: 30px; color: #102434; }
    h1 { color: #063b5c; margin-bottom: 4px; }
    .sub { color: #66788a; margin-bottom: 24px; }
    h2 { color: #0877b8; border-bottom: 2px solid #d9e8f0; padding-bottom: 6px; margin-top: 28px; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    th, td { padding: 10px 12px; border: 1px solid #d9e8f0; text-align: left; font-size: 13px; }
    th { background: #eefaff; color: #063b5c; font-weight: 700; }
    .cards { display: flex; gap: 16px; margin: 16px 0; }
    .card { background: #f3f9fc; border: 1px solid #d9e8f0; border-radius: 8px; padding: 16px 24px; flex: 1; }
    .card strong { font-size: 28px; color: #0877b8; display: block; }
    .card span { color: #66788a; font-size: 13px; }
    @media print { body { padding: 15px; } }
  </style>
  </head><body>
  <h1>ÁquaLog — Relatório</h1>
  <div class="sub">Gerado em ${agora}</div>

  <div class="cards">
    <div class="card"><strong>${total}</strong><span>Total de pedidos</span></div>
    <div class="card"><strong>${entregues}</strong><span>Entregues</span></div>
    <div class="card"><strong>${pendentes}</strong><span>Pendentes</span></div>
  </div>

  <h2>Status dos pedidos</h2>
  <table><thead><tr><th>Status</th><th>Quantidade</th></tr></thead><tbody>
    ${Object.entries(porStatus).map(([s, qtd]) =>
      `<tr><td>${statusTexto(s)}</td><td>${qtd}</td></tr>`
    ).join('')}
  </tbody></table>

  <h2>Roteirização por bairro</h2>
  <table><thead><tr><th>Bairro</th><th>Entregas</th></tr></thead><tbody>
    ${Object.entries(porBairro).sort((a, b) => b[1] - a[1]).map(([bairro, qtd]) =>
      `<tr><td>${escapeHtml(bairro)}</td><td>${qtd}</td></tr>`
    ).join('')}
  </tbody></table>

  <h2>Últimos pedidos</h2>
  <table><thead><tr><th>ID</th><th>Cliente</th><th>Produto</th><th>Bairro</th><th>Status</th></tr></thead><tbody>
    ${cachePedidos.slice(0, 50).map(p =>
      `<tr><td>${p.id}</td><td>${escapeHtml(p.cliente)}</td><td>${escapeHtml(p.produto)}</td><td>${escapeHtml(p.bairro)}</td><td>${statusTexto(p.status)}</td></tr>`
    ).join('')}
  </tbody></table>
  </body></html>`;

  const win = window.open('', '_blank');
  win.document.write(html);
  win.document.close();
  win.focus();
  setTimeout(() => win.print(), 500);
}

function gerarRelatorioExcel() {
  const wb = XLSX.utils.book_new();

  const pedidosData = cachePedidos.map(p => ({
    ID: p.id,
    Cliente: p.cliente,
    Entregador: p.entregador || '-',
    Produto: p.produto,
    Bairro: p.bairro,
    Status: statusTexto(p.status),
    Data: formatarData(p.data_criacao)
  }));
  const wsPedidos = XLSX.utils.json_to_sheet(pedidosData);
  XLSX.utils.book_append_sheet(wb, wsPedidos, 'Pedidos');

  const clientesData = cacheClientes.map(c => ({
    ID: c.id,
    Nome: c.nome,
    Telefone: c.telefone,
    Endereço: c.endereco,
    Bairro: c.bairro,
    Referência: c.referencia || ''
  }));
  const wsClientes = XLSX.utils.json_to_sheet(clientesData);
  XLSX.utils.book_append_sheet(wb, wsClientes, 'Clientes');

  const entregadoresData = cacheEntregadores.map(e => ({
    ID: e.id,
    Nome: e.nome,
    Telefone: e.telefone,
    Veículo: e.veiculo,
    Status: e.status === 'disponivel' ? 'Disponível' : 'Ocupado'
  }));
  const wsEntregadores = XLSX.utils.json_to_sheet(entregadoresData);
  XLSX.utils.book_append_sheet(wb, wsEntregadores, 'Entregadores');

  const produtosData = cacheProdutos.map(p => ({
    ID: p.id,
    Produto: p.nome,
    Preço: Number(p.preco).toFixed(2),
    Estoque: p.estoque
  }));
  const wsProdutos = XLSX.utils.json_to_sheet(produtosData);
  XLSX.utils.book_append_sheet(wb, wsProdutos, 'Produtos');

  const porBairro = {};
  cachePedidos.forEach(p => { porBairro[p.bairro] = (porBairro[p.bairro] || 0) + 1; });
  const rotaData = Object.entries(porBairro).sort((a, b) => b[1] - a[1]).map(([bairro, qtd]) => ({
    Bairro: bairro,
    Entregas: qtd
  }));
  const wsRotas = XLSX.utils.json_to_sheet(rotaData);
  XLSX.utils.book_append_sheet(wb, wsRotas, 'Roteirização');

  XLSX.writeFile(wb, `aqualog_relatorio_${new Date().toISOString().slice(0, 10)}.xlsx`);
}
