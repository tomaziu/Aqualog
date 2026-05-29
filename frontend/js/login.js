if (sessionStorage.getItem('admin_logado') === '1') {
  document.getElementById('tela-login-admin').style.display = 'none';
}

async function loginAdmin() {
  const senha = document.getElementById('admin-senha').value.trim();
  if (!senha) return;
  document.getElementById('erro-admin').textContent = '';
  try {
    const r = await fetch(API + '/admin/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ senha })
    });
    if (!r.ok) {
      document.getElementById('erro-admin').textContent = 'Senha incorreta';
      return;
    }
    sessionStorage.setItem('admin_logado', '1');
    document.getElementById('tela-login-admin').style.display = 'none';
    carregarTudo();
  } catch {
    document.getElementById('erro-admin').textContent = 'Erro de conexão';
  }
}

function logoutAdmin() {
  sessionStorage.removeItem('admin_logado');
  location.reload();
}

document.getElementById('admin-senha').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') loginAdmin();
});
