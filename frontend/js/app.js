async function carregarTudo() {
  await carregarDashboard();
  await carregarClientes();
  await carregarEntregadores();
  await carregarProdutos();
  await carregarPedidos();
}

$('formCliente').onsubmit = async (e) => {
  e.preventDefault();

  const cliente = {
    nome: valor('clienteNome'),
    telefone: valor('clienteTelefone'),
    endereco: valor('clienteEndereco'),
    bairro: valor('clienteBairro'),
    referencia: valor('clienteReferencia') || null
  };

  const resposta = await apiSend('/clientes', 'POST', cliente);
  if (resposta) {
    $('formCliente').reset();
    await carregarTudo();
    alert('Cliente cadastrado com sucesso!');
  }
};

$('formEntregador').onsubmit = async (e) => {
  e.preventDefault();

  const entregador = {
    nome: valor('entregadorNome'),
    telefone: valor('entregadorTelefone'),
    veiculo: valor('entregadorVeiculo'),
    codigo_acesso: valor('entregadorCodigo'),
    status: valor('entregadorStatus') || 'disponivel'
  };

  const resposta = await apiSend('/entregadores', 'POST', entregador);
  if (resposta) {
    $('formEntregador').reset();
    await carregarTudo();
    alert('Entregador cadastrado com sucesso!');
  }
};

$('formProduto').onsubmit = async (e) => {
  e.preventDefault();

  const produto = {
    nome: valor('produtoNome'),
    preco: numero('produtoPreco'),
    estoque: numero('produtoEstoque')
  };

  const resposta = await apiSend('/produtos', 'POST', produto);
  if (resposta) {
    $('formProduto').reset();
    await carregarTudo();
    alert('Produto cadastrado com sucesso!');
  }
};

$('formPedido').onsubmit = async (e) => {
  e.preventDefault();

  const pedido = {
    cliente_id: numero('pedidoCliente'),
    entregador_id: valor('pedidoEntregador') ? numero('pedidoEntregador') : null,
    produto_id: numero('pedidoProduto'),
    quantidade: numero('pedidoQuantidade'),
    forma_pagamento: valor('pedidoPagamento')
  };

  const resposta = await apiSend('/pedidos', 'POST', pedido);
  if (resposta) {
    $('formPedido').reset();
    await carregarTudo();
    alert('Pedido criado com sucesso!');
  }
};

if (sessionStorage.getItem('admin_logado') === '1') carregarTudo();
