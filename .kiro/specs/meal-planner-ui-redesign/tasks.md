# Implementation Plan

## Overview

This plan fixes the Meal Planner page's dark theme and narrow fixed-width layout by converting it to a polished light theme with full-width responsive grid. The fix is purely CSS/HTML — no JavaScript, FastAPI, or backend changes. The workflow follows the exploratory bugfix methodology: write tests first to confirm the bug, then implement the fix, then verify tests pass.

## Tasks

- [ ] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Dark Theme and Fixed-Width Layout Defects
  - **IMPORTANT**: Write this property-based test BEFORE implementing the fix
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bug exists
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the dark theme and narrow layout bug exists
  - **Scoped PBT Approach**: Scope the property to the concrete failing cases: page renders with dark CSS variables and fixed 420px grid column
  - Write a DOM/style inspection test that loads `meal_planner.html` and asserts:
    - `body` computed background color is `#FFFFFF` (not `#060a0e`)
    - `:root` CSS variable `--bg` resolves to a light value (not `#060a0e`)
    - `:root` CSS variable `--surface` resolves to a light value (not `#0d1117`)
    - The `#mealForm` section grid does NOT use fixed `420px` column (no `xl:grid-cols-[420px_1fr]`)
    - `#advisorPanel` is NOT constrained within a narrow 420px parent column
    - Card components (`.mp-hero`, `.mp-form-card`, `.mp-placeholder`) have consistent border-radius values
  - Run test on UNFIXED code - expect FAILURE (this confirms the bug exists)
  - Document counterexamples found (e.g., "background resolves to rgb(6,10,14) instead of white", "grid has fixed 420px column", "advisor panel width ≤ 420px")
  - Mark task complete when test is written, run, and failure is documented
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - JavaScript Functionality and DOM Structure Unchanged
  - **IMPORTANT**: Follow observation-first methodology
  - **IMPORTANT**: Write these tests BEFORE implementing the fix
  - Observe on UNFIXED code:
    - All critical DOM IDs exist: `#advisorPanel`, `#mealResult`, `#generateBtn`, `#formError`, `#mealLoading`, `#mealPlaceholder`, `#mealForm`, `#recipeQRModal`
    - All form field IDs exist: `#mealSchool`, `#mealStudent`, `#mealAge`, `#mealGender`, `#mealHeight`, `#mealWeight`, `#mealDiet`, `#mealActivity`, `#mealRegion`, `#mealMonth`, `#mealStrategy`, `#mealHealthNotes`
    - Button text "Generate Meal Plan with Selected AI Advice" is present in `#generateBtn`
    - The auth-check script block exists in the page
    - Hero section button text "Start Planning" and "Browse Foods" is present
    - QR modal has required structure with `#recipeQRTitle`, `#recipeQRDesc`, `#recipeQRCanvas`, `#recipeQRLink`, `#recipeQRClose`
    - `generateMeal` function is callable via `#generateBtn` onclick
    - `clearFieldError` handlers remain on inputs
    - `onDietChange` handler remains on diet select
    - Page loads all required script files: `advisor.js`, `nutrition_score.js`, `weekly_summary.js`, `meal.js`
  - Write property-based tests that for all critical DOM IDs and form elements: they exist, are accessible via `getElementById`, and have expected attributes/handlers
  - Verify tests PASS on UNFIXED code (confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11_

- [ ] 3. Implement the meal planner UI redesign fix

  - [ ] 3.1 Replace dark `:root` variables with light-theme values in inline style block
    - Change `--bg: #060a0e` → `--bg: #FFFFFF`
    - Change `--surface: #0d1117` → `--surface: #F8FAFC`
    - Change `--border: #1a2332` → `--border: rgba(148,163,184,0.18)`
    - Change `--border-hi: #253347` → `--border-hi: rgba(148,163,184,0.3)`
    - Change `--green: #1D9E75` → `--green: #14B8A6`
    - Change `--green-hi: #3EFFA8` → `--green-hi: #0D9488`
    - Change `--text: #E2E8F0` → `--text: #0F172A`
    - Change `--muted: #94A3B8` → `--muted: #64748B`
    - Change `--dim: #4A5568` → `--dim: #94A3B8`
    - _Bug_Condition: isBugCondition(page) where page.inlineStyleBlock.definesVariable('--bg', '#060a0e') AND page.inlineStyleBlock.definesVariable('--surface', '#0d1117')_
    - _Expected_Behavior: Light theme variables — white background, soft gray cards, teal accents, dark text_
    - _Preservation: No DOM IDs or class names referenced by JS are changed_
    - _Requirements: 2.2, 2.6_

  - [ ] 3.2 Override base.html dark body background for the meal planner page
    - Add `body[data-page="meal-planner"] { background: #FFFFFF; color: #0F172A; }` to the inline style block
    - This neutralizes the global dark background without modifying `base.html`
    - The `{% block page_id %}meal-planner{% endblock %}` already sets `data-page` attribute
    - _Bug_Condition: base.html sets body background to dark globally_
    - _Expected_Behavior: Meal planner page background is white_
    - _Preservation: Other pages retain their dark theme_
    - _Requirements: 2.2_

  - [ ] 3.3 Replace fixed-width grid with responsive layout
    - Change `xl:grid-cols-[420px_1fr]` on `#mealForm` section to a responsive class like `lg:grid-cols-2`
    - This allows both columns to share viewport width proportionally
    - On mobile, columns stack vertically (default grid behavior)
    - _Bug_Condition: page.layoutGrid.hasFixedColumn('420px')_
    - _Expected_Behavior: Full-width responsive grid distributes space proportionally_
    - _Preservation: Section stacking order unchanged, mobile still stacks vertically_
    - _Requirements: 2.1, 2.5_

  - [ ] 3.4 Move `#advisorPanel` outside the narrow form column to its own wider grid cell
    - Restructure HTML: move `<div id="advisorPanel" class="mt-5"></div>` from inside `.mp-form-card` to its own grid cell or a full-width section below the form
    - Keep `id="advisorPanel"` intact so `advisor.js` selector still works
    - Ensure the advisor panel has sufficient width (not constrained to 420px)
    - Consider placing Student Details (form) and AI Advisor side by side in the 2-col grid, with Generate button below spanning full width
    - _Bug_Condition: page.advisorPanel.maxWidth <= 420_
    - _Expected_Behavior: Advisor panel width > 500px on desktop_
    - _Preservation: #advisorPanel DOM ID preserved, advisor.js continues to render into it_
    - _Requirements: 2.1, 2.3_

  - [ ] 3.5 Override design-system.css dark variables for meal planner scope
    - Add scoped overrides in the inline style block: `[data-page="meal-planner"] { --surface: #FFFFFF; --surface-light: #F1F5F9; --border: rgba(148,163,184,0.18); --text: #0F172A; --text-muted: #64748B; --shadow-sm: 0 4px 12px rgba(15,23,42,0.04); --shadow-md: 0 10px 30px rgba(15,23,42,0.06); }`
    - This ensures `advisor.css` picks up light colors on this page without modifying `design-system.css`
    - _Bug_Condition: design-system.css defines dark tokens consumed by advisor.css_
    - _Expected_Behavior: Advisor shell, cards, messages render with light backgrounds and dark text_
    - _Preservation: design-system.css is NOT modified; other pages unaffected_
    - _Requirements: 2.2, 2.4_

  - [ ] 3.6 Standardize card styling across all components
    - Apply consistent values to `.mp-hero`, `.mp-form-card`, `.mp-placeholder`, `.ld-meal-card`:
      - `border-radius: 1.5rem`
      - `padding: 1.5rem` (adjust hero separately if needed)
      - `box-shadow: 0 14px 35px rgba(15,23,42,0.06)`
      - `border: 1px solid rgba(148,163,184,0.18)`
    - Update `.mp-ph-item` to use consistent inner card styling
    - _Bug_Condition: page.cardStyles.areInconsistent()_
    - _Expected_Behavior: All cards share consistent border-radius, shadow, and border styling_
    - _Preservation: DOM structure and class names unchanged_
    - _Requirements: 2.4_

  - [ ] 3.7 Update hero section to light theme
    - Replace dark gradient `background: linear-gradient(135deg, #071f17 0%, #0a2e1f 40%, #0d3d2a 100%)` with a light teal/white gradient
    - Update `.mp-hero-label` from dark neon green to teal accent on white
    - Update `h1` text colors from white/green-gradient to navy/teal
    - Update `.mp-hero-desc` color from `rgba(255,255,255,.65)` to `#64748B`
    - Update `.mp-btn-primary` and `.mp-btn-ghost` to light-theme button styles
    - Update `.mp-hero-step` cards from dark glass to light cards with subtle borders
    - Remove dot-grid overlay (`::after` background-image) or adapt to light version
    - _Bug_Condition: Hero renders with dark gradient and white/neon text_
    - _Expected_Behavior: Hero displays light theme with teal/navy accents, professional appearance_
    - _Preservation: Button text "Start Planning" and "Browse Foods" unchanged, href attributes unchanged_
    - _Requirements: 2.6_

  - [ ] 3.8 Update form inputs to light theme
    - Change `.mp-input`, `.mp-select`, `.mp-textarea` background from `#0b1120` to `#FFFFFF`
    - Update border color from `var(--border-hi)` (dark) to light border value
    - Update `color` to dark text
    - Update `::placeholder` color to muted gray
    - Update `.mp-select option` background to white
    - Update focus ring to use teal accent
    - _Bug_Condition: Form inputs have dark backgrounds (#0b1120) with light text_
    - _Expected_Behavior: White input backgrounds, dark text, teal focus ring_
    - _Preservation: All input IDs, names, event handlers unchanged_
    - _Requirements: 2.6_

  - [ ] 3.9 Update `#mealResult` overrides for light theme
    - Remove or invert the dark-theme Tailwind class overrides block
    - In light mode, default Tailwind utility classes (`.bg-white`, `.text-gray-800`, `.border-slate-100`) will render correctly without forced overrides
    - Keep `#mealResult > div { color: var(--text); }` with updated light text variable
    - Keep `#nutritionScoreContainer`, `#weeklySummaryContainer` variable scoping with light surface value
    - _Bug_Condition: #mealResult overrides force dark colors on Tailwind utilities_
    - _Expected_Behavior: Meal results render naturally with Tailwind light utility classes_
    - _Preservation: #mealResult DOM ID preserved, JS rendering unchanged_
    - _Requirements: 2.6_

  - [ ] 3.10 Update QR modal to light theme
    - Change `.qrm-panel` background from `#0d1117` to `#FFFFFF`
    - Update `.qrm-panel` border to light border value
    - Update text colors (`.qrm-kicker`, `.qrm-scan-hint`) to dark/muted colors
    - Update `.qrm-close` button styling for light background
    - Update `.qrm-link` color from `#3EFFA8` to teal accent
    - Keep header gradient (green-themed) or lighten it
    - _Bug_Condition: QR modal panel has dark background (#0d1117)_
    - _Expected_Behavior: White modal panel with teal accents_
    - _Preservation: #recipeQRModal, closeRecipeQR() function, all QR-related IDs unchanged_
    - _Requirements: 2.6_

  - [ ] 3.11 Add light-theme overrides to `static/css/advisor.css`
    - Add scoped rules under `[data-page="meal-planner"]` selector for:
      - `.advisor-shell` — light background, subtle border and shadow
      - `.advisor-chat-card`, `.advisor-selected-card` — white/light-gray backgrounds
      - `.advisor-messages` — light background
      - `.advisor-message.assistant .advisor-msg-content` — light card styling
      - `.advisor-chip` — teal on white instead of neon green on dark
      - `.advisor-rec-card` — white background with subtle border
      - `.advisor-empty` — light dashed border style
      - `.advisor-input` — white background, dark text
      - `.advisor-select` — white background
    - Do NOT modify existing dark-theme rules — only ADD scoped overrides
    - _Bug_Condition: advisor.css renders dark cards/backgrounds via design-system.css variables_
    - _Expected_Behavior: Advisor components render in light theme on meal planner page_
    - _Preservation: advisor.css dark theme preserved for other pages; no JS changes_
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ] 3.12 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Light Theme and Full-Width Layout
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior (light bg, responsive grid, wider advisor)
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bug is fixed)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 3.13 Verify preservation tests still pass
    - **Property 2: Preservation** - JavaScript Functionality and DOM Structure Unchanged
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all DOM IDs still resolve, form handlers still work, script references intact
    - Confirm no JS functionality was broken by the HTML restructuring

- [ ] 4. Checkpoint - Ensure all tests pass
  - Run the full test suite to confirm both exploration and preservation tests pass
  - Visually verify the page renders with light theme at various viewport widths (375px, 768px, 1024px, 1440px, 1920px)
  - Confirm the AI Nutrition Advisor panel has adequate width on desktop
  - Confirm card styling is consistent across all components
  - Ensure all tests pass, ask the user if questions arise

## Task Dependency Graph

```json
{
  "waves": [
    ["1", "2"],
    ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11"],
    ["3.12", "3.13"],
    ["4"]
  ]
}
```

## Notes

- Files to modify: `templates/meal_planner.html` (inline styles + HTML structure), `static/css/advisor.css` (scoped light-theme overrides)
- Files NOT to modify: `static/js/advisor.js`, `meal.js`, `nutrition_score.js`, `weekly_summary.js`, any Python/FastAPI files, `static/css/design-system.css`
- Critical DOM IDs to preserve: `#advisorPanel`, `#mealResult`, `#generateBtn`, `#formError`, `#mealLoading`, `#mealPlaceholder`, `#mealForm`, `#recipeQRModal`
- The bug condition exploration test (task 1) is expected to FAIL on unfixed code — this confirms the bug exists
- The preservation tests (task 2) are expected to PASS on unfixed code — this confirms baseline behavior
- After the fix (tasks 3.12 and 3.13), both test suites should PASS
