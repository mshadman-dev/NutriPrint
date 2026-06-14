/**
 * NutriPrint — Auth helpers
 * ─────────────────────────────────────────────────────────────────────────────
 * Session is written by demo_mode.js (NutriDemo.activate) and cleared by
 * NutriAuth.logout().  The real Supabase OTP backend (routers/auth.py) is not
 * yet connected to the frontend; this file handles client-side session state.
 *
 * Session key: np_teacher_session
 */
(function () {
  'use strict';

  const SESSION_KEY = 'np_teacher_session';

  const NutriAuth = {

    /** Returns the stored session object, or null. */
    getSession() {
      try {
        return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
      } catch (_) {
        return null;
      }
    },

    /** True when a valid session exists. */
    isLoggedIn() {
      return this.getSession() !== null;
    },

    /** Clear the session. */
    logout() {
      localStorage.removeItem(SESSION_KEY);
    },

    /**
     * Call on any protected page.
     * Redirects to /login if not authenticated, then returns false.
     * Returns true when authenticated.
     */
    requireAuth() {
      if (!this.isLoggedIn()) {
        sessionStorage.setItem('np_login_redirect', window.location.pathname);
        window.location.replace('/login?msg=protected');
        return false;
      }
      return true;
    },

    /** Update the navbar button state (Login ↔ Logout + teacher badge). */
    updateNavbar() {
      const session   = this.getSession();
      const loginBtn  = document.getElementById('loginBtn');
      const logoutBtn = document.getElementById('logoutBtn');
      const badge     = document.getElementById('teacherBadge');
      const demoBadge = document.getElementById('demoBadge');

      const dashLinks = document.querySelectorAll('.nav-dashboard-link');

      if (session) {
        if (loginBtn)  loginBtn.style.display  = 'none';
        if (logoutBtn) logoutBtn.style.display = '';

        const inDemo = (typeof NutriDemo !== 'undefined') && NutriDemo.isDemo();
        if (badge) {
          badge.style.display = inDemo ? 'none' : '';
          if (!inDemo) badge.textContent = '👩‍🏫 Teacher';
        }
        if (demoBadge) demoBadge.style.display = inDemo ? '' : 'none';
        dashLinks.forEach(el => { el.style.display = ''; });
      } else {
        if (loginBtn)  loginBtn.style.display  = '';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (badge)     badge.style.display     = 'none';
        if (demoBadge) demoBadge.style.display = 'none';
        dashLinks.forEach(el => { el.style.display = 'none'; });
      }
    },
  };

  // Expose globally
  window.NutriAuth = NutriAuth;

  // Auto-update navbar as soon as the DOM is ready
  document.addEventListener('DOMContentLoaded', () => NutriAuth.updateNavbar());
})();
