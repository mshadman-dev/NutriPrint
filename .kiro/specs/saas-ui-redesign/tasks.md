# Implementation Plan: SaaS UI Redesign

## Overview

A frontend-only visual overhaul of NutriPrint V2 — CSS token system, Shell_Card / Badge components,
navigation upgrade, per-page layout improvements, and a property-based test suite.

**Critical constraint throughout every task:**
- Never remove or rename any JS-referenced ID or class (see design.md § JS Safety Strategy).
- Never modify `action`, `method`, `name`, or `type` attributes on any form element.
- Never touch any Python/backend file.
- `.shell-card` is always *added* alongside existing classes, never replacing them.
- `.ld-advisor-typing` CSS default is `display: none`; visibility is JS-controlled only.

---

## Tasks

- [x] 1. Create `base.css` — design tokens, Shell_Card, Badge, and global resets
  - Create `/static/css/base.css` as a new file (does not yet exist).
  - Define the `:root` block with all nine required custom properties:
    `--color-bg`, `--color-surface`, `--color-primary`, `--color-accent`,
    `--color-text`, `--color-text-muted`, `--shadow-card`, `--radius-card`, `--radius-pill`.
  - Set exact values per design.md §2.1:
    `--color-accent: #10B981`, `--color-primary: #0F172A`,
    `--color-bg: #F8FAFC`, `--color-surface: #FFFFFF`.
  - Add complete spacing scale (`--space-1` … `--space-20`) and font tokens
    (`--font-heading: 'Poppins'`, `--font-body: 'Inter'`).
  - Add semantic colour tokens (`--color-error`, `--color-warning`, `--color-success`, `--color-info`).
  - Add shadow tokens (`--shadow-card`, `--shadow-hover`, `--shadow-nav`).
  - Define `.shell-card` with exactly the four canonical properties (background, border,
    border-radius, box-shadow) using `var()` references. No page-level override allowed.
  - Define `.badge` base class and all variants:
    `.badge--green`, `.badge--blue`, `.badge--orange`, `.badge--red`,
    `.badge--accent`, `.badge--outline`.
  - Define BMI badge aliases:
    `.badge-underweight`, `.badge-normal`, `.badge-overweight`, `.badge-obese`
    (preserve existing class names — JS/templates reference them).
  - Define `.site-header` and `.site-header.scrolled` frosted-glass styles.
  - Define `.nav-link-active` using `var(--color-accent)` and `var(--color-accent-light)`.
  - Define `#mobileNav` slide-down animation (`max-height: 0` → `max-height: 400px` on `.open`).
  - Define `.hero-banner`, `.hero-grid`, `.hero-animate`, `@keyframes heroFadeUp`,
    `.hero-headline-accent` (gradient text clip), `.btn-hero-primary`, `.btn-hero-secondary`.
  - Define `.stats-grid`, `.stat-card`, `.stat-card-icon`, `.stat-card-value`, `.stat-card-label`,
    `.stat-card::after` (bottom accent bar on hover).
  - Define `.card-header-gradient`, `.advice-callout`.
  - Define `.bmi-gauge-wrap`, `.bmi-gauge-track`, `.bmi-gauge-centre`, `.bmi-gauge-value`.
  - Define `.bmi-layout-grid` responsive single-column at ≤ 767 px.
  - Define `.day-cards-grid`, `.day-card`, `.day-card-header`, `.meal-row`.
  - Define `.food-cards-grid` (2/3/4-col responsive), `.food-card` with hover lift.
  - Define `.filter-toolbar` (horizontally scrolling, no-wrap), `.filter-chip` and `.filter-chip.active`.
  - Define `.advisor-chat-grid` 1-col / 2-col responsive.
  - Define `.ld-advisor-typing { display: none; }` as default (JS controls visibility).
  - Define `.hero-impact-panel`, `.hero-stat-row`, `.hero-stat-num`, `.hero-stat-label`.
  - Add global `@media (prefers-reduced-motion: reduce)` block covering all keyframe animations
    defined in this file.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.3, 4.4,
    5.1, 5.3, 5.4, 6.1, 6.2, 7.1, 7.3, 7.4, 8.1, 8.4, 9.1, 9.2, 9.4, 10.1, 10.5,
    11.1, 12.2, 13.5_

  - [x] 1.1 Write `base.css` with all tokens, Shell_Card, Badge, and component styles
    - Create the file at the absolute path `/static/css/base.css`.
    - Implement every class listed above.
    - All brand colours in rule bodies MUST use `var(--*)` tokens — no bare hex.
    - _Requirements: 1.1–1.4, 9.1, 9.2, 9.4, 12.1–12.3_

  - [ ]* 1.2 Write property test — Property 1: All required design tokens are declared
    - **Property 1: All required design tokens are declared**
    - Parse `:root` block from `base.css` and assert all nine token names are present.
    - Use `fast-check` with `fc.constantFrom(...requiredTokenNames)`.
    - **Validates: Requirements 1.1**

  - [ ]* 1.3 Write property test — Property 2: No hard-coded brand hex values outside `:root`
    - **Property 2: No hard-coded brand hex values outside `:root`**
    - Scan all CSS rule bodies for literal `#0F172A`, `#10B981`, `#F8FAFC`, `#FFFFFF`.
    - Assert zero occurrences in rule bodies outside the `:root {}` block.
    - **Validates: Requirements 1.2, 12.1**

  - [ ]* 1.4 Write property test — Property 4: Every badge element satisfies the pill spec
    - **Property 4: Every badge element satisfies the pill spec**
    - Use `fc.constantFrom` over all badge class names; parse computed `border-radius`,
      `padding`, `font-weight` from `base.css`; assert pill constraints.
    - **Validates: Requirements 9.4**

- [x] 2. Update `base.html` — link `base.css` first, upgrade navigation
  - Open `/templates/base.html`.
  - Insert `<link rel="stylesheet" href="/static/css/base.css"/>` as the FIRST stylesheet
    entry in `<head>`, before all existing stylesheet links.
  - Add class `site-header` to the existing `<header>` element (preserve all other classes and IDs).
  - Replace the existing `<style>` block's frosted-glass rules with references to `site-header`
    defined in `base.css` (remove duplicate inline CSS, keep the class-based approach).
  - Update `toggleMobileNav()` inline function: toggle `.open` class on `#mobileNav`
    instead of toggling `hidden` (see design.md §3.1). Keep `id="mobileNav"` intact.
  - Add outside-click handler inside `toggleMobileNav()` as specified in design.md §3.1.
  - Add the scroll listener inline `<script>` for `.site-header.scrolled` at the bottom of
    `<body>` (uses `{ passive: true }`).
  - Update `.nav-link-active` CSS (now in `base.css`) — remove any duplicate definition
    from `base.html`'s inline `<style>` block to avoid conflicts.
  - Ensure desktop nav (≥ 1024 px) uses `flex-wrap: nowrap` — add `flex-nowrap` or
    equivalent Tailwind/custom class to the nav list container.
  - Verify all JS-critical IDs are preserved:
    `#mobileNav`, `#teacherBadge`, `#loginBtn`, `#logoutBtn`, `#demoModeBanner`,
    `#demoProgressText`, `#pauseDemoBtn`, `#resumeDemoBtn`.
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 15.1, 15.6_

  - [x] 2.1 Link `base.css` first and wire frosted-glass header in `base.html`
    - Add `<link>` tag as first stylesheet.
    - Add `site-header` class to `<header>`.
    - Add scroll listener script.
    - _Requirements: 2.1, 1.2_

  - [x] 2.2 Upgrade mobile nav drawer in `base.html`
    - Update `toggleMobileNav()` to use `.open` class on `#mobileNav`.
    - Add outside-click close handler.
    - Verify `#mobileNav` ID is preserved.
    - _Requirements: 2.4, 2.5, 15.1_

- [ ] 3. Redesign `index.html` — hero section, impact panel, and statistics cards
  - Open `/templates/index.html`.
  - Wrap the entire hero area in a `<section class="hero-banner">` (or add the class to
    the existing wrapper — preserve any existing IDs).
  - Add `.hero-grid` class to the two-column flex/grid container inside the hero.
  - Mark each hero child with `hero-animate` class for staggered fade-up animation.
  - Add `.hero-headline-accent` to the highlighted word/phrase inside the H1 `<span>`.
  - Replace or update the two CTA buttons: add `.btn-hero-primary` and `.btn-hero-secondary`
    classes (preserve any `href`, `id`, or `onclick` attributes).
  - Add `id="heroImpactPanel"` and class `shell-card hero-impact-panel` to the impact stats panel.
    Use `id="stat-plans"`, `id="stat-students"`, `id="stat-foods"` on the number elements
    (these IDs are already referenced by JS — preserve them exactly).
  - Add `id="statsSection"` to the statistics cards section.
  - Wrap each statistic card in `<div class="stat-card">` (or add the class to existing wrapper).
  - Ensure each stat card has `.stat-card-icon`, `.stat-card-value`, `.stat-card-label` children.
  - Add `.stats-grid` class to the grid container.
  - Add inline `<script>` (or update existing) with `animateCounter()` and
    `IntersectionObserver` logic (design.md §3.3).
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 3.1 Implement hero banner and staggered animation in `index.html`
    - Apply `.hero-banner`, `.hero-grid`, `.hero-animate` classes.
    - Add `.hero-headline-accent` span, CTA button classes, impact panel IDs.
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 3.2 Implement statistics cards and counter animation in `index.html`
    - Apply `.stats-grid`, `.stat-card` and sub-element classes.
    - Add `id="statsSection"`, `animateCounter()` JS, `IntersectionObserver` trigger.
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 3.3 Write property test — Property 8: No page produces horizontal overflow
    - **Property 8: No page produces horizontal overflow**
    - Use Playwright + fast-check to test all six page URLs at random widths ≥ 320 px.
    - Assert `scrollWidth ≤ innerWidth` on every page.
    - **Validates: Requirements 13.1**

- [ ] 4. Redesign `bmi.html` — Shell_Card form, BMI gauge, badge, advice callout
  - Open `/templates/bmi.html`.
  - Add `.shell-card` class alongside the existing form container class (do NOT remove the
    existing class — JS or style selectors may reference it).
  - Add `.card-header-gradient` div inside the shell card, above the form fields.
  - Add `.bmi-gauge-wrap`, `.bmi-gauge-track`, `.bmi-gauge-centre`, `.bmi-gauge-value`
    to the BMI result area. The JS in `bmi.js` writes the BMI value to a DOM element —
    ensure that element's ID/class is preserved.
  - Add `.advice-callout` class to the advice text container.
  - Ensure `.badge-underweight`, `.badge-normal`, `.badge-overweight`, `.badge-obese`
    classes are applied to the classification badge elements (these already exist — confirm
    they remain).
  - Add `.bmi-layout-grid` class to the two-column layout wrapper (form + results).
  - Wrap any error message display area with `.es-toast--error` pattern (not removing
    existing error element IDs).
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ] 4.1 Apply Shell_Card, gauge, badge, and callout classes in `bmi.html`
    - Add all required classes listed above.
    - Confirm no form `action`/`method`/`name`/`type` attributes are modified.
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 4.2 Write property test — Property 3: Shell_Card canonical properties are consistent
    - **Property 3: Shell_Card canonical properties are consistent**
    - Use `fc.constantFrom` over all pages; parse `.shell-card` computed styles from each;
      assert background, border-radius, and box-shadow are identical.
    - **Validates: Requirements 9.1, 9.2**

- [ ] 5. Checkpoint — Base foundation verified
  - Ensure `base.css` loads without errors (check browser console for custom property failures).
  - Confirm `.shell-card` looks consistent on `/bmi` and `/` pages.
  - Confirm frosted-glass header appears on scroll.
  - Confirm mobile nav drawer opens/closes with `.open` toggle and outside-click dismissal.
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Redesign `meal_planner.html` — day-cards, macro chips, weekly summary, loading state
  - Open `/templates/meal_planner.html`.
  - Add `.shell-card` alongside the existing meal planner form container class.
  - Add `.card-header-gradient` header inside the form shell card.
  - Add `.day-cards-grid` class to the results grid wrapper.
  - Add `.day-card` class to each day result card element (alongside existing classes).
  - Add `.day-card-header` to each day card's header row.
  - Add `.meal-row` to each breakfast/lunch/dinner row inside a day card.
  - Ensure macro chip elements use `.macro-chip` with `.macro-cal`, `.macro-pro`,
    `.macro-carb`, `.macro-fat` sub-classes (these are already in `poster.css` — confirm
    they are applied in the template).
  - Add `.shell-card` class alongside `.wns-panel` on the weekly summary panel wrapper.
  - Ensure the loading state area uses `.ld-meal-card` class (design.md §3.8).
  - Preserve all JS-critical IDs: `#mealStudent`, `#mealAge`, `#mealGender`, `#mealHeight`,
    `#mealWeight`, `#mealActivity`, `#mealHealthNotes`, `#mealDiet`, `#mealRegion`,
    `#mealMonth`, `#mealStrategy`.
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ] 6.1 Apply day-card grid and Shell_Card classes in `meal_planner.html`
    - Add `.shell-card`, `.card-header-gradient`, `.day-cards-grid`, `.day-card`, `.day-card-header`,
      `.meal-row` classes to appropriate elements.
    - Confirm all JS form field IDs are intact.
    - _Requirements: 6.1, 6.2, 6.4, 6.6_

  - [ ] 6.2 Wire weekly summary Shell_Card and loading state in `meal_planner.html`
    - Add `.shell-card` to `.wns-panel` container.
    - Confirm `.ld-meal-card` is applied to the loading skeleton container.
    - _Requirements: 6.3, 6.5_

  - [ ]* 6.3 Write property test — Property 9: All multi-column grids collapse at ≤ 480 px
    - **Property 9: All multi-column grids collapse at ≤ 480 px**
    - Use fast-check to sample CSS grid containers; parse `grid-template-columns` at the
      ≤ 480 px media query; assert ≤ 2 columns.
    - **Validates: Requirements 13.3, 4.1, 7.1**

- [ ] 7. Redesign `food_catalog.html` — food card grid, filter toolbar, empty state
  - Open `/templates/food_catalog.html`.
  - Add `.food-cards-grid` class to the card grid container.
  - Add `.food-card` class alongside existing food card wrapper classes.
  - Ensure each food card has a food image (or emoji fallback), food name, category badge
    using `.badge`, diet-type badge using `.badge`, and nutrition stat elements.
  - Add `.filter-toolbar` class to the filter/search row container.
  - Add `.filter-chip` class to each filter button; add `.active` class to the active one.
  - Replace or confirm that the no-results empty state uses `.es-no-results` class
    (already defined in `empty_states.css`).
  - Verify `.filter-toolbar` has `overflow-x: auto; flex-wrap: nowrap` — from `base.css`.
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ] 7.1 Apply food card grid and filter toolbar classes in `food_catalog.html`
    - Add `.food-cards-grid`, `.food-card`, `.filter-toolbar`, `.filter-chip`,
      `.badge` classes to their respective elements.
    - Confirm `.es-no-results` empty state is in place.
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 7.2 Write property test — Property 5: Card section headers use only palette-derived gradients
    - **Property 5: Card section headers use only palette-derived gradients**
    - Parse all `background: linear-gradient(...)` declarations from CSS files;
      use fast-check to iterate over gradient stop colours; assert they derive from
      `#0F172A`, `#10B981`, `#F8FAFC`, `#FFFFFF`, or `var(--color-*)` tokens.
    - **Validates: Requirements 9.3, 12.1**

- [ ] 8. Redesign the AI Advisor section in `meal_planner.html`
  - The advisor UI is rendered into `#advisorPanel` by `advisor.js` — do NOT restructure
    `#advisorPanel` itself or any of its JS-critical IDs/classes.
  - In `advisor.css`: update `.advisor-shell` to remove its four canonical card properties
    (background, border, border-radius, box-shadow) — these will come from `.shell-card`
    added in the JS render template.
  - In `advisor.js`'s render template string: add `shell-card` to the existing
    `advisor-shell` class list (e.g., `class="advisor-shell shell-card"`).
    Preserve `advisor-shell` and all other classes and IDs.
  - Update `.advisor-chip` in `advisor.css` to use token references:
    `border-radius: var(--radius-pill)`, `border: 1.5px solid var(--color-accent)`.
  - Ensure `.ld-advisor-typing` default is `display: none` in `base.css` (already in
    Task 1.1). No static HTML instance of `.ld-advisor-typing` should exist in the template.
  - Update `.advisor-chat-grid` media query to achieve side-by-side at ≥ 1024 px.
  - Preserve all JS-critical IDs: `#advisorPanel`, `#advisorMessages`, `#advisorBody`,
    `#advisorToggleBtn`, `#advisorForm`, `#advisorQuestion`, `#advisorSend`,
    `#advisorRecommendations`, `#advisorLanguage`.
  - Preserve all JS-critical classes: `.advisor-message`, `.advisor-msg-content`,
    `.advisor-check`, `.advisor-rec-card`, `.advisor-chip`, `.ld-advisor-typing`,
    `.ld-dot`, `.ld-dot-row`.
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 8.1 Update `advisor.css` and `advisor.js` for Shell_Card integration
    - Remove redundant card properties from `.advisor-shell` (delegate to `.shell-card`).
    - Add `shell-card` class in the `advisor.js` render template string.
    - Update `.advisor-chip` tokens and `.advisor-chat-grid` breakpoint.
    - _Requirements: 8.1, 8.4, 8.5_

  - [ ]* 8.2 Write property test — Property 11: Typing indicator is hidden except during AI request
    - **Property 11: Typing indicator is hidden except during AI request**
    - Mock `advisor.js` state machine with fast-check; assert `.ld-advisor-typing`
      has `display: none` when `state.loading === false` and is visible when `true`.
    - **Validates: Requirements 8.3, 14.1**

  - [ ]* 8.3 Write property test — Property 13: All JS-referenced DOM IDs and classes are preserved
    - **Property 13: All JS-referenced DOM IDs and classes are preserved**
    - Read all `/static/js/*.js` files; extract referenced IDs and class selectors;
      use fast-check to iterate over them; assert each is findable in the redesigned templates.
    - **Validates: Requirements 15.1, 15.6**

- [ ] 9. Checkpoint — Per-page redesign complete
  - Confirm each page renders Shell_Cards consistently.
  - Confirm advisor side-by-side layout at ≥ 1024 px.
  - Confirm food catalog filter toolbar scrolls horizontally on mobile.
  - Confirm day-cards stack to single column at ≤ 767 px.
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Update existing CSS files — replace hard-coded hex values with token references
  - For each file: `loading.css`, `empty_states.css`, `nutrition_score.css`,
    `poster.css`, `progress_tracker.css`, `qr_system.css`, `recipe.css`,
    `weekly_summary.css`, `advisor.css`:
    - Replace bare `#1D9E75` usages with `var(--color-accent)` where it represents the
      interactive green (NB: the existing files use `#1D9E75` not `#10B981` — the new
      canonical token is `#10B981`; replace all interactive-green hex values with the token).
    - Replace `#0F5E46`, `#0F172A` usages in rule bodies (not `:root`) with
      `var(--color-primary)` or a token-derived tint.
    - Replace `#F8FAFC` / `#FFFFFF` surface usages with `var(--color-bg)` /
      `var(--color-surface)` where semantically appropriate.
    - Replace shadow values with `var(--shadow-card)` / `var(--shadow-hover)`.
    - Replace `border-radius: 1.5rem` card values with `var(--radius-card)`.
    - Replace `border-radius: 9999px` pill values with `var(--radius-pill)`.
    - Keep all prefixed class names (`.ld-*`, `.es-*`, `.wns-*`, etc.) intact — do NOT
      rename any class.
    - Ensure each file has or extends the existing `@media (prefers-reduced-motion: reduce)`
      block to cover any new animation declarations.
  - _Requirements: 1.2, 9.3, 12.1, 12.2, 13.5_

  - [ ] 10.1 Token-update `loading.css` and `empty_states.css`
    - Replace hard-coded hex values with `var(--*)` tokens.
    - Preserve all class names and `@keyframes` names.
    - _Requirements: 1.2, 12.1, 13.5_

  - [ ] 10.2 Token-update `advisor.css`, `nutrition_score.css`, `weekly_summary.css`
    - Replace hard-coded hex values with `var(--*)` tokens.
    - Preserve all class names.
    - _Requirements: 1.2, 12.1_

  - [ ] 10.3 Token-update `poster.css`, `progress_tracker.css`, `qr_system.css`, `recipe.css`
    - Replace hard-coded hex values with `var(--*)` tokens.
    - Preserve all class names.
    - _Requirements: 1.2, 12.1_

  - [ ]* 10.4 Write property test — Property 6: All heading elements use Poppins
    - **Property 6: All heading elements use Poppins with correct weight and letter-spacing**
    - Use fast-check with `fc.constantFrom` over heading selectors from all CSS files;
      assert `font-family` resolves to Poppins, weight 700–900, and letter-spacing `−0.03em`
      when `font-size ≥ 1.8rem`.
    - **Validates: Requirements 10.1, 10.5**

  - [ ]* 10.5 Write property test — Property 10: Every animated element has a reduced-motion override
    - **Property 10: Every animated element has a reduced-motion override**
    - Parse all `animation-name` and `transition` declarations from `/static/css/`;
      assert each has a corresponding `@media (prefers-reduced-motion: reduce)` override.
    - **Validates: Requirements 13.5**

- [ ] 11. System-wide responsiveness and spacing audit
  - Audit every CSS `margin`, `padding`, and `gap` declaration in `base.css` and all
    updated files — replace any value that is not a multiple of `0.25rem` with the nearest
    compliant value.
  - Ensure `<main>` or the primary content wrapper has `max-width: 1280px` and
    `padding: 0 1rem` (mobile) / `padding: 0 2rem` (≥ 768 px).
  - Ensure all multi-column grids have `gap: 1.25rem` on desktop and `gap: 0.75rem`
    on mobile (add responsive gap overrides where missing).
  - Verify that all form inputs and buttons in `bmi.html` and `meal_planner.html` have
    `min-height: 44px` on mobile (use `@media (max-width: 480px)` block).
  - Set `font-size: 0.8rem` minimum and `font-size: 1.4rem` minimum heading size in the
    `@media (max-width: 480px)` block in `base.css`.
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.1, 13.4, 13.6_

  - [ ] 11.1 Audit and fix spacing values to 0.25rem grid in `base.css`
    - Replace any non-grid-compliant values; add responsive gap rules.
    - _Requirements: 11.1, 11.5_

  - [ ] 11.2 Add `max-width` container, responsive padding, and mobile font-size guards
    - Add `max-width: 1280px` to main wrapper; set mobile padding; set minimum font sizes.
    - _Requirements: 11.2, 13.6_

  - [ ] 11.3 Add `min-height: 44px` tap-target rules for mobile form inputs and buttons
    - Add `@media (max-width: 480px)` block in `base.css` for all form inputs and buttons.
    - _Requirements: 13.4_

  - [ ]* 11.4 Write property test — Property 14: Spacing values are multiples of 0.25 rem
    - **Property 14: Spacing values are multiples of 0.25 rem**
    - Parse all `margin`, `padding`, `gap` values from every CSS file;
      use fast-check to iterate; assert each numeric value mod 0.25rem === 0.
    - **Validates: Requirements 11.1**

  - [ ]* 11.5 Write property test — Property 15: Shell_Card inner padding complies with breakpoints
    - **Property 15: Shell_Card inner padding complies with breakpoint rules**
    - Parse `.shell-card` padding at mobile (≤ 639 px) and desktop (≥ 768 px) media queries;
      assert `1.25rem` and `1.75rem–2rem` respectively.
    - **Validates: Requirements 11.4**

- [ ] 12. Typography system — enforce Poppins headings, Inter body, contrast
  - In `base.css` global reset section:
    - Set `h1, h2, h3, h4, .heading, .section-title { font-family: var(--font-heading); font-weight: 700; }`.
    - Set `body, p, span, label, li, .body-text { font-family: var(--font-body); }`.
    - Set `letter-spacing: -0.03em` on all headings with `font-size ≥ 1.8rem`.
    - Ensure body text colour is `var(--color-text)` with contrast ratio ≥ 4.5:1 against
      `var(--color-bg)` (verify `#0F172A` on `#F8FAFC` — passes at ≈ 18:1).
  - In each template, confirm `<h1>`–`<h4>` tags are used for semantic headings (not `<div>`
    with font-weight only) so the global font rules apply automatically.
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ] 12.1 Add global Poppins/Inter reset and letter-spacing rules to `base.css`
    - Implement heading and body font rules as specified.
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [ ]* 12.2 Write property test — Property 7: All body text uses Inter with accessible contrast
    - **Property 7: All body text uses Inter with accessible contrast**
    - Parse body text colour and background from CSS; use fast-check to iterate over
      page/element combinations; assert contrast ratio ≥ 4.5:1 using WCAG formula.
    - **Validates: Requirements 10.2, 10.6, 2.6**

- [ ] 13. Loading/empty states — token update, Shell_Card integration, error toast
  - Confirm `.ld-meal-card` and `.ld-bmi-card` containers have `.shell-card` added
    in their respective template usages (or in JS render functions that emit their HTML).
  - Confirm `.es-toast--error` and `.es-card--error` components are used for API failures
    in `bmi.html` and `meal_planner.html` — add the pattern where missing.
  - Confirm `esFadeIn` and `ldFadeIn` keyframe animations are applied to empty/loading
    state cards (already defined — just verify the classes are on the right elements).
  - Ensure the `ld-meal-card` contains a `.ld-steps` list with at least 3 `.ld-step` children
    (design.md Testing Strategy unit test 14.2).
  - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [ ] 13.1 Confirm Shell_Card classes on loading/empty state containers in templates
    - Add `.shell-card` alongside `.ld-meal-card`, `.ld-bmi-card` in templates.
    - Confirm `.es-toast--error` is used for API failures.
    - _Requirements: 14.1, 14.3, 14.4, 14.5_

- [ ] 14. Colour consistency audit — remove orange primary interactive uses
  - Search all CSS files for `#F97316` (saffron orange) used on primary interactive elements
    (buttons, active states, progress fills, focus rings).
  - Replace any orange primary interactive colour with `var(--color-accent)` (`#10B981`).
  - Orange is only permitted for supplementary chip labels (`.macro-cal` etc.) and
    illustrative emojis.
  - Verify `#advisorSend` button (currently `background: #F97316` in `advisor.css`) is
    updated to `var(--color-accent)`.
  - _Requirements: 12.2, 12.3_

  - [ ] 14.1 Replace orange primary interactive colours with accent green in `advisor.css` and all CSS files
    - Update `.advisor-send` background to `var(--color-accent)`.
    - Audit all other files for `#F97316` in interactive contexts.
    - _Requirements: 12.2, 12.3_

  - [ ]* 14.2 Write property test — Property 12: All interactive elements use accent green
    - **Property 12: All interactive elements use accent green**
    - Parse all button, active-state, progress-bar, and focus-ring selectors from CSS files;
      assert their interactive colour resolves to `var(--color-accent)` / `#10B981`,
      not `#F97316`.
    - **Validates: Requirements 12.2, 12.3**

- [x] 15. Set up the property-based test infrastructure
  - Create directory `tests/css_properties/` (relative to project root).
  - Initialise a minimal `package.json` in `tests/` with `fast-check`, `jest`, and
    `ts-jest` (or plain JS with jest) as dev dependencies.
  - Create `tests/css_properties/utils/css-parser.ts` (or `.js`) with helper functions:
    `parseCSSClass(file, selector)` → returns a `{ property: value }` map,
    `getAnimatedSelectors(dir)` → returns array of selectors with `animation` or `transition`,
    `getReducedMotionOverrides(dir)` → returns Set of selectors overridden in
    `@media (prefers-reduced-motion: reduce)`.
  - Create `tests/css_properties/utils/dom-snapshot.ts` with helpers to create mock
    DOM snapshots containing configurable numbers of `.shell-card`, `.badge`, heading,
    and grid elements for DOM-based property tests.
  - The test utility files are pure CSS/DOM text parsing — no real browser required.
  - _Requirements: (testing infrastructure — underpins all property tests)_

  - [x] 15.1 Set up `tests/css_properties/` directory with `fast-check` and parser utilities
    - Create `tests/package.json`, `tests/css_properties/utils/css-parser.js`,
      `tests/css_properties/utils/dom-snapshot.js`.
    - _Requirements: (underpins properties 1–15)_

- [ ] 16. Write and run all property-based tests
  - Create `tests/css_properties/design-tokens.test.js` — Properties 1, 2.
  - Create `tests/css_properties/shell-card-badge.test.js` — Properties 3, 4.
  - Create `tests/css_properties/gradients.test.js` — Property 5.
  - Create `tests/css_properties/typography.test.js` — Properties 6, 7.
  - Create `tests/css_properties/responsive.test.js` — Properties 8, 9.
  - Create `tests/css_properties/reduced-motion.test.js` — Property 10.
  - Create `tests/css_properties/typing-indicator.test.js` — Property 11.
  - Create `tests/css_properties/interactive-colours.test.js` — Property 12.
  - Create `tests/css_properties/js-safety.test.js` — Property 13.
  - Create `tests/css_properties/spacing.test.js` — Properties 14, 15.
  - Each test file includes the tag comment:
    `// Feature: saas-ui-redesign, Property N: <property_text>`.
  - _Requirements: All (via test coverage)_

  - [ ] 16.1 Write property tests for token system (Properties 1 & 2)
    - Implement `design-tokens.test.js`.
    - Minimum 100 iterations per `fc.assert`.
    - _Requirements: 1.1, 1.2_

  - [ ]* 16.2 Write property tests for Shell_Card and Badge (Properties 3 & 4)
    - **Property 3: Shell_Card canonical properties are consistent**
    - **Property 4: Every badge element satisfies the pill spec**
    - Implement `shell-card-badge.test.js`.
    - **Validates: Requirements 9.1, 9.2, 9.4**

  - [ ]* 16.3 Write remaining property tests (Properties 5–15)
    - Implement all remaining test files listed above.
    - **Validates: All remaining correctness properties**

- [ ] 17. Final checkpoint — full test suite and JS regression check
  - Run `cd tests && npm test` (or `npx jest --runInBand`) — assert all property tests pass.
  - Run `grep -r 'getElementById\|querySelector\|getElementsByClassName\|querySelectorAll' static/js/` and verify each referenced id/class still exists in the redesigned templates.
  - Open each of the six pages in a browser and check DevTools Console for:
    - Zero CSS custom property resolution failures (empty computed values).
    - Zero JS runtime errors.
  - Submit the BMI form, meal planner form, and AI advisor form — verify correct API responses.
  - Resize browser to 320 px wide and confirm no horizontal scrollbar on any page.
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP; the property tests in Task 16 consolidate all the individual `*` sub-tasks above.
- The key sequencing constraint is: **base.css before any template**; **templates before token-update of existing CSS files** (so you can verify tokens resolve).
- All implementation is CSS + HTML class additions only — zero Python changes.
- During implementation, always prefer adding a class alongside existing classes over replacing them (JS Safety Rule).
- The `#F97316` orange on `.advisor-send` must be changed (Task 14.1) — it is the most obvious colour-consistency violation in the existing code.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "15.1"] },
    { "id": 1, "tasks": ["2.1", "2.2", "1.2", "1.3", "1.4"] },
    { "id": 2, "tasks": ["3.1", "3.2", "4.1", "6.1", "6.2", "7.1", "8.1", "12.1"] },
    { "id": 3, "tasks": ["3.3", "4.2", "6.3", "7.2", "8.2", "8.3", "10.1", "10.2", "10.3", "11.1", "11.2", "11.3", "13.1", "14.1"] },
    { "id": 4, "tasks": ["10.4", "10.5", "11.4", "11.5", "12.2", "14.2", "16.1"] },
    { "id": 5, "tasks": ["16.2", "16.3"] }
  ]
}
```
