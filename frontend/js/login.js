if (sessionStorage.getItem('token') && sessionStorage.getItem('tipo') === 'admin') {
  document.getElementById('tela-login-admin').style.display = 'none';
}

async function loginAdmin() {
  var senha = document.getElementById('admin-senha').value.trim();
  if (!senha) return;
  document.getElementById('erro-admin').textContent = '';
  try {
    var r = await fetch(API + API_PREFIX + '/admin/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ senha: senha })
    });
    var json = await r.json();
    if (!r.ok) {
      document.getElementById('erro-admin').textContent = json.detail || 'Senha incorreta';
      return;
    }
    sessionStorage.setItem('token', json.access_token);
    sessionStorage.setItem('tipo', json.tipo);
    sessionStorage.setItem('nome', json.nome);
    document.getElementById('tela-login-admin').style.display = 'none';
    await carregarTudo();
    if (typeof iniciarSSEAdmin === 'function') {
      iniciarSSEAdmin();
    }
    if (typeof iniciarExpiracaoPixAutomatica === 'function') {
      iniciarExpiracaoPixAutomatica();
    }
  } catch {
    document.getElementById('erro-admin').textContent = 'Erro de conexao';
  }
}

function logoutAdmin() {
  sessionStorage.clear();
  location.reload();
}

document.getElementById('admin-senha').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') loginAdmin();
});
