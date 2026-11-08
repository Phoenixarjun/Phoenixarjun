/**
 * Titanium Hacker Developer Arcade — Shared Top Navigation
 * Standardized header with one-time terminal typing animation.
 */
(function () {
  'use strict';

  function initNav() {
    const container = document.getElementById('arcade-nav') || document.querySelector('.arcade-nav-container');
    if (!container) return;

    // Determine slug from data-slug attribute or URL pathname
    let slug = container.getAttribute('data-slug');
    if (!slug) {
      const path = window.location.pathname;
      const knownSlugs = ['packet-breaker', 'circuit-pinball', 'runtime-rush', 'firewall-defense', 'stack-overflow'];
      for (const s of knownSlugs) {
        if (path.indexOf(s) !== -1) {
          slug = s;
          break;
        }
      }
    }
    if (!slug) slug = 'arcade';

    const commandText = 'play --' + slug;
    const arcadeHomeUrl = '../index.html';
    const profileUrl = 'https://github.com/Phoenixarjun';

    container.className = 'arcade-nav-bar';
    container.setAttribute('role', 'navigation');
    container.setAttribute('aria-label', 'Arcade Navigation');

    container.innerHTML = 
      '<div class="arcade-nav-left">' +
        '<span class="arcade-nav-prompt">naresh@github:~$</span>' +
        '<span class="arcade-nav-command" id="arcadeNavCmd"></span>' +
        '<span class="arcade-nav-cursor" id="arcadeNavCursor">_</span>' +
      '</div>' +
      '<div class="arcade-nav-right">' +
        '<a class="arcade-nav-btn" href="' + arcadeHomeUrl + '" title="Return to Developer Arcade">' +
          '<span>◀</span> Back to Arcade' +
        '</a>' +
        '<a class="arcade-nav-btn arcade-nav-btn-primary" href="' + profileUrl + '" target="_blank" rel="noopener noreferrer" title="View Naresh\'s GitHub Profile">' +
          'GitHub Profile <span class="arrow">↗</span>' +
        '</a>' +
      '</div>';

    const cmdEl = document.getElementById('arcadeNavCmd');
    const cursorEl = document.getElementById('arcadeNavCursor');

    // Honor prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      if (cmdEl) cmdEl.textContent = ' ' + commandText;
      if (cursorEl) cursorEl.classList.add('stopped');
      return;
    }

    let index = 0;
    const fullText = ' ' + commandText;
    const charDelay = 42; // ms per character

    function typeChar() {
      if (!cmdEl) return;
      if (index < fullText.length) {
        cmdEl.textContent += fullText.charAt(index);
        index++;
        setTimeout(typeChar, charDelay);
      } else {
        // Animation complete: hold completed command and stop cursor animation
        setTimeout(function () {
          if (cursorEl) cursorEl.classList.add('stopped');
        }, 1200);
      }
    }

    // Small startup pause before typing
    setTimeout(typeChar, 120);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNav);
  } else {
    initNav();
  }
})();

