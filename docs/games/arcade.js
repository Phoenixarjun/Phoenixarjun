/**
 * Titanium Hacker Developer Arcade — Main Portal Controller
 * Drives auto-rotation (5s interval), preview crossfade, manual selection, and terminal effects.
 */

(function () {
  'use strict';

  // Fallback games manifest for instant offline/file:// support
  const DEFAULT_GAMES = [
    {
      id: "packet-breaker",
      number: "01",
      name: "Packet Breaker",
      slug: "packet-breaker",
      category: "Brick Breaker // Arcade Physics",
      description: "Deflect data packets, destroy system faults, and survive progressively harder levels.",
      url: "./packet-breaker/",
      preview: "./assets/previews/packet-breaker.gif",
      controls: "Arrow keys / A-D / Mouse / Touch to steer paddle. Space to launch."
    },
    {
      id: "circuit-pinball",
      number: "02",
      name: "Circuit Pinball",
      slug: "circuit-pinball",
      category: "Pinball // Reactive Circuits",
      description: "Keep the signal alive through reactive bumpers, flippers, and high-energy circuits.",
      url: "./circuit-pinball/",
      preview: "./assets/previews/circuit-pinball.gif",
      controls: "Left/Right Arrows or A/D for flippers. Down Arrow or Space for plunger."
    },
    {
      id: "runtime-rush",
      number: "03",
      name: "Runtime Rush",
      slug: "runtime-rush",
      category: "3D Runner // WebGL Engine",
      description: "Navigate infrastructure failures in a fast-paced futuristic runner.",
      url: "./runtime-rush/",
      preview: "./assets/previews/runtime-rush.gif",
      controls: "A/D or Left/Right to change lanes. W/Up to jump. S/Down to slide."
    },
    {
      id: "firewall-defense",
      number: "04",
      name: "Firewall Defense",
      slug: "firewall-defense",
      category: "Tower Defense // Network Strategy",
      description: "Defend the network across 30 waves with six weapons, tactical powers, and boss encounters.",
      url: "./firewall-defense/",
      preview: "./assets/previews/firewall-defense.gif",
      controls: "1–6 Select module • E/O/Q Tactical powers • Space Launch wave • Click/Tap to place and upgrade"
    },
    {
      id: "stack-overflow",
      number: "05",
      name: "Stack Overflow",
      slug: "stack-overflow",
      category: "Precision Physics // Tower Protocol",
      description: "Build a stable server tower through precise timing and increasingly difficult placements.",
      url: "./stack-overflow/",
      preview: "./assets/previews/stack-overflow.gif",
      controls: "Space / Click / Tap to drop server blocks. Shift for precision focus."
    }
  ];

  let games = DEFAULT_GAMES;
  let currentIndex = 0;
  let isAutoRotating = true;
  let rotationTimer = null;
  let progressTimer = null;
  const ROTATION_INTERVAL = 5000; // 5 seconds per game
  const PROGRESS_STEP = 50; // update progress every 50ms
  let elapsed = 0;

  // DOM Elements
  const previewImg = document.getElementById('previewImg');
  const previewBadgeNum = document.getElementById('previewBadgeNum');
  const previewBadgeName = document.getElementById('previewBadgeName');
  const detailsIndex = document.getElementById('detailsIndex');
  const detailsTitle = document.getElementById('detailsTitle');
  const detailsCategory = document.getElementById('detailsCategory');
  const detailsDesc = document.getElementById('detailsDesc');
  const detailsControls = document.getElementById('detailsControls');
  const launchBtn = document.getElementById('launchBtn');
  const rotationControl = document.getElementById('rotationControl');
  const rotationStatusText = document.getElementById('rotationStatusText');
  const rotationProgressFill = document.getElementById('rotationProgressFill');
  const catalogGrid = document.getElementById('catalogGrid');
  const terminalCmd = document.getElementById('portalTerminalCmd');
  const terminalCursor = document.getElementById('portalTerminalCursor');

  // Terminal Typing Animation for Portal Header
  function initTerminalTyping() {
    if (!terminalCmd) return;
    const fullText = " ls --developer-arcade";
    const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      terminalCmd.textContent = fullText;
      return;
    }

    let i = 0;
    function type() {
      if (i < fullText.length) {
        terminalCmd.textContent += fullText.charAt(i);
        i++;
        setTimeout(type, 45);
      } else {
        setTimeout(() => {
          if (terminalCursor) terminalCursor.style.opacity = '0.7';
        }, 1500);
      }
    }
    setTimeout(type, 200);
  }

  // Render Catalog Selector Cards
  function renderCatalogCards() {
    if (!catalogGrid) return;
    catalogGrid.innerHTML = '';

    games.forEach((game, index) => {
      const card = document.createElement('div');
      card.className = 'game-card' + (index === currentIndex ? ' active' : '');
      card.setAttribute('role', 'button');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', `Select game ${game.number}: ${game.name}`);

      card.innerHTML = `
        <div class="game-card-top">
          <span class="game-card-num">${game.number}</span>
          <span class="game-card-status"></span>
        </div>
        <div class="game-card-title">${game.name}</div>
        <div class="game-card-category">${game.category.split('//')[0].trim()}</div>
        <div class="card-timer-bar" id="cardTimerBar_${index}"></div>
      `;

      card.addEventListener('click', () => {
        selectGame(index, true); // true = pause on user interaction
      });

      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          selectGame(index, true);
        }
      });

      catalogGrid.appendChild(card);
    });
  }

  // Switch to a specific game with crossfade
  function selectGame(index, pauseAutoRotation) {
    if (index < 0 || index >= games.length) return;
    currentIndex = index;
    const game = games[currentIndex];

    // Reset progress timers
    elapsed = 0;
    updateProgressBars(0);

    if (pauseAutoRotation) {
      pauseRotation();
    }

    // Crossfade preview image
    if (previewImg) {
      previewImg.classList.add('fade-out');
      setTimeout(() => {
        previewImg.src = game.preview;
        previewImg.alt = `${game.name} gameplay preview`;
        previewImg.onload = () => {
          previewImg.classList.remove('fade-out');
        };
      }, 150);
    }

    // Update overlay badge
    if (previewBadgeNum) previewBadgeNum.textContent = game.number;
    if (previewBadgeName) previewBadgeName.textContent = game.name.toUpperCase();

    // Update details panel
    if (detailsIndex) detailsIndex.textContent = `MODULE // ${game.number}`;
    if (detailsTitle) detailsTitle.textContent = game.name;
    if (detailsCategory) detailsCategory.textContent = game.category;
    if (detailsDesc) detailsDesc.textContent = game.description;
    if (detailsControls) detailsControls.textContent = game.controls;
    if (launchBtn) {
      launchBtn.href = game.url;
      launchBtn.innerHTML = `<span>PLAY ${game.name.toUpperCase()}</span> <span aria-hidden="true">↗</span>`;
      launchBtn.setAttribute('aria-label', `Play ${game.name}`);
    }

    // Update catalog cards active states
    const cards = catalogGrid ? catalogGrid.querySelectorAll('.game-card') : [];
    cards.forEach((card, idx) => {
      if (idx === currentIndex) {
        card.classList.add('active');
      } else {
        card.classList.remove('active');
        const timerBar = document.getElementById(`cardTimerBar_${idx}`);
        if (timerBar) timerBar.style.width = '0%';
      }
    });
  }

  // Update progress bar fills
  function updateProgressBars(pct) {
    const formatted = `${Math.min(100, Math.max(0, pct))}%`;
    if (rotationProgressFill) {
      rotationProgressFill.style.width = isAutoRotating ? formatted : '0%';
    }
    const currentCardBar = document.getElementById(`cardTimerBar_${currentIndex}`);
    if (currentCardBar) {
      currentCardBar.style.width = isAutoRotating ? formatted : '0%';
    }
  }

  // Step rotation timer
  function startProgressCycle() {
    clearInterval(progressTimer);
    elapsed = 0;
    updateProgressBars(0);

    progressTimer = setInterval(() => {
      if (!isAutoRotating) return;
      elapsed += PROGRESS_STEP;
      const pct = (elapsed / ROTATION_INTERVAL) * 100;
      updateProgressBars(pct);

      if (elapsed >= ROTATION_INTERVAL) {
        elapsed = 0;
        const nextIdx = (currentIndex + 1) % games.length;
        selectGame(nextIdx, false);
      }
    }, PROGRESS_STEP);
  }

  // Pause auto-rotation
  function pauseRotation() {
    isAutoRotating = false;
    clearInterval(progressTimer);
    updateProgressBars(0);
    if (rotationControl) {
      rotationControl.classList.add('is-paused');
    }
    if (rotationStatusText) {
      rotationStatusText.textContent = 'PAUSED (CLICK TO RESUME)';
    }
  }

  // Resume auto-rotation
  function resumeRotation() {
    isAutoRotating = true;
    if (rotationControl) {
      rotationControl.classList.remove('is-paused');
    }
    if (rotationStatusText) {
      rotationStatusText.textContent = 'AUTO-ROTATING';
    }
    startProgressCycle();
  }

  // Toggle rotation
  function toggleRotation() {
    if (isAutoRotating) {
      pauseRotation();
    } else {
      resumeRotation();
    }
  }

  // Keyboard navigation for arcade catalog
  function initKeyboardControls() {
    window.addEventListener('keydown', (e) => {
      // Ignore if user is inside an input or textarea
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIdx = (currentIndex + 1) % games.length;
        selectGame(nextIdx, true);
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIdx = (currentIndex - 1 + games.length) % games.length;
        selectGame(prevIdx, true);
      } else if (e.key.toLowerCase() === 'p') {
        e.preventDefault();
        toggleRotation();
      }
    });
  }

  // Fetch games.json or use fallback
  async function loadGamesManifest() {
    try {
      const response = await fetch('./games.json');
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
          games = data;
        }
      }
    } catch (err) {
      // Silently fall back to DEFAULT_GAMES
      games = DEFAULT_GAMES;
    }
  }

  // Initialize
  async function init() {
    await loadGamesManifest();
    renderCatalogCards();
    selectGame(0, false);
    initTerminalTyping();
    initKeyboardControls();

    if (rotationControl) {
      rotationControl.addEventListener('click', toggleRotation);
    }

    startProgressCycle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

