/**
 * NutriPrint — Auth helpers
 * ─────────────────────────────────────────────────────────────────────────────
<<<<<<< HEAD
 * Session is written into localStorage (np_teacher_session) on login and
 * cleared by NutriAuth.logout().  The real Supabase OTP backend
 * (routers/auth.py) is not yet connected to the frontend; this file handles
 * client-side session state.
=======
 * Session state is shared by the Supabase-backed auth flow and the pilot
 * workspace used for report screenshots and expo review.
>>>>>>> 0c5200c (Remove demo mode and implement guest access workflow)
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

<<<<<<< HEAD
    /** Update the navbar button state (Login ↔ Logout + teacher badge). */
=======
    /** Update the navbar button state. */
>>>>>>> 0c5200c (Remove demo mode and implement guest access workflow)
    updateNavbar() {
      const session   = this.getSession();
      const loginBtn  = document.getElementById('loginBtn');
      const logoutBtn = document.getElementById('logoutBtn');
      const badge     = document.getElementById('teacherBadge');
<<<<<<< HEAD

=======
>>>>>>> 0c5200c (Remove demo mode and implement guest access workflow)
      const dashLinks = document.querySelectorAll('.nav-dashboard-link');

      if (session) {
        if (loginBtn)  loginBtn.style.display  = 'none';
        if (logoutBtn) logoutBtn.style.display = '';

<<<<<<< HEAD
        if (badge) {
          badge.style.display = '';
          badge.textContent = '👩‍🏫 Teacher';
=======
        const inPilot = (typeof NutriPilot !== 'undefined') && NutriPilot.isActive();
        if (badge) {
          badge.style.display = '';
          badge.textContent = inPilot ? 'Pilot Workspace' : 'Teacher';
>>>>>>> 0c5200c (Remove demo mode and implement guest access workflow)
        }
        dashLinks.forEach(el => { el.style.display = ''; });
      } else {
        if (loginBtn)  loginBtn.style.display  = '';
        if (logoutBtn) logoutBtn.style.display = 'none';
        if (badge)     badge.style.display     = 'none';
        dashLinks.forEach(el => { el.style.display = 'none'; });
      }
    },
  };

  // Expose globally
  window.NutriAuth = NutriAuth;

  // Auto-update navbar as soon as the DOM is ready
  document.addEventListener('DOMContentLoaded', () => NutriAuth.updateNavbar());
})();
