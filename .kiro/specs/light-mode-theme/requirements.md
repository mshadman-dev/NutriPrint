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

1. THE Theme_Toggle SHALL render as a clickable button in the site header navigation area, visible on all viewport sizes (mobile and desktop).
2. WHEN a user clicks the Theme_Toggle, THE Theme_Toggle SHALL switch the active theme from Dark_Theme to Light_Theme or from Light_Theme to Dark_Theme within 300 milliseconds.
3. THE Theme_Toggle SHALL display a visual indicator (sun icon for light mode, moon icon for dark mode) representing the currently active theme.
4. WHEN the active theme changes, THE Theme_Toggle SHALL update its icon to reflect the new active theme state.
5. THE Theme_Toggle SHALL be keyboard-accessible and operable via Enter or Space key press.
6. THE Theme_Toggle SHALL include an accessible label (aria-label) describing its function for screen reader users.

### Requirement 2: Theme Preference Persistence

**User Story:** As a user, I want my theme preference to be remembered across page navigations and browser sessions, so that I do not need to re-select my preferred theme on every visit.

#### Acceptance Criteria

1. WHEN a user selects a theme via the Theme_Toggle, THE Theme_Preference SHALL be saved to the browser's localStorage under a defined key (`nutriprint-theme`).
2. WHEN a Scoped_Page loads, THE Theme_Stylesheet SHALL read the stored Theme_Preference from localStorage and apply the corresponding theme before the page content becomes visible.
3. IF no Theme_Preference exists in localStorage, THEN THE Theme_Stylesheet SHALL default to Dark_Theme.
4. WHEN a user navigates between pages, THE Theme_Preference SHALL persist and the selected theme SHALL remain active on all Scoped_Pages.

### Requirement 3: Light Theme Visual Design

**User Story:** As a user, I want the light theme to provide a professional, premium SaaS appearance with white backgrounds and green accents, so that the application feels modern and easy to read in well-lit environments.

#### Acceptance Criteria

1. WHILE Light_Theme is active, THE Design_System SHALL override the background color to white (`#FFFFFF`) for the page body and `#F8FAFC` for surface elements.
2. WHILE Light_Theme is active, THE Design_System SHALL set primary text color to `#0F172A` (dark slate) and muted text color to `#64748B`.
3. WHILE Light_Theme is active, THE Design_System SHALL apply subtle box shadows (`0 4px 12px rgba(15,23,42,0.06)`) to card components and elevated elements.
4. WHILE Light_Theme is active, THE Design_System SHALL use `#10B981` (emerald green) as the accent color for interactive elements, badges, and highlights.
5. WHILE Light_Theme is active, THE Design_System SHALL set border colors to `rgba(148,163,184,0.18)` for card boundaries and section dividers.
6. WHILE Light_Theme is active, THE Design_System SHALL set the navigation header background to `rgba(255,255,255,0.92)` with a `blur(20px)` backdrop filter.
7. WHILE Light_Theme is active, THE Design_System SHALL ensure all text elements maintain a contrast ratio of at least 4.5:1 against their background (WCAG AA compliance).

### Requirement 4: Scoped Page Application

**User Story:** As a developer, I want the light theme to apply only to the Homepage, BMI page, and Meal Planner page initially, so that the feature can be evaluated incrementally without affecting other pages.

#### Acceptance Criteria

1. WHILE Light_Theme is active and the user is on the Homepage (`/`), THE Light_Theme SHALL apply all light-mode overrides to the page content, hero section, stat cards, and navigation.
2. WHILE Light_Theme is active and the user is on the BMI page (`/bmi`), THE Light_Theme SHALL apply light-mode overrides to the BMI form, gauge display, result cards, and advice callouts.
3. WHILE Light_Theme is active and the user is on the Meal Planner page (`/meal-planner`), THE Light_Theme SHALL apply light-mode overrides to the day cards, meal rows, generation form, and plan display.
4. WHILE Light_Theme is active and the user is on a non-Scoped page (Food Catalog, Dashboard, About, Login), THE Light_Theme overrides SHALL NOT apply, and the page SHALL render using the Dark_Theme.
5. WHEN a user navigates from a Scoped_Page to a non-Scoped page, THE theme display SHALL transition gracefully without visual jarring or layout shifts.

### Requirement 5: Non-Destructive Implementation

**User Story:** As a developer, I want the light theme to be implemented as an additive layer without modifying existing dark-mode CSS, so that the dark theme remains unchanged and the feature can be removed cleanly if needed.

#### Acceptance Criteria

1. THE Theme_Stylesheet SHALL exist as a separate CSS file (`static/css/light-theme.css`) that does not modify existing CSS files (`design-system.css`, `base.css`, or page-specific stylesheets).
2. THE Light_Theme overrides SHALL be scoped using a CSS attribute selector (e.g., `[data-theme="light"]`) applied to the `<html>` or `<body>` element.
3. IF the Theme_Stylesheet file is removed from the project, THEN THE Dark_Theme SHALL continue to function identically to the current production state with no visual regressions.
4. THE Theme_Toggle JavaScript SHALL be contained in a single dedicated script file (`static/js/theme-toggle.js`) that does not modify existing JavaScript files.

### Requirement 6: Preview and Comparison Mechanism

**User Story:** As a developer, I want a side-by-side comparison view and documented analysis of the light theme versus dark theme, so that stakeholders can evaluate which pages benefit from each mode before committing changes.

#### Acceptance Criteria

1. THE Preview_Mode SHALL provide a documented comparison (screenshot references or HTML preview page) showing each Scoped_Page in both Dark_Theme and Light_Theme side by side.
2. THE Preview_Mode comparison SHALL include a written analysis identifying pros and cons of Light_Theme for each Scoped_Page.
3. THE Preview_Mode comparison SHALL identify which pages benefit from Light_Theme and which pages look better in Dark_Theme, with reasoning for each recommendation.
4. THE Preview_Mode documentation SHALL be stored in the project repository as a markdown file (`docs/light-theme-comparison.md`) for stakeholder review.

### Requirement 7: Theme Transition Smoothness

**User Story:** As a user, I want theme changes to feel smooth and polished, so that switching themes does not create a jarring flash or layout disruption.

#### Acceptance Criteria

1. WHEN the theme changes, THE Design_System SHALL apply a CSS transition on background-color and color properties with a duration of 200–300 milliseconds and an ease timing function.
2. WHEN a Scoped_Page loads with Light_Theme active, THE page SHALL NOT display a flash of Dark_Theme content before applying Light_Theme (no FOUT/FOUC).
3. IF the Theme_Preference script fails to load or execute, THEN THE page SHALL render using Dark_Theme without errors or broken layout.
