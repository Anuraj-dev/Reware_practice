// Enhanced Main JS for interactivity, transitions, and responsive behavior
(function(){
  // Enhanced Hero video autoplay with better error handling
  const v = document.getElementById('heroVideo');
  if (v) {
    v.removeAttribute('controls');
    
    const tryPlay = async () => {
      try {
        await v.play();
      } catch (error) {
        console.warn('Video autoplay failed:', error);
        // Fallback: show a poster image or static background
        v.style.display = 'none';
      }
    };
    
    if (document.readyState === 'complete') {
      tryPlay();
    } else {
      window.addEventListener('load', tryPlay, { once: true });
    }
    
    document.addEventListener('visibilitychange', () => { 
      if (!document.hidden) tryPlay(); 
    });
    
    // Pause video when out of viewport for performance
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          tryPlay();
        } else {
          v.pause();
        }
      });
    });
    observer.observe(v);
  }

  // Enhanced Flash messages with better animations
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((el) => {
    const closeBtn = el.querySelector('.flash-close');
    const hide = () => { 
      el.classList.add('hide'); 
      setTimeout(() => el.remove(), 300); 
    };
    
    if (closeBtn) closeBtn.addEventListener('click', hide);
    
    // Auto-dismiss with different timeouts based on severity
    const isDanger = el.classList.contains('danger') || el.classList.contains('error');
    const isWarning = el.classList.contains('warning');
    const timeout = isDanger ? 8000 : (isWarning ? 6000 : 4000);
    setTimeout(hide, timeout);
    
    // Add swipe-to-dismiss for touch devices
    let startX = 0;
    let currentX = 0;
    let isDragging = false;
    
    el.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
    });
    
    el.addEventListener('touchmove', (e) => {
      if (!isDragging) return;
      currentX = e.touches[0].clientX;
      const diffX = currentX - startX;
      if (diffX > 0) {
        el.style.transform = `translateX(${diffX}px)`;
        el.style.opacity = Math.max(0.3, 1 - diffX / 200);
      }
    });
    
    el.addEventListener('touchend', () => {
      if (!isDragging) return;
      isDragging = false;
      const diffX = currentX - startX;
      
      if (diffX > 100) {
        hide();
      } else {
        el.style.transform = '';
        el.style.opacity = '';
      }
    });
  });

  // Set background images from data-bg
  document.querySelectorAll('.auth-visual.bg[data-bg]').forEach(el => {
    const src = el.getAttribute('data-bg');
    if (src) el.style.backgroundImage = `url('${src}')`;
  });

  // Auth image/visual swap-out on submit
  const registerForm = document.getElementById('registerForm');
  const registerVisual = document.querySelector('.auth-visual.bg[data-bg*="image3.jpg"]');
  if (registerForm && registerVisual) {
    registerForm.addEventListener('submit', () => {
      registerVisual.classList.add('swap-out');
    });
  }

  const loginForm = document.getElementById('loginForm');
  const loginVisual = document.querySelector('.auth-visual.bg[data-bg*="image4.jpg"]');
  if (loginForm && loginVisual) {
    loginForm.addEventListener('submit', () => {
      loginVisual.classList.add('swap-out');
    });
  }

  // Client-side transition between Register and Login without immediate navigation
  const transitionLinks = document.querySelectorAll('[data-auth-transition]');
  transitionLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      // Only intercept primary button clicks without modifier keys
      if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

      const container = document.querySelector('.auth-split');
      if (!container) return;
      e.preventDefault();

      // Add transition classes
      const visual = container.querySelector('.auth-visual.bg');
      const card = container.querySelector('.auth-card');
      if (visual) visual.classList.add('swap-out');
      if (card) card.classList.add('slide-fade-out');

      // After animation, navigate
      setTimeout(() => { window.location.href = link.href; }, 350);
    });
  });

  // Confirm password indicator
  const pwd = document.getElementById('password');
  const confirm = document.getElementById('confirm_password');
  if (pwd && confirm) {
    const ensureIndicator = () => {
      let indicator = confirm.parentElement.querySelector('.match-indicator');
      if (!indicator) {
        indicator = document.createElement('small');
        indicator.className = 'match-indicator help';
        confirm.parentElement.appendChild(indicator);
      }
      return indicator;
    };
    const update = () => {
      const indicator = ensureIndicator();
      if (!confirm.value) { indicator.textContent = ''; indicator.removeAttribute('data-state'); return; }
      const ok = confirm.value === pwd.value && confirm.value.length >= 6;
      indicator.textContent = ok ? 'Passwords match' : 'Passwords do not match';
      indicator.setAttribute('data-state', ok ? 'ok' : 'bad');
    };
    ['input','change','keyup'].forEach(evt => {
      pwd.addEventListener(evt, update);
      confirm.addEventListener(evt, update);
    });
  }

  // Simple confirm for delete forms
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', (e) => {
      const msg = form.getAttribute('data-confirm') || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // Enhanced search with debouncing and better UX
  const search = document.getElementById('searchListings');
  const grid = document.getElementById('listingGrid');
  if (search && grid) {
    const cards = Array.from(grid.querySelectorAll('.listing-card'));
    let searchTimeout;
    
    const filter = () => {
      const q = search.value.trim().toLowerCase();
      let visibleCount = 0;
      
      cards.forEach((card, index) => {
        const hay = (card.getAttribute('data-title') || '').toLowerCase();
        const show = !q || hay.includes(q);
        
        if (show) {
          visibleCount++;
          card.style.display = '';
          // Stagger animations for better visual effect
          card.style.animationDelay = `${index * 50}ms`;
          card.classList.add('fade-in');
        } else {
          card.style.display = 'none';
          card.classList.remove('fade-in');
        }
      });
      
      // Show "no results" message if needed
      let noResultsMsg = grid.querySelector('.no-results');
      if (visibleCount === 0 && q) {
        if (!noResultsMsg) {
          noResultsMsg = document.createElement('div');
          noResultsMsg.className = 'no-results';
          noResultsMsg.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
              <p>No items found for "${q}"</p>
              <button class="btn ghost" onclick="document.getElementById('searchListings').value=''; this.closest('.no-results').remove(); document.querySelectorAll('.listing-card').forEach(c => c.style.display = '');">Clear search</button>
            </div>
          `;
          grid.appendChild(noResultsMsg);
        }
      } else if (noResultsMsg) {
        noResultsMsg.remove();
      }
    };
    
    const debouncedFilter = () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(filter, 300);
    };
    
    ['input', 'change'].forEach(evt => search.addEventListener(evt, debouncedFilter));
    
    // Add keyboard shortcuts
    search.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        search.value = '';
        filter();
        search.blur();
      }
    });
  }

  // Enhanced responsive navigation
  const createMobileMenu = () => {
    const nav = document.querySelector('.nav');
    const navlinks = document.querySelector('.navlinks');
    
    if (!nav || !navlinks || window.innerWidth > 768) return;
    
    let mobileMenuBtn = nav.querySelector('.mobile-menu-btn');
    if (!mobileMenuBtn) {
      mobileMenuBtn = document.createElement('button');
      mobileMenuBtn.className = 'mobile-menu-btn btn ghost';
      mobileMenuBtn.innerHTML = '☰';
      mobileMenuBtn.setAttribute('aria-label', 'Toggle navigation menu');
      
      mobileMenuBtn.addEventListener('click', () => {
        navlinks.classList.toggle('show-mobile');
        mobileMenuBtn.innerHTML = navlinks.classList.contains('show-mobile') ? '✕' : '☰';
      });
      
      nav.appendChild(mobileMenuBtn);
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && navlinks.classList.contains('show-mobile')) {
        navlinks.classList.remove('show-mobile');
        mobileMenuBtn.innerHTML = '☰';
      }
    });
  };
  
  // Handle window resize
  const handleResize = () => {
    createMobileMenu();
    
    // Remove mobile menu on larger screens
    if (window.innerWidth > 768) {
      const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
      const navlinks = document.querySelector('.navlinks');
      if (mobileMenuBtn) mobileMenuBtn.remove();
      if (navlinks) navlinks.classList.remove('show-mobile');
    }
  };
  
  window.addEventListener('resize', debounce(handleResize, 250));
  window.addEventListener('load', createMobileMenu);

  // Utility function for debouncing
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Add fade-in animation CSS if not already present
  if (!document.querySelector('#dynamic-animations')) {
    const style = document.createElement('style');
    style.id = 'dynamic-animations';
    style.textContent = `
      .fade-in {
        animation: fadeIn 0.3s ease-out forwards;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .mobile-menu-btn {
        display: none;
        font-size: 1.25rem;
        padding: 0.5rem;
        min-width: 44px;
        justify-content: center;
      }
      
      @media (max-width: 768px) {
        .mobile-menu-btn {
          display: flex;
        }
        
        .navlinks {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--bg-nav);
          border-top: 1px solid var(--glass-border);
          padding: var(--space-md);
          flex-direction: column;
          transform: translateY(-100%);
          opacity: 0;
          visibility: hidden;
          transition: var(--transition);
        }
        
        .navlinks.show-mobile {
          transform: translateY(0);
          opacity: 1;
          visibility: visible;
        }
        
        .navlinks a {
          padding: var(--space-sm) var(--space-md);
          border-radius: var(--radius);
          text-align: center;
        }
      }
    `;
    document.head.appendChild(style);
  }
})();
