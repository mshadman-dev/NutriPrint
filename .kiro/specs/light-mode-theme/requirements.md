# Requirements Document

## Introduction

NutriPrint currently uses an exclusively dark-mode design (dark backgrounds with green accents). This feature introduces a professional light-mode theme as a prototype/preview that coexists with the existing dark mode, applied initially to a subset of pages (Homepage, BMI, Meal Planner). The goal is to evaluate light mode viability through a side-by-side comparison before any permanent adoption. The implementation must be non-destructive — the existing dark theme remains intact and default.

## Glossary

- **Theme_Toggle**: A persistent UI control that allows users to switch between dark mode and light mode without page reload.
- **Light_Theme**: A CSS theme layer providing white backgrounds, subtle green accents (#10B981), soft shadows, and premium SaaS-style styling.
- **Dark_Theme**: The existing default NutriPrint dark-mode styling (dark backgrounds #060a0e, green accents, dark surface colors).
- **Theme_Stylesheet**: A dedicated CSS file (`light-theme.css`) containing all light-mode overrides scoped to a data attribute on the document root.
- **Scoped_Pages**: The three pages initially receiving the light-mode treatment: Homepage (`/`), BMI page (`/bmi`), and Meal Planner page (`/meal-planner`).
- **Theme_Preference**: The user's selected theme choice stored in the browser's localStorage for persistence across sessions.
- **Preview_Mode**: A development-only comparison mechanism allowing side-by-side visual evaluation of dark mode and light mode without committing to permanent changes.
- **Design_System**: The existing set of CSS custom properties (design tokens) defined in `design-system.css` and `base.css` that control colors, spacing, typography, and shadows.

## Requirements

### Requirement 1: Theme Toggle Control

**User Story:** As a user, I want a visible toggle control in the navigation header, so that I can switch between dark mode and light mode on supported pages.

#### Acceptance Criteria

1. THE Theme_Toggle SHALL render as a clickable button within the site header navigation area, visible without scrolling on viewports from 320px to 2560px wide, with a minimum interactive target size of 44×44 CSS pixels.
2. WHEN the page loads and no user theme preference has been persisted, THE System SHALL apply Dark_Theme as the default active theme by setting the `data-theme` attribute on the root HTML element to "dark".
3. WHEN a user clicks the Theme_Toggle, THE Theme_Toggle SHALL switch the active theme from Dark_Theme to Light_Theme or from Light_Theme to Dark_Theme by updating the `data-theme` attribute on the root HTML element within 300 milliseconds.
4. THE Theme_Toggle SHALL display a sun icon when Dark_Theme is active (indicating the action will switch to light) or a moon icon when Light_Theme is active (indicating the action will switch to dark).
5. WHEN the active theme changes, THE Theme_Toggle SHALL update its displayed icon to reflect the new active theme state within the same 300-millisecond transition.
6. THE Theme_Toggle SHALL be keyboard-focusable and operable via Enter or Space key press, producing the same theme switch behavior as a click.
7. THE Theme_Toggle SHALL include an aria-label that communicates the current action, reading "Switch to light mode" when Dark_Theme is active and "Switch to dark mode" when Light_Theme is active.
8. THE Theme_Toggle SHALL be rendered on all pages that extend the base site template (base.html), and only on those pages.

### Requirement 2: Theme Preference Persistence

**User Story:** As a user, I want my theme preference to be remembered across page navigations and browser sessions, so that I do not need to re-select my preferred theme on every visit.

#### Acceptance Criteria

1. WHEN a user selects a theme via the Theme_Toggle, THE Theme_Preference SHALL be saved to the browser's localStorage under the key `nutriprint-theme` with a value of `"light"` or `"dark"` corresponding to the selected theme.
2. WHEN a Scoped_Page loads, THE Theme_Stylesheet SHALL read the stored Theme_Preference from localStorage and apply the corresponding theme by setting the `data-theme` attribute on the `<html>` element before the first contentful paint, so that no flash of the incorrect theme is visible to the user.
3. IF no Theme_Preference exists in localStorage, THEN THE Theme_Stylesheet SHALL default to Dark_Theme by not setting the `data-theme` attribute (or setting it to `"dark"`).
4. IF localStorage is unavailable (blocked by browser settings or private browsing restrictions) or the stored Theme_Preference value is not one of the valid values (`"light"`, `"dark"`), THEN THE Theme_Stylesheet SHALL fall back to Dark_Theme and the Theme_Toggle SHALL remain functional for the current session without producing JavaScript errors.
5. WHEN a user navigates between Scoped_Pages, THE Theme_Preference SHALL persist in localStorage and the selected theme SHALL remain visually active without requiring re-selection.

### Requirement 3: Light Theme Visual Design

**User Story:** As a user, I want the light theme to provide a professional, premium SaaS appearance with white backgrounds and green accents, so that the application feels modern and easy to read in well-lit environments.

#### Acceptance Criteria

1. WHILE Light_Theme is active, THE Design_System SHALL set the `--color-bg` custom property to `#FFFFFF` for the page body and `--color-surface` to `#F8FAFC` for card components, stat cards, day cards, and other container elements that reference this token.
2. WHILE Light_Theme is active, THE Design_System SHALL set `--color-text` to `#0F172A` for primary text and `--color-text-muted` to `#64748B` for secondary/muted text.
3. WHILE Light_Theme is active, THE Design_System SHALL set `--shadow-card` to `0 4px 12px rgba(15,23,42,0.06)` and `--shadow-hover` to `0 10px 24px rgba(15,23,42,0.10)` for card components and elements that reference these shadow tokens.
4. WHILE Light_Theme is active, THE Design_System SHALL set `--color-accent` to `#10B981` for use as background fills on buttons, badges, and active filter chips, pairing it with white (`#FFFFFF`) foreground text to maintain a minimum 3:1 contrast ratio for large UI components.
5. WHILE Light_Theme is active, THE Design_System SHALL set border colors to `rgba(148,163,184,0.18)` for card boundaries and section dividers via the relevant border token.
6. WHILE Light_Theme is active, THE Design_System SHALL set the `.site-header` background to `rgba(255,255,255,0.92)` with `backdrop-filter: blur(20px)` and a bottom border of `1px solid rgba(148,163,184,0.12)`.
7. WHILE Light_Theme is active, THE Design_System SHALL ensure all text elements at or below 14pt (non-bold) or 18pt (bold) maintain a minimum contrast ratio of 4.5:1 against their immediate background, and text elements above those thresholds maintain a minimum of 3:1 (WCAG 2.1 AA compliance).
8. WHILE Light_Theme is active, THE Design_System SHALL define hover and focus states for interactive elements (buttons, links, filter chips) using `--color-accent-dark` (`#0D9668`) as the hover background and a visible `2px solid var(--color-accent)` outline offset by 2px for keyboard focus indication.
9. WHILE Light_Theme is active, THE Design_System SHALL style form inputs (text fields, select menus, number inputs) with a background of `#FFFFFF`, a border of `1px solid rgba(148,163,184,0.30)`, text color of `#0F172A`, and placeholder text color of `#94A3B8`.

### Requirement 4: Scoped Page Application

**User Story:** As a developer, I want the light theme to apply only to the Homepage, BMI page, and Meal Planner page initially, so that the feature can be evaluated incrementally without affecting other pages.

#### Acceptance Criteria

1. WHILE Light_Theme is active and the user is on the Homepage (`/`, `data-page="home"`), THE Light_Theme SHALL apply all light-mode CSS variable overrides to the page content, hero section, stat cards, and navigation such that background colors, text colors, and border colors render using the defined Light_Theme palette values.
2. WHILE Light_Theme is active and the user is on the BMI page (`/bmi`, `data-page="bmi"`), THE Light_Theme SHALL apply light-mode CSS variable overrides to the BMI form, gauge display, result cards, and advice callouts such that background colors, text colors, and border colors render using the defined Light_Theme palette values.
3. WHILE Light_Theme is active and the user is on the Meal Planner page (`/meal-planner`, `data-page="meal-planner"`), THE Light_Theme SHALL apply light-mode CSS variable overrides to the day cards, meal rows, generation form, and plan display such that background colors, text colors, and border colors render using the defined Light_Theme palette values.
4. WHILE Light_Theme is active and the user is on any page whose `data-page` attribute value is NOT one of "home", "bmi", or "meal-planner", THE Light_Theme overrides SHALL NOT apply, and the page SHALL render using the Dark_Theme palette values.
5. WHEN a user navigates from a Scoped_Page to a non-Scoped page, THE system SHALL complete the theme transition within a single rendering frame such that no intermediate state is visible where both light and dark styles are partially applied, and Cumulative Layout Shift attributable to the transition SHALL be 0.
6. IF a new page is added to the application without explicitly being added to the scoped page list, THEN THE system SHALL render that page using the Dark_Theme by default.

### Requirement 5: Non-Destructive Implementation

**User Story:** As a developer, I want the light theme to be implemented as an additive layer without modifying existing dark-mode CSS, so that the dark theme remains unchanged and the feature can be removed cleanly if needed.

#### Acceptance Criteria

1. THE Theme_Stylesheet SHALL exist as a separate CSS file (`static/css/light-theme.css`) that does not add, remove, or change any lines in existing CSS files (`design-system.css`, `base.css`, or page-specific stylesheets), verifiable by comparing those files against their current Git-committed state.
2. THE Light_Theme overrides SHALL be scoped using the CSS attribute selector `[data-theme="light"]` applied to the `<html>` element, and the Theme_Stylesheet SHALL be loaded after all existing stylesheets in document order so that its selectors take precedence without using `!important`.
3. IF the Theme_Stylesheet file and Theme_Toggle script file are both removed from the project and their corresponding `<link>` and `<script>` references are removed from templates, THEN THE Dark_Theme SHALL render identically to the current Git-committed production state, verifiable by automated visual screenshot comparison or a byte-level CSS/JS diff showing zero changes to existing files.
4. THE Theme_Toggle JavaScript SHALL be contained in a single dedicated script file (`static/js/theme-toggle.js`) that does not add, remove, or change any lines in existing JavaScript files, verifiable by comparing those files against their current Git-committed state.
5. WHEN the Theme_Stylesheet and Theme_Toggle script are integrated into Jinja2 templates, THE integration SHALL be limited to adding new `<link>` and `<script>` tags and a conditional `data-theme` attribute, without modifying or removing any existing template markup, so that removing those additions restores the template to its prior state.

### Requirement 6: Preview and Comparison Mechanism

**User Story:** As a developer, I want a side-by-side comparison view and documented analysis of the light theme versus dark theme, so that stakeholders can evaluate which pages benefit from each mode before committing changes.

#### Acceptance Criteria

1. THE Preview_Mode SHALL provide a documented comparison showing each Scoped_Page (Homepage, BMI, Meal Planner) in both Dark_Theme and Light_Theme, using either embedded screenshot references or a linked HTML preview page that displays both themes side by side for each page.
2. THE Preview_Mode comparison SHALL include a written analysis for each Scoped_Page that evaluates Light_Theme against at least the following criteria: text readability, visual contrast and hierarchy, consistency with brand identity, and suitability for data-heavy content.
3. THE Preview_Mode comparison SHALL provide a per-page recommendation stating whether Light_Theme or Dark_Theme is more suitable, with at least one specific reason per recommendation grounded in the evaluation criteria from criterion 2.
4. THE Preview_Mode comparison SHALL include a section identifying which non-scoped pages (Food Catalog, Dashboard, About, Login) could benefit from Light_Theme adoption, with a brief rationale for each page assessed.
5. THE Preview_Mode documentation SHALL be stored in the project repository as a markdown file (`docs/light-theme-comparison.md`) and SHALL contain a summary table listing each assessed page alongside its recommended theme and primary rationale.
6. THE Preview_Mode documentation SHALL include a final stakeholder action section summarizing the overall recommendation (adopt light theme on specific pages, expand scope, or retain dark theme) so that reviewers can approve or reject without reading the full analysis.

### Requirement 7: Theme Transition Smoothness

**User Story:** As a user, I want theme changes to feel smooth and polished, so that switching themes does not create a jarring flash or layout disruption.

#### Acceptance Criteria

1. WHEN the theme changes, THE Design_System SHALL apply a CSS transition on background-color, color, border-color, and box-shadow properties with a duration of 200–300 milliseconds and an ease timing function.
2. WHEN a Scoped_Page loads with Light_Theme active, THE page SHALL apply the Light_Theme data-attribute to the HTML element before the first contentful paint so that no frame of Dark_Theme content is visible to the user.
3. IF the Theme_Preference script fails to load or execute, THEN THE page SHALL render using Dark_Theme with all CSS custom properties resolving to their Dark_Theme defaults, no unstyled or collapsed elements, and no browser console errors originating from theme logic.
4. WHILE a theme transition is in progress, THE Design_System SHALL NOT cause any element to change its computed width or height, preventing layout shift during the transition.
5. WHILE the user's operating system has `prefers-reduced-motion: reduce` enabled, THE Design_System SHALL disable all theme transition durations so that theme changes apply immediately without animation.
