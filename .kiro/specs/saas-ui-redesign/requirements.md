# Requirements Document

## Introduction

NutriPrint V2 is a FastAPI + Jinja2 web application that helps teachers in Karnataka schools assess student BMI, generate AI-powered meal plans, and produce shareable nutrition posters. While the product's functionality is complete, the visual design needs a professional overhaul to qualify as a startup-grade product — suitable for VTU Project Report screenshots, LinkedIn portfolio showcase, GitHub demos, and live presentations.

This feature redesigns the frontend-only layer: CSS files in `/static/css/`, page-specific `<style>` blocks inside Jinja2 templates, and HTML structural improvements (class additions, layout refactoring) that preserve all existing functionality, routes, and backend logic. No database schema, Python code, or API contracts are changed.

The target aesthetic is a **modern, clean SaaS dashboard** with:
- Primary: `#0F172A` (dark navy)
- Accent: `#10B981` (emerald green)
- Background: `#F8FAFC` (light gray-white)
- Cards: `#FFFFFF`
- Typography: Poppins (headings) + Inter (body)

---

## Glossary

- **UI_System**: The complete set of CSS files and template style blocks that control visual presentation.
- **Design_Token**: A named CSS custom property (e.g., `--color-accent`) used consistently across all stylesheets.
- **Shell_Card**: The primary card container pattern used for page sections — `background: #FFFFFF`, `border-radius: 1.5rem`, subtle border and shadow.
- **Hero_Section**: The full-width banner at the top of the homepage (`index.html`).
- **Stat_Card**: A metric display tile showing a large number, icon, and label — used on the homepage and dashboard.
- **Page**: Any of the six HTML template pages: Homepage (`index.html`), BMI (`bmi.html`), Meal Planner (`meal_planner.html`), Food Catalog (`food_catalog.html`), AI Advisor (section within `meal_planner.html`), Dashboard (`dashboard.html`).
- **Responsive_Layout**: A layout that correctly adapts across mobile (≤ 480 px), tablet (481–1023 px), and desktop (≥ 1024 px) breakpoints without horizontal scroll or content overflow.
- **Color_Palette**: The four canonical brand colours — `#0F172A`, `#10B981`, `#F8FAFC`, `#FFFFFF`.
- **Accent_Green**: `#10B981` — the single interactive/highlight colour used for buttons, badges, progress bars, and active states.
- **Navigation**: The sticky `<header>` and mobile nav drawer defined in `base.html`.
- **Accessibility_Contrast**: A foreground/background colour pair that meets WCAG 2.1 AA minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text.

---

## Requirements

### Requirement 1: Design Token System

**User Story:** As a developer maintaining the redesigned UI, I want all colours, shadows, border-radii, and spacing values to be defined as CSS custom properties, so that future brand changes require editing one place instead of dozens of files.

#### Acceptance Criteria

1. THE UI_System SHALL define a root CSS custom property block containing at minimum: `--color-bg`, `--color-surface`, `--color-primary`, `--color-accent`, `--color-text`, `--color-text-muted`, `--shadow-card`, `--radius-card`, `--radius-pill`.
2. WHEN any CSS rule uses a brand colour, shadow, or radius, THE UI_System SHALL reference the corresponding Design_Token rather than hard-coding the hex value. CSS rules MAY reference a design token even if the root `:root` block defining it appears later in the same stylesheet.
3. THE UI_System SHALL set `--color-accent` to `#10B981` and `--color-primary` to `#0F172A`.
4. THE UI_System SHALL set `--color-bg` to `#F8FAFC` and `--color-surface` to `#FFFFFF`.

---

### Requirement 2: Navigation Upgrade

**User Story:** As a visitor viewing NutriPrint, I want the top navigation bar to look polished and professional, so that the first impression matches a funded startup product.

#### Acceptance Criteria

1. THE Navigation SHALL display a frosted-glass effect — `background: rgba(255,255,255,0.92)`, `backdrop-filter: blur(20px)` — on all pages when the user is at scroll position > 0.
2. THE Navigation SHALL render the NutriPrint logotype and nav links in a single horizontal row on viewports ≥ 1024 px without wrapping.
3. WHEN a nav link corresponds to the current page, THE Navigation SHALL apply an active indicator using `--color-accent` (either a bottom border, background tint, or pill highlight) that is visually distinct from inactive links.
4. THE Navigation SHALL include a mobile hamburger menu that opens a full-width slide-down drawer on all viewports < 1024 px, including very narrow viewports.
5. IF the hamburger drawer is open and the user taps outside it, THEN THE Navigation SHALL close the drawer on any viewport width where the hamburger menu is shown.
6. THE Navigation SHALL maintain sufficient Accessibility_Contrast between link text and its background in both default and active states.

---

### Requirement 3: Homepage Hero Section

**User Story:** As a recruiter or evaluator opening NutriPrint for the first time, I want to see an impressive hero section that communicates the product's value immediately, so that I understand it is a professional SaaS product rather than a student project.

#### Acceptance Criteria

1. THE Hero_Section SHALL use a full-width gradient banner (`#0F172A` to `#10B981`) with a minimum height of `420 px` on desktop.
2. THE Hero_Section SHALL render a headline (≥ 2.4 rem on desktop) with an accent-coloured highlighted word or phrase using a CSS gradient text clip.
3. THE Hero_Section SHALL display at least two CTA buttons — a primary (white fill, dark text) and a secondary (accent fill, white text) — using `border-radius: 9999px` pill shape.
4. THE Hero_Section SHALL include a live-impact card panel (right column on desktop, below copy on mobile) showing platform statistics fetched from `/api/impact`.
5. WHEN the page loads, THE Hero_Section SHALL animate each element into view using a staggered fade-up sequence with a maximum total duration of 600 ms.
6. THE Hero_Section SHALL be fully Responsive_Layout compliant — stacking to a single column on viewports ≤ 1023 px.

---

### Requirement 4: Statistics Cards

**User Story:** As a teacher or evaluator viewing the homepage stats section, I want the metric cards to communicate impact data at a glance with a professional, data-rich appearance, so that the platform feels credible and polished.

#### Acceptance Criteria

1. THE UI_System SHALL render Stat_Cards in a 4-column grid on desktop (≥ 640 px), collapsing to 2-column on mobile.
2. EACH Stat_Card SHALL display: an icon, a large numeric value (≥ 1.8 rem), and a label — in a vertically stacked layout.
3. WHEN a user hovers over a Stat_Card, THE Stat_Card SHALL animate upward by 4 px and reveal a bottom accent bar in `--color-accent`.
4. THE Stat_Card SHALL maintain `background: #FFFFFF`, `border-radius: 1.5rem`, and a subtle `box-shadow` matching `--shadow-card`.
5. THE UI_System SHALL animate the numeric values of Stat_Cards from `0` to their final values using a JS counter animation triggered when the section enters the viewport.

---

### Requirement 5: BMI Assessment Page

**User Story:** As a teacher using the BMI assessment tool, I want the form and results to look clean and trustworthy, so that the tool feels like professional healthcare software.

#### Acceptance Criteria

1. THE BMI assessment form SHALL be rendered inside a Shell_Card with `padding: 2rem` and a section header using a gradient accent strip.
2. WHEN the BMI result is displayed, THE UI_System SHALL show the BMI value inside a large circular gauge or donut indicator with colour-coded zones (underweight, normal, overweight, obese).
3. THE BMI result card SHALL display the classification badge (`badge-underweight`, `badge-normal`, `badge-overweight`, `badge-obese`) with consistent background and text colours using the Color_Palette.
4. THE UI_System SHALL render the advice text in a distinct callout box using a left accent border in `--color-accent`.
5. IF the form submission fails or an API error occurs, THEN THE UI_System SHALL display an inline error message inside a styled `es-toast--error` component without a full-page reload. Successful form submissions MAY result in a full-page reload.
6. THE BMI page SHALL be Responsive_Layout compliant — form and results stacking to a single column on viewports ≤ 767 px.

---

### Requirement 6: Meal Planner Page

**User Story:** As a teacher generating a 7-day meal plan, I want the meal planner to feel like a premium product with clear visual hierarchy, so that the output is presentable in reports and demonstrations.

#### Acceptance Criteria

1. THE Meal Planner input form SHALL be contained in a Shell_Card with a header gradient matching the Color_Palette.
2. THE UI_System SHALL render each day's meal plan as a day-card with a coloured day header (using `--color-accent` or a tint), and three sub-rows for breakfast, lunch, and dinner.
3. WHEN the AI is generating a meal plan, THE UI_System SHALL display the `ld-meal-card` loading skeleton with animated step indicators, replacing the results area.
4. EACH meal item in a day-card SHALL display the meal name, calorie estimate, and a macro chip row (calories, protein, carbs, fat) using colour-coded pill badges.
5. THE Meal Planner results section SHALL include a weekly nutrition summary panel (`wns-panel`) showing aggregate calorie, protein, calcium, and iron averages against ICMR RDA targets.
6. THE Meal Planner page SHALL be Responsive_Layout compliant — day-cards stacking to a single column on viewports ≤ 767 px.

---

### Requirement 7: Food Catalog Page

**User Story:** As a teacher browsing the food catalog, I want to see food cards that are visually rich and clearly organised, so that the catalog feels like a professional nutrition database product.

#### Acceptance Criteria

1. THE Food Catalog SHALL render food items as cards in a responsive grid: 4 columns on desktop (≥ 1280 px), 3 columns on tablet (640–1279 px), 2 columns on mobile.
2. EACH food card SHALL display: a food image (or emoji fallback), food name, category badge, diet-type badge, and key nutrition stats (calories, protein).
3. WHEN a user hovers over a food card, THE food card SHALL animate upward by 3 px and increase box-shadow depth.
4. THE Food Catalog SHALL include a filter/search toolbar with pill-shaped filter buttons for diet type, category, and meal type — using `--color-accent` for the active filter state.
5. WHEN no food items match the active filters, THE UI_System SHALL display the `es-no-results` empty state component.
6. THE food catalog filter toolbar SHALL be Responsive_Layout compliant — scrolling horizontally as a single row on mobile rather than wrapping into multiple rows.

---

### Requirement 8: AI Nutrition Advisor UI

**User Story:** As a teacher using the AI Nutrition Advisor, I want the chat interface to look like a modern AI product UI, so that the tool feels sophisticated in a demo or presentation context.

#### Acceptance Criteria

1. THE AI Advisor chat panel SHALL be rendered inside a Shell_Card with an `advisor-header` gradient top bar in the Color_Palette.
2. THE UI_System SHALL visually differentiate user messages (right-aligned, `--color-accent` background, white text) from assistant messages (left-aligned, white background, dark text, subtle border).
3. WHEN the AI is processing a response, THE UI_System SHALL display the `ld-advisor-typing` indicator with three animated bouncing dots. The typing indicator visibility SHALL be controlled exclusively by the JavaScript that manages the AI request lifecycle — it SHALL be shown only after the fetch/XHR to the AI endpoint is initiated and SHALL be hidden only after a response is received or the request errors. The typing indicator SHALL NOT be visible at page load, between conversations, or at any time when no AI request is in flight.
4. THE advisor quick-select chips SHALL use `border-radius: 9999px`, a light green background (`#F0FDF4`), and `--color-accent` border.
5. THE AI Advisor panel and the recommendations panel SHALL display side-by-side on viewports ≥ 1024 px (inclusive) and stack vertically on viewports < 1024 px.
6. WHEN an advisor recommendation card is displayed, THE recommendation card SHALL include a title, action summary, and body text in a Shell_Card layout.

---

### Requirement 9: Card Layouts and Component Consistency

**User Story:** As a developer reviewing the codebase, I want all card components to follow a single consistent visual language, so that the product looks cohesive rather than assembled from mismatched parts.

#### Acceptance Criteria

1. THE UI_System SHALL implement Shell_Card as a single, centrally defined CSS class named `.shell-card` with the canonical properties: `background: var(--color-surface)`, `border: 1px solid rgba(148,163,184,0.18)`, `border-radius: var(--radius-card)`, `box-shadow: var(--shadow-card)`. ALL primary card containers across every Page SHALL apply the `.shell-card` class — no equivalent container element may define these properties through one-off inline styles or page-specific overrides.
2. THE UI_System SHALL NOT define conflicting card styles that produce different border-radii or shadow depths for equivalent-level container elements on the same page. Any page-level `<style>` block that modifies `border-radius` or `box-shadow` on a `.shell-card` element is a violation of this criterion.
3. WHEN a card contains a prominent section header (e.g., advisor header, poster header), THE header SHALL use the canonical gradient: `linear-gradient(135deg, #0F172A 0%, #10B981 100%)` or a close variant using only Color_Palette values.
4. THE UI_System SHALL define a single centrally-named badge/pill component pattern — `border-radius: 9999px`, padded, font-weight ≥ 600 — and ALL badge or pill elements across pages SHALL use this centralised component rather than one-off inline styles.

---

### Requirement 10: Typography Hierarchy

**User Story:** As a visitor reading NutriPrint's content, I want clear typographic hierarchy, so that headings, body copy, labels, and supporting text are instantly distinguishable.

#### Acceptance Criteria

1. THE UI_System SHALL use Poppins (font-weight 700–900) exclusively for all headings (`h1`–`h4` and equivalent `.heading` class elements).
2. THE UI_System SHALL use Inter (font-weight 400–600) for all body copy, labels, and helper text.
3. THE UI_System SHALL NOT mix more than two typefaces on any single page.
4. EACH page SHALL maintain a minimum of three distinct font-size levels: heading (≥ 1.8 rem on desktop), subheading (1.0–1.4 rem), and body (0.85–1.0 rem).
5. THE UI_System SHALL set `letter-spacing: -0.03em` on all headings with `font-size ≥ 1.8 rem` to achieve a tight, professional SaaS appearance.
6. THE UI_System SHALL ensure all body text colours meet Accessibility_Contrast requirements against their background.

---

### Requirement 11: Spacing and Layout Consistency

**User Story:** As a developer or evaluator reviewing the product's layout, I want consistent spacing between elements, so that the product looks intentionally designed rather than hastily assembled.

#### Acceptance Criteria

1. THE UI_System SHALL use multiples of `0.25 rem` (4 px base grid) for all margin, padding, and gap values.
2. THE UI_System SHALL wrap all page content inside a centred container with `max-width: 1280 px` and horizontal padding of at least `1 rem` on mobile and `2 rem` on desktop.
3. EACH page section SHALL have a consistent vertical separation of `4 rem–5 rem` between top-level sections on desktop.
4. THE UI_System SHALL apply consistent inner padding to Shell_Cards: `1.25 rem` on mobile and `1.75 rem–2 rem` on desktop.
5. WHERE a section contains a grid of cards, THE grid SHALL use `gap: 1.25 rem` on desktop and `gap: 0.75 rem` on mobile.

---

### Requirement 12: Color Consistency

**User Story:** As an evaluator looking at screenshots of NutriPrint, I want all UI colours to be from a defined palette, so that the product has a coherent brand identity rather than a patchwork of random colours.

#### Acceptance Criteria

1. THE UI_System SHALL use only the four canonical Color_Palette values — `#0F172A`, `#10B981`, `#F8FAFC`, `#FFFFFF` — as base colours, with allowed tints/shades and opacity variants derived from them.
2. THE UI_System SHALL use `#10B981` (Accent_Green) as the single interactive colour for all: primary CTA buttons, active nav states, progress bar fills, hover borders on cards, and input focus rings.
3. THE UI_System SHALL NOT use the saffron orange (`#F97316`) or any secondary accent colour for primary interactive elements — orange may only be used for supplementary chip labels or illustrative emojis.
4. WHEN a semantic colour is needed (error, warning, success, info), THE UI_System SHALL use: error → `#EF4444` tint, warning → `#F59E0B` tint, success → `#10B981` tint, info → `#3B82F6` tint. These semantic colours are permitted to be outside the four base Color_Palette values.

---

### Requirement 13: Mobile Responsiveness

**User Story:** As a teacher using NutriPrint on a mobile phone, I want all pages to render correctly and be fully usable on small screens, so that the product works in a real school environment where teachers primarily use phones.

#### Acceptance Criteria

1. THE UI_System SHALL ensure no page produces a horizontal scrollbar on viewports ≥ 320 px wide.
2. THE Navigation SHALL collapse to a hamburger + drawer layout on viewports < 1024 px.
3. ALL multi-column grids (stats, features, food cards, day-cards) SHALL collapse to single or double-column layouts on viewports ≤ 480 px.
4. EACH form input and button SHALL have a minimum tap target size of 44 × 44 px on mobile.
5. THE UI_System SHALL include `@media (prefers-reduced-motion: reduce)` blocks for all animations and transitions, disabling or minimising motion for users who have enabled the system accessibility preference.
6. THE UI_System SHALL ensure that all text remains legible (minimum `0.8 rem` body, minimum `1.4 rem` headings) on viewports ≤ 480 px without the user needing to zoom.

---

### Requirement 14: Loading and Empty States

**User Story:** As a teacher waiting for an AI-generated meal plan, I want to see polished loading animations, so that the wait feels intentional and the product feels premium rather than frozen.

#### Acceptance Criteria

1. WHEN an API call is in progress, THE UI_System SHALL replace the results area with the appropriate loading component (`ld-meal-card`, `ld-bmi-card`, `ld-advisor-typing`) rather than showing a blank space or native browser spinner.
2. THE `ld-meal-card` loading state SHALL include an animated multi-step progress list where each step transitions from pending → active → done. Steps MAY complete out of order as the backend processes them; strict sequential ordering is not required.
3. WHEN a page section has no data to display (e.g., no students on dashboard, no matching foods in catalog), THE UI_System SHALL render an `es-card` empty state with an icon, descriptive title, and optional action button.
4. THE UI_System SHALL animate loading and empty state cards into view using the `esFadeIn` / `ldFadeIn` keyframe animations already defined in the CSS files.
5. IF an API call fails, THEN THE UI_System SHALL display an `es-toast--error` or `es-card--error` component with a descriptive message and a retry button. Error components SHALL appear only when an API call actually fails, not for other error conditions.

---

### Requirement 15: No Functionality Regression

**User Story:** As the project owner, I want all existing features to continue working after the visual redesign, so that the redesign does not break any of the application's functional requirements.

#### Acceptance Criteria

1. THE UI_System SHALL NOT remove or rename any HTML element `id` or `class` attribute that is referenced by a selector, `querySelector`, `querySelectorAll`, `getElementById`, `getElementsByClassName`, or `addEventListener` call in any JavaScript file under `/static/js/`.
2. THE UI_System SHALL NOT remove any Jinja2 template variables, blocks, or macros from the template files.
3. THE UI_System SHALL NOT modify any FastAPI route handlers, Pydantic schemas, or database queries.
4. WHEN the redesigned pages are rendered, ALL API endpoints listed in `README.md` SHALL continue to return correct responses with the same HTTP status codes and response body schemas as the pre-redesign baseline.
5. THE UI_System SHALL NOT change the `action`, `method`, `name`, or `type` attributes of any existing HTML form element or any `<input>`, `<select>`, or `<textarea>` element inside an existing form. No new `<form>` elements may wrap or restructure existing form markup in a way that alters the fields submitted to the server.
6. WHEN the redesigned CSS and HTML are loaded, ALL JavaScript modules under `/static/js/` — including but not limited to `auth.js`, `demo_mode.js`, and `splash.js` — SHALL execute without runtime errors and SHALL produce the same observable DOM mutations, event handler registrations, API call behaviour, and form submission workflows as the pre-redesign baseline. Adding new CSS classes or wrapper `<div>` elements is permitted only if the existing element IDs, class selectors, and DOM traversal paths used by JavaScript remain intact and reachable.
