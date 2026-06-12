/* ─────────────────────────────────────────────────────────────────────────────
   NutriPrint — Premium Splash Screen Engine
   Sequence: background → particles → seed → sprout → logo reveal →
             food orbit → text entrance → checklist → fade out
   Total duration: ~2.8 s (skipped on repeat visits via localStorage)
   ───────────────────────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  /* ── Skip on repeat visits ─────────────────────────────────────────────── */
  const SKIP_KEY = 'np_splash_seen_v3';
  const splash   = document.getElementById('splashScreen');
  if (!splash) return;

  if (sessionStorage.getItem(SKIP_KEY)) {
    splash.style.display = 'none';
    _afterSplash();
    return;
  }
  sessionStorage.setItem(SKIP_KEY, '1');

  /* ── Canvas particle system ─────────────────────────────────────────────── */
  const canvas = document.getElementById('splashCanvas');
  let   raf    = null;

  if (canvas) {
    const ctx = canvas.getContext('2d');
    const FOODS = ['🥗','🌿','🫘','🥛','🍚','🥕','🥦','🧆','🫓','🥬','🍲','🌾','🥜'];
    const particles = [];

    function resizeCanvas () {
      canvas.width  = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas, { passive: true });

    /* Spawn particles spread across full screen */
    for (let i = 0; i < 28; i++) {
      particles.push({
        x      : Math.random() * window.innerWidth,
        y      : Math.random() * window.innerHeight,
        emoji  : FOODS[Math.floor(Math.random() * FOODS.length)],
        size   : Math.random() * 18 + 12,
        vx     : (Math.random() - 0.5) * 0.55,
        vy     : (Math.random() - 0.5) * 0.55,
        alpha  : Math.random() * 0.22 + 0.06,
        rot    : Math.random() * Math.PI * 2,
        rotV   : (Math.random() - 0.5) * 0.012,
        /* parallax depth: 0=slow, 1=fast */
        depth  : Math.random(),
      });
    }

    /* Mouse parallax offset */
    let mouseX = 0, mouseY = 0;
    document.addEventListener('mousemove', e => {
      mouseX = (e.clientX / window.innerWidth  - 0.5) * 18;
      mouseY = (e.clientY / window.innerHeight - 0.5) * 18;
    }, { passive: true });

    function drawParticles () {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (const p of particles) {
        const px = p.x + mouseX * p.depth;
        const py = p.y + mouseY * p.depth;
        ctx.save();
        ctx.globalAlpha = p.alpha;
        ctx.translate(px, py);
        ctx.rotate(p.rot);
        ctx.font = `${p.size}px serif`;
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(p.emoji, 0, 0);
        ctx.restore();

        p.x   += p.vx;
        p.y   += p.vy;
        p.rot += p.rotV;

        /* wrap edges */
        const pad = 40;
        if (p.x < -pad) p.x = canvas.width  + pad;
        if (p.x > canvas.width  + pad) p.x = -pad;
        if (p.y < -pad) p.y = canvas.height + pad;
        if (p.y > canvas.height + pad) p.y = -pad;
      }
      raf = requestAnimationFrame(drawParticles);
    }
    drawParticles();
  }

  /* ── Food-icon orbit ────────────────────────────────────────────────────── */
  const orbitTrack = document.getElementById('splashOrbit');
  if (orbitTrack) {
    const icons = ['🌾','🫘','🥛','🥕','🥦','🧆','🍚','🌿'];
    icons.forEach((icon, i) => {
      const deg  = (360 / icons.length) * i;
      const dot  = document.createElement('span');
      dot.className = 'splash-orbit-dot';
      dot.textContent = icon;
      dot.style.setProperty('--i', i);
      dot.style.setProperty('--total', icons.length);
      dot.setAttribute('aria-hidden', 'true');
      orbitTrack.appendChild(dot);
    });
  }

  /* ── Checklist sequencer ────────────────────────────────────────────────── */
  const checkItems  = document.querySelectorAll('.splash-check-item');
  const checkDelays = [600, 900, 1200, 1500, 1900];

  checkItems.forEach((el, i) => {
    setTimeout(() => el.classList.add('splash-check-visible'), checkDelays[i] || 600 + i * 280);
  });

  /* ── Progress bar ───────────────────────────────────────────────────────── */
  const progressBar = document.getElementById('splashProgress');
  let   prog        = 0;
  const progressTimer = setInterval(() => {
    prog = Math.min(prog + (100 / 18), 100);
    if (progressBar) progressBar.style.width = prog + '%';
    if (prog >= 100) clearInterval(progressTimer);
  }, 140);

  /* ── Dismiss ────────────────────────────────────────────────────────────── */
  function hideSplash () {
    if (splash._hiding) return;
    splash._hiding = true;

    if (raf) cancelAnimationFrame(raf);
    clearInterval(progressTimer);

    splash.classList.add('splash-exit');
    setTimeout(() => {
      splash.style.display = 'none';
      _afterSplash();
    }, 680);
  }

  /* Hard deadline: 3.2 s */
  const deadline = setTimeout(hideSplash, 3200);

  /* Allow skip on click/tap */
  splash.addEventListener('click', () => { clearTimeout(deadline); hideSplash(); });

  /* Auto-hide after checklist completes */
  setTimeout(() => { clearTimeout(deadline); hideSplash(); }, 2750);

  function _afterSplash () {
    if (typeof initHeroAnimations === 'function') initHeroAnimations();
    /* Fire custom event so other scripts can react */
    document.dispatchEvent(new CustomEvent('splashDone'));
  }
})();
