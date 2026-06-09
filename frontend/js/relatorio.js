function gerarRelatorioPDF() {
  var total = cachePedidos.length;
  var entregues = cachePedidos.filter(function(p) { return p.status === 'entregue'; }).length;
  var pendentes = cachePedidos.filter(function(p) { return p.status !== 'entregue' && p.status !== 'cancelado'; }).length;

  var porStatus = {};
  cachePedidos.forEach(function(p) { porStatus[p.status] = (porStatus[p.status] || 0) + 1; });

  var porBairro = {};
  cachePedidos.forEach(function(p) { porBairro[p.bairro] = (porBairro[p.bairro] || 0) + 1; });

  var agora = new Date().toLocaleString('pt-BR');

  var html = '<!DOCTYPE html><html><head><meta charset="UTF-8">' +
  '<style>' +
    'body { font-family: "Segoe UI", Arial, sans-serif; padding: 30px; color: #102434; }' +
    'h1 { color: #063b5c; margin-bottom: 4px; }' +
    '.sub { color: #66788a; margin-bottom: 24px; }' +
    'h2 { color: #0877b8; border-bottom: 2px solid #d9e8f0; padding-bottom: 6px; margin-top: 28px; }' +
    'table { width: 100%; border-collapse: collapse; margin: 12px 0; }' +
    'th, td { padding: 10px 12px; border: 1px solid #d9e8f0; text-align: left; font-size: 13px; }' +
    'th { background: #eefaff; color: #063b5c; font-weight: 700; }' +
    '.cards { display: flex; gap: 16px; margin: 16px 0; }' +
    '.card { background: #f3f9fc; border: 1px solid #d9e8f0; border-radius: 8px; padding: 16px 24px; flex: 1; }' +
    '.card strong { font-size: 28px; color: #0877b8; display: block; }' +
    '.card span { color: #66788a; font-size: 13px; }' +
    '@media print { body { padding: 15px; } }' +
  '</style></head><body>' +
  '<h1>Aqualog Relatorio</h1>' +
  '<div class="sub">Gerado em ' + agora + '</div>' +
  '<div class="cards">' +
    '<div class="card"><strong>' + total + '</strong><span>Total de pedidos</span></div>' +
    '<div class="card"><strong>' + entregues + '</strong><span>Entregues</span></div>' +
    '<div class="card"><strong>' + pendentes + '</strong><span>Pendentes</span></div>' +
  '</div>' +
  '<h2>Status dos pedidos</h2>' +
  '<table><thead><tr><th>Status</th><th>Quantidade</th></tr></thead><tbody>' +
    Object.entries(porStatus).map(function(entry) {
      return '<tr><td>' + statusTexto(entry[0]) + '</td><td>' + entry[1] + '</td></tr>';
    }).join('') +
  '</tbody></table>' +
  '<h2>Roteirizacao por bairro</h2>' +
  '<table><thead><tr><th>Bairro</th><th>Entregas</th></tr></thead><tbody>' +
    Object.entries(porBairro).sort(function(a, b) { return b[1] - a[1]; }).map(function(entry) {
      return '<tr><td>' + escapeHtml(entry[0]) + '</td><td>' + entry[1] + '</td></tr>';
    }).join('') +
  '</tbody></table>' +
  '<h2>Ultimos pedidos</h2>' +
  '<table><thead><tr><th>ID</th><th>Cliente</th><th>Produto</th><th>Bairro</th><th>Status</th></tr></thead><tbody>' +
    cachePedidos.slice(0, 50).map(function(p) {
      return '<tr><td>' + p.id + '</td><td>' + escapeHtml(p.cliente) + '</td><td>' + escapeHtml(p.produto) + '</td><td>' + escapeHtml(p.bairro) + '</td><td>' + statusTexto(p.status) + '</td></tr>';
    }).join('') +
  '</tbody></table></body></html>';

  var win = window.open('', '_blank');
  win.document.write(html);
  win.document.close();
  win.focus();
  setTimeout(function() { win.print(); }, 500);
}

function gerarRelatorioExcel() {
  var wb = XLSX.utils.book_new();

  var pedidosData = cachePedidos.map(function(p) {
    return { ID: p.id, Cliente: p.cliente, Entregador: p.entregador || '-', Produto: p.produto, Bairro: p.bairro, Status: statusTexto(p.status), Data: formatarData(p.data_criacao) };
  });
  var wsPedidos = XLSX.utils.json_to_sheet(pedidosData);
  XLSX.utils.book_append_sheet(wb, wsPedidos, 'Pedidos');

  var clientesData = cacheClientes.map(function(c) {
    return { ID: c.id, Nome: c.nome, Telefone: c.telefone, 'Endereco': c.endereco, Bairro: c.bairro, 'Referencia': c.referencia || '' };
  });
  var wsClientes = XLSX.utils.json_to_sheet(clientesData);
  XLSX.utils.book_append_sheet(wb, wsClientes, 'Clientes');

  var entregadoresData = cacheEntregadores.map(function(e) {
    return { ID: e.id, Nome: e.nome, Telefone: e.telefone, 'Veiculo': e.veiculo, Status: e.status === 'disponivel' ? 'Disponivel' : 'Ocupado' };
  });
  var wsEntregadores = XLSX.utils.json_to_sheet(entregadoresData);
  XLSX.utils.book_append_sheet(wb, wsEntregadores, 'Entregadores');

  var produtosData = cacheProdutos.map(function(p) {
    return { ID: p.id, Produto: p.nome, 'Preco': Number(p.preco).toFixed(2), Estoque: p.estoque, 'Estoque mínimo': p.estoque_minimo || 0 };
  });
  var wsProdutos = XLSX.utils.json_to_sheet(produtosData);
  XLSX.utils.book_append_sheet(wb, wsProdutos, 'Produtos');

  var porBairro = {};
  cachePedidos.forEach(function(p) { porBairro[p.bairro] = (porBairro[p.bairro] || 0) + 1; });
  var rotaData = Object.entries(porBairro).sort(function(a, b) { return b[1] - a[1]; }).map(function(entry) {
    return { Bairro: entry[0], Entregas: entry[1] };
  });
  var wsRotas = XLSX.utils.json_to_sheet(rotaData);
  XLSX.utils.book_append_sheet(wb, wsRotas, 'Roteirizacao');

  XLSX.writeFile(wb, 'aqualog_relatorio_' + new Date().toISOString().slice(0, 10) + '.xlsx');
}

async function baixarBackupSQL() {
  document.body.classList.add('loading');
  try {
    var r = await fetch(API + API_PREFIX + '/backup/sql', {
      headers: getAuthHeaders()
    });
    if (!r.ok) {
      mostrarToast('erro', 'Não foi possível gerar o backup SQL.');
      return;
    }
    var blob = await r.blob();
    var nome = 'aqualog_backup_' + new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '') + '.sql';
    var disposicao = r.headers.get('Content-Disposition') || '';
    var match = disposicao.match(/filename="([^"]+)"/);
    if (match) nome = match[1];

    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = nome;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    mostrarToast('sucesso', 'Backup SQL baixado.');
  } finally {
    document.body.classList.remove('loading');
  }
}
