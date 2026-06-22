var configAtual = null;

async function carregarConfiguracoes() {
  var dados = await apiGet('/configuracoes');
  if (!dados || Array.isArray(dados)) return;
  configAtual = dados;
  $('configNomeLoja').value = dados.nome_loja || 'ÁquaLog';
  $('configSubtituloLoja').value = dados.subtitulo_loja || 'Pedido online da distribuidora';
  $('configPixChave').value = dados.pix_chave || '';
  $('configAvisoCliente').value = dados.aviso_cliente || '';
  $('configEstoqueMinimo').value = dados.estoque_minimo_padrao ?? 5;
  $('configLojaAberta').value = dados.loja_aberta ? '1' : '0';
  $('configSomNovoPedido').value = dados.som_novo_pedido ? '1' : '0';
  if ($('produtoEstoqueMinimo') && (!$('produtoEstoqueMinimo').value || $('produtoEstoqueMinimo').value === '5')) {
    $('produtoEstoqueMinimo').value = dados.estoque_minimo_padrao ?? 5;
  }
}

$('formConfiguracoes').onsubmit = async function(e) {
  e.preventDefault();
  var payload = {
    nome_loja: valor('configNomeLoja'),
    subtitulo_loja: valor('configSubtituloLoja'),
    pix_chave: valor('configPixChave'),
    aviso_cliente: valor('configAvisoCliente'),
    estoque_minimo_padrao: numero('configEstoqueMinimo'),
    loja_aberta: valor('configLojaAberta') === '1',
    som_novo_pedido: valor('configSomNovoPedido') === '1'
  };
  var resposta = await apiSend('/configuracoes', 'PUT', payload);
  if (resposta) {
    await carregarConfiguracoes();
    mostrarToast('sucesso', 'Configurações salvas.');
  }
};
