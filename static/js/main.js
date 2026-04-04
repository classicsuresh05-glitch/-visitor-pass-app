// ═══════════════════════════════════════════════════════════
//  VISITORPASS PRO — MAIN JS
// ═══════════════════════════════════════════════════════════

/* ── NAVBAR scroll effect ──────────────────────────────── */
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  });
}

/* ── Hamburger mobile menu ─────────────────────────────── */
const hamburger = document.getElementById('hamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    document.getElementById('navbar').classList.toggle('menu-open');
    hamburger.classList.toggle('active');
  });
}

/* ── Scroll reveal ─────────────────────────────────────── */
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length) {
  const ro = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity   = '1';
        e.target.style.transform = 'none';
        ro.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  revealEls.forEach(el => {
    el.style.opacity   = '0';
    el.style.transform = 'translateY(32px)';
    el.style.transition= 'opacity .7s ease, transform .7s ease';
    ro.observe(el);
  });
}

/* ── Auto-dismiss flash messages ──────────────────────── */
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => {
    f.style.opacity   = '0';
    f.style.transform = 'translateX(120%)';
    f.style.transition= 'all .4s ease';
    setTimeout(() => f.remove(), 400);
  });
}, 5000);
