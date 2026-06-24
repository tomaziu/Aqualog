var cacheCupons = [];
var ultimoCupons = null;

function dataInputCupom(valor) {
  if (!valor) return '';
  return String(valor).slice(0, 10);
}

function dataDisplayCupom(valor) {
  if (!valor) return 'Sem data';
  var partes = String(valor).slice(0, 10).split('-');
  if (partes.length !== 3) return escapeHtml(valor);
  return partes[2] + '/' + partes[1] + '/' + partes[0];
}

function numeroOpcionalCupom(valor) {
  var texto = String(valor || '').replace('%', '').replace(',', '.').trim();
  if (!texto) return null;
  var numero = Number(texto);
  return Number.isFinite(numero) ? numero : null;
}

async function carregarCupons() {
  var dados = await apiGet('/cupons');
  if (!Array.isArray(dados)) return;
  var atual = JSON.stringify(dados);
  if (ultimoCupons === atual) return;
  ultimoCupons = atual;
  cacheCupons = dados;
  filtrarCupons();
}

function filtrarCupons() {
  var q = ($('filtroCupom') ? $('filtroCupom').value : '').toLowerCase();
  var dados = cacheCupons.filter(function(c) {
    return !q || String(c.codigo || '').toLowerCase().includes(q);
  });
  var paginado = paginarDados('cupons', dados);
  $('listaCupons').innerHTML = paginado.dados.map(function(c) {
    var ativo = Number(c.ativo) === 1 || c.ativo === true;
    var validade = dataDisplayCupom(c.validade_inicio) + ' até ' + dataDisplayCupom(c.validade_fim);
    var limiteUsos = c.limite_usos ? Number(c.limite_usos) : '';
    var usosTexto = Number(c.usos || 0) + (limiteUsos ? '/' + limiteUsos : '');
    return '<tr>' +
      '<td>' + c.id + '</td>' +
      '<td class="editavel" contenteditable="true" data-linha="cupom-' + c.id + '" data-campo="codigo">' + escapeHtml(c.codigo) + '</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="cupom-' + c.id + '" data-campo="percentual">' + Number(c.percentual || 0).toFixed(2) + '%</td>' +
      '<td class="editavel numero-editavel" contenteditable="true" data-linha="cupom-' + c.id + '" data-campo="valor_minimo">' + Number(c.valor_minimo || 0).toFixed(2) + '</td>' +
      '<td><div class="coupon-date-cell">' +
        '<input type="date" data-linha="cupom-' + c.id + '" data-campo="validade_inicio" value="' + dataInputCupom(c.validade_inicio) + '" title="Início">' +
        '<span>até</span>' +
        '<input type="date" data-linha="cupom-' + c.id + '" data-campo="validade_fim" value="' + dataInputCupom(c.validade_fim) + '" title="Fim">' +
        '<small>' + validade + '</small>' +
      '</div></td>' +
      '<td><div class="coupon-uses">' +
        '<strong>' + escapeHtml(usosTexto) + '</strong>' +
        '<input type="number" min="1" placeholder="Sem limite" data-linha="cupom-' + c.id + '" data-campo="limite_usos" value="' + escapeHtml(limiteUsos) + '">' +
      '</div></td>' +
      '<td><select class="select-inline" data-linha="cupom-' + c.id + '" data-campo="ativo">' +
        '<option value="1"' + (ativo ? ' selected' : '') + '>Ativo</option>' +
        '<option value="0"' + (!ativo ? ' selected' : '') + '>Inativo</option>' +
      '</select></td>' +
      '<td class="acoes">' +
        '<button class="save" onclick="salvarCupom(' + c.id + ')">Salvar</button>' +
        '<button class="delete" onclick="excluirCupom(' + c.id + ')">Excluir</button>' +
      '</td>' +
    '</tr>';
  }).join('') + renderPaginacao('cupons');
}

async function salvarCupom(id) {
  var linha = 'cupom-' + id;
  var percentual = numeroOpcionalCupom(lerCelula(linha, 'percentual'));
  var valorMinimo = numeroOpcionalCupom(lerCelula(linha, 'valor_minimo'));
  var limiteUsos = numeroOpcionalCupom(lerCelula(linha, 'limite_usos'));
  var payload = {
    codigo: lerCelula(linha, 'codigo'),
    percentual: percentual,
    ativo: lerSelect(linha, 'ativo') === '1',
    validade_inicio: lerCelula(linha, 'validade_inicio') || null,
    validade_fim: lerCelula(linha, 'validade_fim') || null,
    valor_minimo: valorMinimo || 0,
    limite_usos: limiteUsos || null
  };
  if (!payload.codigo || !payload.percentual || payload.percentual <= 0 || payload.percentual > 100 || payload.valor_minimo < 0) {
    mostrarToast('erro', 'Cupom inválido.');
    return;
  }
  var resposta = await apiSend('/cupons/' + id, 'PUT', payload);
  if (resposta) {
    ultimoCupons = null;
    await carregarCupons();
    mostrarToast('sucesso', 'Cupom atualizado.');
  }
}

async function excluirCupom(id) {
  await mostrarConfirm('Excluir cupom', 'Excluir este cupom?', async function() {
    if (await apiDelete('/cupons/' + id)) {
      ultimoCupons = null;
      await carregarCupons();
      mostrarToast('sucesso', 'Cupom excluído.');
    }
  });
}

$('formCupom').onsubmit = async function(e) {
  e.preventDefault();
  var payload = {
    codigo: valor('cupomCodigo'),
    percentual: numero('cupomPercentual'),
    ativo: valor('cupomAtivo') === '1',
    validade_inicio: valor('cupomValidadeInicio') || null,
    validade_fim: valor('cupomValidadeFim') || null,
    valor_minimo: numero('cupomValorMinimo'),
    limite_usos: valor('cupomLimiteUsos') ? numero('cupomLimiteUsos') : null
  };
  var resposta = await apiSend('/cupons', 'POST', payload);
  if (resposta) {
    $('formCupom').reset();
    $('cupomAtivo').value = '1';
    ultimoCupons = null;
    await carregarCupons();
    mostrarToast('sucesso', 'Cupom cadastrado.');
  }
};
