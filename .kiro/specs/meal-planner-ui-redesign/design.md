# Meal Planner UI Redesign Bugfix Design

## Overview

The Meal Planner page (`templates/meal_planner.html`) suffers from a dark theme with a narrow fixed-width layout that wastes screen real estate and looks unprofessional. This fix converts the page to a clean light theme with full-width responsive layout, wider AI Nutrition Advisor panel, and consistent card styling. The fix is purely CSS/HTML — no JavaScript logic, FastAPI endpoints, or backend behaviour changes are made.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the visual defect — the page renders with dark theme colors and a narrow `xl:grid-cols-[420px_1fr]` layout that constrains content
- **Property (P)**: The desired visual state — light theme (white bg, gray cards, teal/navy accents) with full-width responsive layout and wider AI panel
- **Preservation**: All JavaScript-driven functionality (meal generation, AI advisor, nutrition scores, weekly summaries, QR modal, auth check) must remain unchanged
- **`meal_planner.html`**: The Jinja2 template at `templates/meal_planner.html` that extends `base.html` and contains the inline `<style>` block with all `mp-*` CSS classes
- **`design-system.css`**: Defines dark theme CSS variables (`--surface`, `--border`, `--text`, etc.) consumed by `advisor.css`
- **`advisor.css`**: Styles the AI Nutrition Advisor panel rendered by `advisor.js` into `#advisorPanel`
- **`base.css`**: Already defines a light design system with tokens like `--color-bg: #F8FAFC`, `--color-surface: #FFFFFF`, etc.
- **Critical DOM IDs**: `#advisorPanel`, `#mealResult`, `#generateBtn`, `#formError`, `#mealLoading`, `#mealPlaceholder`, `#mealForm`, `#recipeQRModal` — must remain in the DOM

## Bug Details

### Bug Condition

The bug manifests when the Meal Planner page is viewed on any screen size. The inline `<style>` block defines dark CSS variables (`--bg: #060a0e`, `--surface: #0d1117`) and the layout uses `xl:grid-cols-[420px_1fr]` which fixes the form to 420px. The `advisor.css` references `var(--surface)` and `var(--border)` from `design-system.css` which are also dark-themed. Together these create a cramped, dark appearance that wastes horizontal space.

**Formal Specification:**
```
FUNCTION isBugCondition(page)
  INPUT: page of type RenderedMealPlannerPage
  OUTPUT: boolean
  
  RETURN page.inlineStyleBlock.definesVariable('--bg', '#060a0e')
         AND page.inlineStyleBlock.definesVariable('--surface', '#0d1117')
         AND page.layoutGrid.hasFixedColumn('420px')
         AND page.advisorPanel.maxWidth <= 420
         AND page.cardStyles.areInconsistent()
END FUNCTION
```

### Examples

- **Dark background**: Page body shows `#060a0e` background instead of `#FFFFFF` — user sees a dark, outdated interface
- **Narrow form column**: On a 1920px screen, the form is locked to 420px, leaving ~1400px for results — the form feels cramped while result area is oversized
- **Cramped advisor**: The AI Nutrition Advisor chat grid, recommendation cards, and input row are squeezed into 420px making text wrap excessively
- **Inconsistent cards**: Hero section uses `border-radius: 1.25rem` while placeholder items use `0.85rem` and form card uses `1.25rem` — shadows and borders vary

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- `meal.js` generates meal plans by calling the FastAPI endpoint and renders results into `#mealResult`
- `advisor.js` renders the AI Nutrition Advisor chat interface into `#advisorPanel`
- `nutrition_score.js` renders nutrient scores into `#nutritionScoreContainer`
- `weekly_summary.js` renders weekly summaries into `#weeklySummaryContainer`
- The auth-check script redirects unauthenticated users to `/login`
- The Recipe QR modal (`#recipeQRModal`) opens/closes via existing JS
- All form field IDs (`mealSchool`, `mealStudent`, `mealAge`, etc.) remain unchanged
- Button text "Generate Meal Plan with Selected AI Advice" remains unchanged
- The loading animation steps (`#mealLoadingSteps`) remain functional
- Mobile responsiveness stacks content vertically

**Scope:**
All inputs that do NOT involve visual rendering of the page layout/theme should be completely unaffected by this fix. This includes:
- Form submission logic (JavaScript event handlers)
- FastAPI endpoint calls and response processing
- AI advisor question/answer flow
- Nutrition score calculations
- QR code generation
- Authentication and redirect logic
- All `onclick`, `oninput`, `onchange` handlers

## Hypothesized Root Cause

Based on the bug description, the root causes are:

1. **Dark theme CSS variables in inline style block**: The template's `<style>` block defines `:root` variables (`--bg: #060a0e`, `--surface: #0d1117`, `--border: #1a2332`, etc.) that override any light theme. The `base.html` body also sets `background: #060a0e` globally.

2. **Fixed-width grid layout**: The `#mealForm` section uses `xl:grid-cols-[420px_1fr]` which hard-codes the left column at 420px regardless of viewport width, wasting space.

3. **Advisor constrained by parent column**: Since `#advisorPanel` is nested inside the 420px form column, it inherits the narrow width constraint. The `advisor.css` `advisor-chat-grid` tries to be 2-column but collapses to 1-column at `<1280px` due to the narrow parent.

4. **`design-system.css` defines dark tokens**: The variables `--surface: #0d1117`, `--border: rgba(255,255,255,0.08)`, etc. are consumed by `advisor.css` for card backgrounds and borders. These need light-theme overrides on the meal planner page.

5. **Inconsistent card styling**: Different sections use different `border-radius`, `padding`, `box-shadow`, and `border` values because they were authored ad-hoc in the inline style block.

## Correctness Properties

Property 1: Bug Condition - Light Theme and Full-Width Layout

_For any_ rendering of the Meal Planner page where the bug condition holds (dark theme variables are active and fixed-width grid is applied), the fixed template SHALL display a light theme (white `#FFFFFF` background, `#F8FAFC` card backgrounds, teal `#14B8A6` / navy `#0F172A` accents) with a full-width responsive grid layout that distributes space proportionally.

**Validates: Requirements 2.1, 2.2, 2.4, 2.5, 2.6**

Property 2: Preservation - JavaScript Functionality Unchanged

_For any_ user interaction that triggers JavaScript (form submission, AI advisor questions, meal plan generation, QR modal, auth checks), the fixed page SHALL produce exactly the same behavior as the original page, preserving all DOM IDs, class names referenced by JS, event handlers, and API call flows.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct:

**File**: `templates/meal_planner.html`

**Section**: Inline `<style>` block in `{% block head %}`

**Specific Changes**:

1. **Replace dark `:root` variables with light-theme values**: Change `--bg` to `#FFFFFF`, `--surface` to `#F8FAFC`, `--border` to `rgba(148,163,184,0.18)`, `--text` to `#0F172A`, `--muted` to `#64748B`, `--green` to `#14B8A6`, etc.

2. **Override `base.html` dark body background**: Add a page-scoped override `body[data-page="meal-planner"] { background: #FFFFFF; color: #0F172A; }` to neutralize the global dark background from `base.html`.

3. **Replace fixed-width grid with responsive layout**: Change `xl:grid-cols-[420px_1fr]` to a responsive layout that places Student Details and AI Advisor side by side in a balanced grid (e.g., `lg:grid-cols-2`), with the Generate button and Results area spanning full width below.

4. **Move `#advisorPanel` outside the narrow form column**: Restructure the HTML so the advisor panel occupies its own grid cell (or a wider section), giving it more horizontal space. Keep `id="advisorPanel"` intact so `advisor.js` still finds it.

5. **Override `design-system.css` dark variables for meal planner scope**: Add scoped overrides like `[data-page="meal-planner"] { --surface: #FFFFFF; --border: rgba(148,163,184,0.18); --text: #0F172A; --text-muted: #64748B; }` so `advisor.css` picks up light colors.

6. **Standardize card styling**: Apply consistent `border-radius: 1.5rem`, `padding: 1.5rem`, `box-shadow: 0 14px 35px rgba(15,23,42,0.06)`, `border: 1px solid rgba(148,163,184,0.18)` to all card components (hero, form, placeholder, loading, result).

7. **Update hero section to light theme**: Replace dark gradient background with a light teal/navy gradient or white card with accent border. Update text colors from white/green-neon to navy/teal.

8. **Update form inputs to light theme**: Change input backgrounds from `#0b1120` to `#FFFFFF` with subtle borders, focus states using teal instead of green-neon.

9. **Update `#mealResult` overrides for light theme**: Replace the dark-theme Tailwind class overrides (`.bg-white`, `.text-gray-800`, etc.) since in light mode the default Tailwind classes will already be correct. Remove or invert the dark overrides.

10. **Update QR modal to light theme**: Change `.qrm-panel` background from `#0d1117` to white, update text colors and borders accordingly.

**File**: `static/css/advisor.css`

**Changes**: Add light-theme overrides scoped to `[data-page="meal-planner"]` for `.advisor-shell`, `.advisor-messages`, `.advisor-chip`, `.advisor-message.assistant`, and card backgrounds so the advisor renders in light mode on this page.

**File**: `static/css/design-system.css`

**Changes**: No changes needed — we override variables at the page scope in the template's inline styles rather than modifying the global design system.

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bug on unfixed code (visual inspection confirms dark/narrow layout), then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bug BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Inspect the rendered page in a browser at various viewport widths. Check computed styles for background colors, grid column widths, and advisor panel dimensions. Run these checks on the UNFIXED code to confirm the defects.

**Test Cases**:
1. **Dark Background Test**: Assert `document.body` computed background is `#060a0e` (will confirm bug on unfixed code)
2. **Fixed Column Width Test**: Assert `#mealForm` grid template has `420px` fixed column (will confirm bug on unfixed code)
3. **Advisor Width Test**: Assert `#advisorPanel` computed width ≤ 420px on desktop (will confirm bug on unfixed code)
4. **Card Inconsistency Test**: Assert border-radius values differ between `.mp-hero`, `.mp-form-card`, and `.mp-ph-item` (will confirm bug on unfixed code)

**Expected Counterexamples**:
- Background color resolves to dark (`rgb(6, 10, 14)`) instead of white
- Grid column widths are `420px | remaining` instead of proportional
- Advisor panel is constrained to ≤420px width

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed template produces the expected visual behavior.

**Pseudocode:**
```
FOR ALL viewport WHERE isBugCondition(renderPage(viewport)) DO
  result := renderFixedPage(viewport)
  ASSERT result.bodyBackground == '#FFFFFF'
  ASSERT result.cardBackgrounds == '#F8FAFC'
  ASSERT result.layoutIsFullWidth == true
  ASSERT result.advisorPanelWidth > 500
  ASSERT result.cardBorderRadius.allEqual('1.5rem')
END FOR
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (i.e., JavaScript interactions), the fixed page produces the same result as the original page.

**Pseudocode:**
```
FOR ALL interaction WHERE NOT isBugCondition(interaction) DO
  ASSERT originalPage.handleInteraction(interaction) == fixedPage.handleInteraction(interaction)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many combinations of form inputs and interactions automatically
- It catches edge cases where DOM ID removal might break JS selectors
- It provides strong guarantees that JS functionality is unchanged

**Test Plan**: Observe behavior on UNFIXED code first for form submissions, AI advisor interactions, and navigation, then write tests verifying the same behavior on fixed code.

**Test Cases**:
1. **DOM ID Preservation**: Verify all critical IDs (`#advisorPanel`, `#mealResult`, `#generateBtn`, `#formError`, `#mealLoading`, `#mealPlaceholder`, `#mealForm`, `#recipeQRModal`) exist in the fixed DOM
2. **Form Submission Preservation**: Verify `generateMeal()` function can still read all form field values and submit to API
3. **Advisor Rendering Preservation**: Verify `advisor.js` can still render into `#advisorPanel` and the chat interface works
4. **Auth Redirect Preservation**: Verify unauthenticated users still get redirected to `/login`

### Unit Tests

- Test that all critical DOM IDs exist after HTML restructuring
- Test that CSS variables resolve to light-theme values on the meal planner page
- Test that form field IDs and their parent structure allow `getElementById` access
- Test that grid layout is responsive (collapses on mobile, expands on desktop)

### Property-Based Tests

- Generate random viewport widths (320px–2560px) and verify the layout remains responsive without horizontal overflow
- Generate random sequences of form interactions (fill fields, click generate, open advisor) and verify no JS errors
- Test that all `.mp-*` class elements have consistent computed card styles (border-radius, shadow, padding)

### Integration Tests

- Full flow: load page → fill form → interact with AI advisor → generate meal plan → view results → open QR modal
- Verify the page renders correctly in both light system preference and dark system preference (the page should always be light regardless of OS preference)
- Test mobile viewport (375px) stacks all sections vertically without horizontal scroll
