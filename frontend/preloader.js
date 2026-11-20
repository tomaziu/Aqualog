/* ==========================================================================
   ÁquaLog — Preloader padrão (compartilhado por todas as páginas)
   Animação da barra e dos três pontinhos via requestAnimationFrame.
   ========================================================================== */
(function initPreloader() {
  var pre = document.getElementById('preloader');
  if (!pre) return;

  var finalizado = false;
  var rafId = null;
  var inicio = null;

  var barra = pre.querySelector('.preloader-bar');
  var pontos = pre.querySelectorAll('.preloader-dots span');

  function animar(tempo) {
    if (inicio === null) inicio = tempo;
    var t = tempo - inicio;

    /* Barra: desliza da esquerda para a direita em ciclos de 0,95s */
    if (barra) {
      var progresso = (t % 950) / 950;
      var posicao = -110 + progresso * 460;
      barra.style.transform = 'translateX(' + posicao.toFixed(2) + '%)';
    }

    /* Pontinhos brancos: salto em sequência, ciclo de 1s */
    for (var i = 0; i < pontos.length; i++) {
      var fase = ((t % 1000) / 1000 + i / pontos.length) % 1;
      var salto = Math.max(0, Math.sin(fase * Math.PI * 2));
      pontos[i].style.transform = 'translateY(' + (-salto * 9).toFixed(2) + 'px)';
      pontos[i].style.opacity = (0.4 + salto * 0.6).toFixed(2);
    }

    rafId = window.requestAnimationFrame(animar);
  }

  if (window.requestAnimationFrame) {
    rafId = window.requestAnimationFrame(animar);
  }

  function esconder() {
    if (finalizado) return;
    finalizado = true;

    if (rafId !== null && window.cancelAnimationFrame) {
      window.cancelAnimationFrame(rafId);
    }

    pre.classList.add('is-done');
    window.setTimeout(function() {
      if (pre.parentNode) pre.parentNode.removeChild(pre);
    }, 500);
  }

  if (document.readyState === 'complete') {
    window.setTimeout(esconder, 900);
  } else {
    window.addEventListener('load', function() {
      window.setTimeout(esconder, 900);
    }, { once: true });
  }

  /* Segurança: nunca deixa a página bloqueada se um recurso externo falhar */
  window.setTimeout(esconder, 5000);
})();
