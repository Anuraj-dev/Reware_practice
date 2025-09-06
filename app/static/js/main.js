// Main JS for interactivity and transitions
(function(){
  // Hero video autoplay resilience
  const v = document.getElementById('heroVideo');
  if (v) {
    v.removeAttribute('controls');
    const tryPlay = () => v.play().catch(() => {});
    if (document.readyState === 'complete') tryPlay();
    else window.addEventListener('load', tryPlay, { once: true });
    document.addEventListener('visibilitychange', () => { if (!document.hidden) tryPlay(); });
  }

  // Auth image swap-out on submit
  const registerForm = document.getElementById('registerForm');
  const registerImg = document.getElementById('registerVisual');
  if (registerForm && registerImg) {
    registerForm.addEventListener('submit', () => {
      registerImg.classList.add('swap-out');
    });
  }

  const loginForm = document.getElementById('loginForm');
  const loginImg = document.getElementById('loginVisual');
  if (loginForm && loginImg) {
    loginForm.addEventListener('submit', () => {
      loginImg.classList.add('swap-out');
    });
  }

  // Client-side transition between Register and Login without immediate navigation
  // Adds a subtle fade-slide transition on the visual and card, then proceeds to navigate.
  const transitionLinks = document.querySelectorAll('[data-auth-transition]');
  transitionLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      // Only intercept primary button clicks without modifier keys
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

      const container = document.querySelector('.auth-split');
      if (!container) return;
      e.preventDefault();

      // Add transition classes
      const visual = container.querySelector('.auth-visual img');
      const card = container.querySelector('.auth-card');
      if (visual) visual.classList.add('swap-out');
      if (card) card.classList.add('slide-fade-out');

      // After animation, navigate
      setTimeout(() => { window.location.href = link.href; }, 350);
    });
  });
})();
