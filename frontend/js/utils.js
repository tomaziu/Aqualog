const $ = (id) => document.getElementById(id);

function valor(id) {
  const el = $(id);
  return el ? el.value.trim() : '';
}

function numero(id) {
  const n = Number(valor(id));
  return Number.isFinite(n) ? n : 0;
}

function escapeHtml(valor) {
  return String(valor ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function lerCelula(idLinha, campo) {
  const el = document.querySelector(`[data-linha="${idLinha}"][data-campo="${campo}"]`);
  return el ? el.textContent.trim() : '';
}

function lerSelect(idLinha, campo) {
  const el = document.querySelector(`[data-linha="${idLinha}"][data-campo="${campo}"]`);
  return el ? el.value : '';
}

function formatarData(d) {
  if (!d) return '-';
  const dt = new Date(d);
  return dt.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusTexto(s) {
  const map = {
    'recebido': 'Recebido',
    'em_preparo': 'Em preparo',
    'saiu_para_entrega': 'Saiu p/ entrega',
    'entregue': 'Entregue',
    'cancelado': 'Cancelado'
  };
  return map[s] || s;
}

function mostrarTela(id) {
  document.querySelectorAll('.tela').forEach(t => t.classList.remove('ativa'));
  $(id).classList.add('ativa');
  carregarTudo();
}

function renderCliente(c) {
  return `<tr>
    <td>${c.id}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="nome">${escapeHtml(c.nome)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="telefone">${escapeHtml(c.telefone)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="endereco">${escapeHtml(c.endereco)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="bairro">${escapeHtml(c.bairro)}</td>
    <td class="editavel" contenteditable="true" data-linha="cliente-${c.id}" data-campo="referencia">${escapeHtml(c.referencia || '')}</td>
    <td class="acoes">
      <button class="save" onclick="salvarCliente(${c.id})">Salvar</button>
      <button class="delete" onclick="excluirCliente(${c.id})">Excluir</button>
    </td>
  </tr>`;
}
