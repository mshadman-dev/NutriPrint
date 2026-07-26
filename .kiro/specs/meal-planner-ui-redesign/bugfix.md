# Bugfix Requirements Document

## Introduction

The Meal Planner page (`templates/meal_planner.html`) has multiple UI/UX layout and styling defects that make it look unprofessional for an engineering final-year project demonstration. The page uses a dark theme with a narrow fixed-width column layout, leaving over half the screen unused on desktop. The AI Nutrition Advisor panel is cramped, cards have inconsistent spacing, and the overall aesthetic is outdated compared to modern SaaS dashboards. This fix converts the page to a polished light theme with full-width responsive layout while preserving all existing functionality (no changes to JS logic, FastAPI endpoints, AI integration, or backend behaviour).

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the Meal Planner page is viewed on desktop THEN the system renders content in a narrow left column (`xl:grid-cols-[420px_1fr]`) leaving more than half the screen as empty dark space

1.2 WHEN the Meal Planner page loads THEN the system displays a dark theme (background `#060a0e`, surface `#0d1117`) that looks outdated and inconsistent with a modern SaaS presentation

1.3 WHEN the AI Nutrition Advisor panel is rendered THEN the system constrains it within the narrow 420px form column, making the question input, AI response, recommendation cards, and quick action buttons cramped and difficult to use

1.4 WHEN multiple card components are displayed on the page THEN the system renders them with inconsistent spacing, padding, sizing, and shadow styles

1.5 WHEN the page layout is rendered on desktop THEN the system uses `xl:grid-cols-[420px_1fr]` which fixes the form to a narrow column regardless of available viewport width, wasting horizontal space

1.6 WHEN the hero section, form card, and result area are rendered THEN the system applies dark-specific CSS variables and inline styles (dark backgrounds, light text, green neon accents) that conflict with a polished professional appearance

### Expected Behavior (Correct)

2.1 WHEN the Meal Planner page is viewed on desktop THEN the system SHALL use the full available desktop width with a balanced responsive layout (e.g., Student Details and AI Nutrition Advisor side by side, Generate button full-width, 7-Day Meal Plan full-width)

2.2 WHEN the Meal Planner page loads THEN the system SHALL display a clean light theme with white background (#FFFFFF), soft gray cards (#F8FAFC background), teal (#14B8A6) and navy (#0F172A) accents, consistent shadows and rounded corners

2.3 WHEN the AI Nutrition Advisor panel is rendered THEN the system SHALL allocate significantly more width so that the question input, AI response, recommendation cards, and quick action buttons are comfortably displayed without feeling cramped

2.4 WHEN multiple card components are displayed on the page THEN the system SHALL render them with consistent padding, margins, border-radius, shadows, and typography alignment throughout

2.5 WHEN the page layout is rendered on desktop THEN the system SHALL remove the fixed 420px column constraint and instead use a flexible grid that distributes space proportionally across the viewport

2.6 WHEN the hero section, form card, and result area are rendered THEN the system SHALL apply light-theme styling (white/gray backgrounds, dark text, teal/navy accents) that presents a polished startup SaaS dashboard suitable for a final-year project demonstration

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user fills in student details and clicks "Generate Meal Plan" THEN the system SHALL CONTINUE TO submit form data to the FastAPI backend and render the 7-day meal plan result via JavaScript (`meal.js`)

3.2 WHEN the AI Nutrition Advisor is used (question input, quick actions, recommendations) THEN the system SHALL CONTINUE TO function via the existing `advisor.js` logic rendering into `#advisorPanel`

3.3 WHEN the meal plan result is generated THEN the system SHALL CONTINUE TO display nutrition scores via `nutrition_score.js` and weekly summaries via `weekly_summary.js` without modification

3.4 WHEN any FastAPI endpoint is called (meal generation, AI advisor, etc.) THEN the system SHALL CONTINUE TO behave identically — no backend routes, response formats, or API logic shall be modified

3.5 WHEN the page is accessed without authentication THEN the system SHALL CONTINUE TO redirect to the login page using the existing inline auth-check script

3.6 WHEN the Recipe QR modal is triggered THEN the system SHALL CONTINUE TO display and function correctly with its existing JavaScript logic

3.7 WHEN CSS class names or element IDs referenced by JavaScript files (`advisor.js`, `meal.js`, `nutrition_score.js`, `weekly_summary.js`) are used THEN the system SHALL CONTINUE TO exist in the DOM so that JS selectors (e.g., `#advisorPanel`, `#mealResult`, `#generateBtn`, `#formError`, `#mealLoading`, `#mealPlaceholder`) resolve correctly

3.8 WHEN the page is viewed on mobile or tablet THEN the system SHALL CONTINUE TO be responsive and usable, stacking sections vertically as appropriate

3.9 WHEN the user interacts with the page THEN the system SHALL CONTINUE TO present the workflow in the same order: Student Details → AI Nutrition Advisor → Generate Meal Plan → Results

3.10 WHEN buttons and labels are displayed (e.g., "Generate Meal Plan with Selected AI Advice", "Start Planning", "Browse Foods") THEN the system SHALL CONTINUE TO show the same text content so the presentation and speaking script remains consistent

3.11 WHEN HTML IDs or classes referenced by `meal.js` or `advisor.js` are present THEN the system SHALL NOT rename or remove them — only structural/wrapper HTML and CSS styling may change
