var cacheSuporte = [];
var suporteAtual = null;

async function carregarSuporte() {
  var dados = await apiGet('/suporte');
  if (!Array.isArray(dados)) return;
  cacheSuporte = dados;
  filtrarSuporte();
}

function filtrarSuporte() {
  var input = $('filtroSuporte');
  if (!input) return;
  var q = (input.value || '').toLowerCase();
  var filtrados = cacheSuporte.filter(function(t) {
    return !q ||
      String(t.pedido_id).includes(q) ||
      (t.cliente && t.cliente.toLowerCase().includes(q)) ||
      (t.telefone && String(t.telefone).toLowerCase().includes(q));
  });

  var lista = $('listaSuporte');
  if (!lista) return;
  if (!filtrados.length) {
    lista.innerHTML = '<div class="support-empty">Nenhuma conversa aberta.</div>';
    return;
  }
  lista.innerHTML = filtrados.map(function(t) {
    var ativo = suporteAtual === t.pedido_id ? ' active' : '';
    var pendentes = Number(t.pendentes || 0);
    return '<div class="support-thread-row">' +
      '<button class="support-thread' + ativo + '" onclick="abrirSuporte(' + t.pedido_id + ')">' +
        '<strong>Pedido #' + t.pedido_id + '</strong>' +
        '<small>' + escapeHtml(t.cliente) + ' - ' + escapeHtml(formatarTelefoneDisplay(t.telefone)) + '</small>' +
        '<span>' + escapeHtml(t.ultima_mensagem || 'Sem mensagem') + '</span>' +
        (pendentes ? '<em>' + pendentes + '</em>' : '') +
      '</button>' +
      '<button class="support-delete" type="button" title="Apagar chat" onclick="apagarSuporte(event, ' + t.pedido_id + ')">x</button>' +
    '</div>';
  }).join('');
}

async function abrirSuporte(pedidoId, preservarResposta) {
  suporteAtual = pedidoId;
  filtrarSuporte();
  var detalhe = $('suporteDetalhe');
  var rascunho = '';
  if (preservarResposta && $('respostaSuporte')) {
    rascunho = $('respostaSuporte').value;
  }
  detalhe.innerHTML = '<div class="support-empty">Carregando conversa...</div>';
  var dados = await apiGet('/suporte/' + pedidoId);
  if (!dados || !dados.pedido) {
    detalhe.innerHTML = '<div class="support-empty">Não foi possível abrir a conversa.</div>';
    return;
  }
  var mensagens = dados.mensagens || [];
  detalhe.innerHTML =
    '<div class="support-head">' +
      '<div class="support-avatar">' + escapeHtml(iniciaisSuporte(dados.pedido.cliente)) + '</div>' +
      '<div><strong>Pedido #' + dados.pedido.pedido_id + '</strong><span>' + escapeHtml(dados.pedido.cliente) + ' - ' + escapeHtml(formatarTelefoneDisplay(dados.pedido.telefone)) + '</span></div>' +
      '<span class="support-live">Ao vivo</span>' +
    '</div>' +
    '<div class="support-messages" id="mensagensSuporte">' +
      mensagens.map(renderMensagemSuporte).join('') +
    '</div>' +
    '<div class="support-reply">' +
      '<textarea id="respostaSuporte" rows="3" placeholder="Digite sua resposta..."></textarea>' +
      '<button class="save support-send" onclick="responderSuporte()">Enviar</button>' +
    '</div>';
  var box = $('mensagensSuporte');
  if (box) box.scrollTop = box.scrollHeight;
  var input = $('respostaSuporte');
  if (input) {
    if (preservarResposta && rascunho) {
      input.value = rascunho;
      input.focus();
    }
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) responderSuporte();
    });
  }
}

function iniciaisSuporte(nome) {
  return String(nome || 'C')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map(function(p) { return p.charAt(0).toUpperCase(); })
    .join('') || 'C';
}

function renderMensagemSuporte(m) {
  var classe = m.autor === 'admin' ? 'admin' : 'cliente';
  var autor = m.autor === 'admin' ? 'Admin' : 'Cliente';
  return '<div class="support-msg ' + classe + '">' +
    '<span class="support-meta">' + autor + '</span>' +
    '<p>' + escapeHtml(m.mensagem) + '</p>' +
    '<span class="support-time">' + formatarData(m.criado_em) + '</span>' +
  '</div>';
}

async function responderSuporte() {
  if (!suporteAtual) return;
  var texto = valor('respostaSuporte');
  if (!texto) return;
  var resposta = await apiSend('/suporte/' + suporteAtual, 'POST', { mensagem: texto });
  if (resposta) {
    await abrirSuporte(suporteAtual);
    await carregarSuporte();
    mostrarToast('sucesso', 'Resposta enviada.');
  }
}

function confirmarApagarSuporte(pedidoId) {
  return new Promise(function(resolve) {
    var antigo = document.getElementById('supportConfirmModal');
    if (antigo) antigo.remove();

    var modal = document.createElement('div');
    modal.id = 'supportConfirmModal';
    modal.className = 'support-confirm-backdrop ativo';
    modal.innerHTML =
      '<div class="support-confirm-panel" role="dialog" aria-modal="true" aria-labelledby="supportConfirmTitle">' +
        '<div class="support-confirm-icon">!</div>' +
        '<div class="support-confirm-copy">' +
          '<h3 id="supportConfirmTitle">Apagar conversa?</h3>' +
          '<p>O chat do pedido #' + escapeHtml(pedidoId) + ' será removido do suporte. O pedido continuará cadastrado.</p>' +
        '</div>' +
        '<div class="support-confirm-actions">' +
          '<button type="button" class="support-confirm-cancel">Cancelar</button>' +
          '<button type="button" class="support-confirm-delete">Apagar chat</button>' +
        '</div>' +
      '</div>';

    function fechar(resultado) {
      modal.classList.remove('ativo');
      setTimeout(function() {
        modal.remove();
        resolve(resultado);
      }, 120);
    }

    modal.querySelector('.support-confirm-cancel').onclick = function() { fechar(false); };
    modal.querySelector('.support-confirm-delete').onclick = function() { fechar(true); };
    modal.addEventListener('click', function(e) {
      if (e.target === modal) fechar(false);
    });
    modal.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') fechar(false);
      if (e.key === 'Enter') fechar(true);
    });
    document.body.appendChild(modal);
    modal.querySelector('.support-confirm-cancel').focus();
  });
}

async function apagarSuporte(event, pedidoId) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }
  if (!await confirmarApagarSuporte(pedidoId)) return;
  if (await apiDelete('/suporte/' + pedidoId)) {
    if (Number(suporteAtual) === Number(pedidoId)) {
      suporteAtual = null;
      var detalhe = $('suporteDetalhe');
      if (detalhe) detalhe.innerHTML = '<div class="support-empty">Selecione uma conversa para responder.</div>';
    }
    await carregarSuporte();
    mostrarToast('sucesso', 'Chat apagado.');
  }
}
