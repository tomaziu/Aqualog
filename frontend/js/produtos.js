var cacheProdutos = [];
var ultimoProdutos = null;
var cropperInstance = null;
var imageModalProdutoId = null;

async function carregarProdutos() {
  var dados = await apiGet('/produtos');
  if (!Array.isArray(dados)) return;

  var dadosAtuais = JSON.stringify(dados);
  if (ultimoProdutos === dadosAtuais) {
    return;
  }
  ultimoProdutos = dadosAtuais;
  cacheProdutos = dados;
  filtrarProdutos();
  var ativos = dados.filter(function(p) { return p.ativo !== false && Number(p.ativo) !== 0; });
  $('pedidoProduto').innerHTML = ativos
    .map(function(p) { return '<option value="' + p.id + '">' + escapeHtml(p.nome) + '</option>'; })
    .join('');
}

function filtrarProdutos() {
  var q = ($('filtroProduto').value || '').toLowerCase();
  var status = $('filtroProdutoStatus') ? $('filtroProdutoStatus').value : 'todos';
  var dados = cacheProdutos.filter(function(p) {
    var ativo = p.ativo !== false && Number(p.ativo) !== 0;
    var bateNome = !q || p.nome.toLowerCase().includes(q);
    var bateStatus = status === 'todos' || (status === 'ativos' && ativo) || (status === 'inativos' && !ativo);
    return bateNome && bateStatus;
  });
  var paginado = paginarDados('produtos', dados);
  window.idsProdutosVisiveis = paginado.dados.map(function(p) { return p.id; });
  $('listaProdutos').innerHTML = paginado.dados.map(function(p) {
    var baixo = Number(p.estoque) <= Number(p.estoque_minimo || 0);
    var ativo = p.ativo !== false && Number(p.ativo) !== 0;
    var imgBtn = '<button class="img-btn" onclick="abrirImageModal(' + p.id + ')" title="Gerenciar imagem">' +
      (p.imagem
        ? '<img src="' + escapeHtml(p.imagem) + '" class="img-thumb">'
        : '<i class="ph ph-image"></i>') +
      '</button>';
    return '<tr class="' + (ativo ? '' : 'inactive-row ') + (baixo && ativo ? 'stock-low-row' : '') + '">' +
      '<td class="bulk-cell">' + checkboxMassaHtml('produtos', p.id, 'Selecionar produto ' + p.nome) + '</td>' +
      '<td>' + p.id + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="nome">' + escapeHtml(p.nome) + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="preco">' + Number(p.preco).toFixed(2) + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="estoque">' + p.estoque + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="produto-' + p.id + '" data-campo="estoque_minimo">' + (p.estoque_minimo ?? 5) + '</td>' +
      '<td><select class="select-inline" data-linha="produto-' + p.id + '" data-campo="ativo">' +
        '<option value="1"' + (ativo ? ' selected' : '') + '>Ativo</option>' +
        '<option value="0"' + (!ativo ? ' selected' : '') + '>Inativo</option>' +
      '</select></td>' +
      '<td class="acoes">' +
        imgBtn +
        (!ativo ? '<span class="status-muted">inativo</span>' : (baixo ? '<span class="stock-alert">baixo</span>' : '')) +
        '<button class="save" onclick="salvarProduto(' + p.id + ')">Salvar</button>' +
        '<button class="delete" onclick="excluirProduto(' + p.id + ')">Inativar</button>' +
      '</td></tr>';
  }).join('') + renderPaginacao('produtos');
  atualizarResumoSelecaoMassa('produtos');
}

async function salvarProduto(id) {
  var linha = 'produto-' + id;
  var produto = {
    nome: lerCelula(linha, 'nome'),
    preco: Number(lerCelula(linha, 'preco').replace(',', '.')),
    estoque: Number(lerCelula(linha, 'estoque')),
    estoque_minimo: Number(lerCelula(linha, 'estoque_minimo')),
    ativo: lerSelect(linha, 'ativo') === '1'
  };
  if (!produto.nome || produto.nome.length < 2 || produto.preco <= 0 || produto.estoque < 0 || produto.estoque_minimo < 0) {
    mostrarToast('erro', 'Dados invalidos para produto.');
    return;
  }
  var resposta = await apiSend('/produtos/' + id, 'PUT', produto);
  if (resposta) {
    await carregarTudo();
    mostrarToast('sucesso', 'Produto atualizado com sucesso!');
  }
}

async function excluirProduto(id) {
  mostrarConfirm('Inativar produto', 'Inativar este produto? Ele sairá da loja do cliente, mas os pedidos antigos continuam salvos.', async function() {
    if (await apiDelete('/produtos/' + id)) {
      await carregarTudo();
      mostrarToast('sucesso', 'Produto inativado com sucesso!');
    }
  });
}

async function excluirProdutosSelecionados() {
  await excluirSelecionadosMassa('produtos', 'produtos selecionados', '/produtos', async function() {
    ultimoProdutos = null;
    await carregarTudo();
  }, 'Inativar');
}

function abrirImageModal(produtoId) {
  imageModalProdutoId = produtoId;
  var produto = cacheProdutos.find(function(p) { return p.id === produtoId; });
  var modal = $('imageModal');
  var uploadArea = $('imageUploadArea');
  var cropperArea = $('imageCropperArea');
  var previewArea = $('imagePreviewArea');
  var fileInput = $('imageFileInput');

  fileInput.value = '';
  cancelarCrop();

  if (produto && produto.imagem) {
    uploadArea.style.display = 'none';
    cropperArea.style.display = 'none';
    previewArea.style.display = 'block';
    $('imagePreviewImg').src = produto.imagem;
  } else {
    uploadArea.style.display = 'block';
    cropperArea.style.display = 'none';
    previewArea.style.display = 'none';
  }

  modal.classList.add('ativo');
  modal.setAttribute('aria-hidden', 'false');
}

function fecharImageModal() {
  var modal = $('imageModal');
  modal.classList.remove('ativo');
  modal.setAttribute('aria-hidden', 'true');
  cancelarCrop();
  imageModalProdutoId = null;
  $('imageFileInput').value = '';
}

function handleImageSelect(event) {
  var file = event.target.files[0];
  if (file) processImageFile(file);
}

function handleImageDrop(event) {
  var file = event.dataTransfer.files[0];
  if (file) processImageFile(file);
}

function processImageFile(file) {
  if (!file.type.match(/^image\/(jpeg|png|webp)$/)) {
    mostrarToast('erro', 'Formato não permitido. Use JPG, PNG ou WebP.');
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    mostrarToast('erro', 'Arquivo muito grande. Máximo 5MB.');
    return;
  }

  var reader = new FileReader();
  reader.onload = function(e) {
    $('imageUploadArea').style.display = 'none';
    $('imagePreviewArea').style.display = 'none';
    $('imageCropperArea').style.display = 'block';

    var img = $('imageCropperImg');
    img.src = e.target.result;

    if (cropperInstance) {
      cropperInstance.destroy();
      cropperInstance = null;
    }

    cropperInstance = new Cropper(img, {
      aspectRatio: 1,
      viewMode: 1,
      minCropBoxSize: 100,
      background: false,
      autoCropArea: 0.9,
    });
  };
  reader.readAsDataURL(file);
}

function cancelarCrop() {
  if (cropperInstance) {
    cropperInstance.destroy();
    cropperInstance = null;
  }
  $('imageCropperArea').style.display = 'none';
  $('imageUploadArea').style.display = 'block';
  $('imageFileInput').value = '';
}

async function editarImagemAtual() {
  var produto = cacheProdutos.find(function(p) { return p.id === imageModalProdutoId; });
  if (!produto || !produto.imagem) return;

  $('imagePreviewArea').style.display = 'none';
  $('imageUploadArea').style.display = 'none';
  $('imageCropperArea').style.display = 'block';

  var img = $('imageCropperImg');

  if (cropperInstance) {
    cropperInstance.destroy();
    cropperInstance = null;
  }

  try {
    var dados = await apiGet('/produtos/' + imageModalProdutoId + '/imagem-original');
    if (dados && dados.url) {
      img.src = dados.url + '?t=' + Date.now();
    } else {
      img.src = produto.imagem + '?t=' + Date.now();
    }
  } catch (e) {
    img.src = produto.imagem + '?t=' + Date.now();
  }

  img.onload = function() {
    cropperInstance = new Cropper(img, {
      aspectRatio: 1,
      viewMode: 1,
      minCropBoxSize: 100,
      background: false,
      autoCropArea: 0.9,
    });
  };
}

async function aplicarCrop() {
  if (!cropperInstance || !imageModalProdutoId) return;

  var canvas = cropperInstance.getCroppedCanvas({ width: 400, height: 400 });
  canvas.toBlob(async function(blob) {
    if (!blob) return;

    var btn = $('btnAplicarCrop');
    btn.textContent = 'Enviando...';
    btn.disabled = true;

    var formData = new FormData();
    formData.append('file', blob, 'produto.webp');

    try {
      var token = sessionStorage.getItem('token');
      var r = await fetch('/api/v1/produtos/' + imageModalProdutoId + '/imagem', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: formData
      });
      var resposta = {};
      try { resposta = await r.json(); } catch { resposta = {}; }

      if (!r.ok) {
        mostrarToast('erro', resposta.detail || 'Erro ao enviar imagem');
      } else {
        mostrarToast('sucesso', 'Imagem atualizada!');
        fecharImageModal();
        ultimoProdutos = null;
        await carregarTudo();
      }
    } catch (err) {
      mostrarToast('erro', 'Erro de conexão ao enviar imagem');
    } finally {
      btn.textContent = 'Salvar imagem';
      btn.disabled = false;
    }
  }, 'image/webp', 0.85);
}

async function removerImagemProduto() {
  if (!imageModalProdutoId) return;
  mostrarConfirm('Remover imagem', 'Remover a imagem deste produto?', async function() {
    var resposta = await apiDelete('/produtos/' + imageModalProdutoId + '/imagem');
    if (resposta !== false) {
      mostrarToast('sucesso', 'Imagem removida!');
      fecharImageModal();
      ultimoProdutos = null;
      await carregarTudo();
    }
  });
}
