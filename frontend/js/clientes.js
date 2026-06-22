var cacheClientes = [];
var ultimoClientes = null;

async function carregarClientes() {
  var clientes = await apiGet('/clientes');
  if (!Array.isArray(clientes)) return;

  var dadosAtuais = JSON.stringify(clientes);
  if (ultimoClientes === dadosAtuais) {
    return; // Dados não mudaram
  }
  ultimoClientes = dadosAtuais;
  cacheClientes = clientes;
  filtrarClientes();
  $('pedidoCliente').innerHTML = clientes
    .map(function(c) { return '<option value="' + c.id + '">' + escapeHtml(c.nome) + ' - ' + escapeHtml(c.bairro) + '</option>'; })
    .join('');
  prepararBuscaClientePedido(clientes);
}

function textoClientePedido(c) {
  return [c.nome, c.bairro, formatarTelefoneDisplay(c.telefone)].filter(Boolean).join(' - ');
}

function selecionarClientePedido(cliente) {
  var select = $('pedidoCliente');
  var input = $('pedidoClienteBusca');
  var lista = $('pedidoClienteOpcoes');
  if (!select || !input || !cliente) return;
  select.value = cliente.id;
  input.value = textoClientePedido(cliente);
  input.dataset.clienteId = cliente.id;
  if (lista) lista.classList.remove('ativo');
}

function renderOpcoesClientePedido(clientes, termo) {
  var lista = $('pedidoClienteOpcoes');
  if (!lista) return;
  var q = String(termo || '').toLowerCase();
  var filtrados = clientes.filter(function(c) {
    var texto = textoClientePedido(c).toLowerCase();
    return !q || texto.includes(q) || String(c.id).includes(q);
  }).slice(0, 8);

  if (!filtrados.length) {
    lista.innerHTML = '<div class="cliente-search-empty">Nenhum cliente encontrado</div>';
    lista.classList.add('ativo');
    return;
  }

  lista.innerHTML = filtrados.map(function(c) {
    return '<button type="button" data-cliente-id="' + c.id + '">' +
      '<strong>' + escapeHtml(c.nome) + '</strong>' +
      '<span>' + escapeHtml([formatarTelefoneDisplay(c.telefone), c.bairro].filter(Boolean).join(' - ')) + '</span>' +
    '</button>';
  }).join('');

  lista.querySelectorAll('button').forEach(function(btn) {
    btn.onclick = function() {
      var id = Number(btn.dataset.clienteId);
      selecionarClientePedido(clientes.find(function(c) { return Number(c.id) === id; }));
    };
  });
  lista.classList.add('ativo');
}

function prepararBuscaClientePedido(clientes) {
  var select = $('pedidoCliente');
  if (!select) return;

  var wrapper = document.getElementById('pedidoClienteBuscaWrap');
  if (!wrapper) {
    wrapper = document.createElement('div');
    wrapper.id = 'pedidoClienteBuscaWrap';
    wrapper.className = 'cliente-search';
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    wrapper.insertAdjacentHTML('afterbegin',
      '<input id="pedidoClienteBusca" type="text" autocomplete="off" placeholder="Digite o nome do cliente" aria-label="Buscar cliente">' +
      '<div id="pedidoClienteOpcoes" class="cliente-search-options"></div>'
    );
    select.classList.add('cliente-search-native');

    $('pedidoClienteBusca').addEventListener('focus', function() {
      renderOpcoesClientePedido(cacheClientes, this.value);
    });
    $('pedidoClienteBusca').addEventListener('input', function() {
      select.value = '';
      this.dataset.clienteId = '';
      renderOpcoesClientePedido(cacheClientes, this.value);
    });
    document.addEventListener('click', function(e) {
      if (!wrapper.contains(e.target)) {
        $('pedidoClienteOpcoes').classList.remove('ativo');
      }
    });
    var form = $('formPedido');
    if (form) {
      form.addEventListener('submit', function(e) {
        if (!select.value) {
          e.preventDefault();
          mostrarToast('erro', 'Selecione um cliente da lista.');
          $('pedidoClienteBusca').focus();
        }
      }, true);
    }
  }

  var selecionado = clientes.find(function(c) { return Number(c.id) === Number(select.value); }) || clientes[0];
  if (selecionado && !select.value) select.value = selecionado.id;
  selecionarClientePedido(selecionado);
}

function filtrarClientes() {
  var q = ($('filtroCliente').value || '').toLowerCase();
  var filtrados = cacheClientes.filter(function(c) {
    return !q || c.nome.toLowerCase().includes(q) || c.bairro.toLowerCase().includes(q) || c.telefone.toLowerCase().includes(q);
  });
  var paginado = paginarDados('clientes', filtrados);
  window.idsClientesVisiveis = paginado.dados.map(function(c) { return c.id; });
  $('listaClientes').innerHTML = paginado.dados.map(renderCliente).join('') + renderPaginacao('clientes');
  atualizarResumoSelecaoMassa('clientes');
}

async function salvarCliente(id) {
  var linha = 'cliente-' + id;
  var cliente = {
    nome: lerCelula(linha, 'nome'),
    telefone: lerCelula(linha, 'telefone').replace(/\D/g, ''),
    endereco: lerCelula(linha, 'endereco'),
    numero_casa: lerCelula(linha, 'numero_casa') || null,
    bairro: lerCelula(linha, 'bairro'),
    referencia: lerCelula(linha, 'referencia') || null
  };
  var resposta = await apiSend('/clientes/' + id, 'PUT', cliente);
  if (resposta) {
    await carregarTudo();
    mostrarToast('sucesso', 'Cliente atualizado com sucesso!');
  }
}

async function excluirCliente(id) {
  mostrarConfirm('Excluir cliente', 'Deseja excluir este cliente?', async function() {
    if (await apiDelete('/clientes/' + id)) {
      await carregarTudo();
      mostrarToast('sucesso', 'Cliente excluido com sucesso!');
    }
  });
}

async function excluirClientesSelecionados() {
  await excluirSelecionadosMassa('clientes', 'clientes', '/clientes', async function() {
    ultimoClientes = null;
    await carregarTudo();
  });
}
