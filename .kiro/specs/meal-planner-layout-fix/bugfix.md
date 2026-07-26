# Bugfix Requirements Document

## Introduction

The Meal Planner page (`/meal-planner`) has significant UI/UX issues on desktop: a dark theme inconsistent with the rest of the application's light design system, a cramped single-column layout that wastes available screen width, and an AI Nutrition Advisor section that is too narrow to use comfortably. This fix addresses layout, theming, and spacing to bring the page in line with the polished light SaaS aesthetic used throughout the rest of NutriPrint.

**Scope:** HTML structure and CSS only. No changes to FastAPI endpoints, JavaScript logic, AI integration, meal generation, or backend behaviour.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the Meal Planner page is rendered on desktop THEN the system displays a dark theme (backgrounds `#060a0e`, `#0d1117`, green-on-black accents) that conflicts with the application-wide light theme defined in `base.css` (`--color-bg: #F8FAFC`, `--color-surface: #FFFFFF`, teal/navy accents)

1.2 WHEN the Meal Planner page is rendered on desktop (≥1280px) THEN the system constrains the form to a fixed 420px left column (`xl:grid-cols-[420px_1fr]`) while the right column remains mostly empty placeholder content, wasting available viewport width

1.3 WHEN the AI Nutrition Advisor section is rendered THEN the system places it inside the narrow 420px form column, making the chat input, AI response messages, recommendation cards, and quick-action buttons cramped and difficult to read or interact with

1.4 WHEN cards and sections are rendered on the Meal Planner page THEN the system applies inconsistent spacing, padding, border-radius, and shadow values that differ from the design-system tokens used on other pages (e.g., `var(--shadow-card)`, `var(--radius-card)`)

1.5 WHEN the Meal Planner hero section is rendered THEN the system uses a dark radial-gradient background with neon green text that visually clashes with the soft gradient hero banners on other pages

### Expected Behavior (Correct)

2.1 WHEN the Meal Planner page is rendered on desktop THEN the system SHALL use the application's light theme: white background (`#FFFFFF` / `--color-surface`), soft gray cards (`#F8FAFC`), teal accent (`#14B8A6`), navy text (`#0F172A`), and consistent shadows and rounded corners matching `base.css` design tokens

2.2 WHEN the Meal Planner page is rendered on desktop (≥1280px) THEN the system SHALL use the full available width with a responsive two-column layout placing Student Details and AI Nutrition Advisor side by side in the top section, and a full-width meal plan results area below

2.3 WHEN the AI Nutrition Advisor section is rendered THEN the system SHALL occupy significantly more horizontal space (at least 55-60% of the available width on desktop) to comfortably display the question input, AI response chat area, recommendation cards, and quick-action buttons without cramping

2.4 WHEN cards and sections are rendered on the Meal Planner page THEN the system SHALL use consistent padding (`--space-5` to `--space-7`), margins, border-radius (`--radius-card`), and box-shadow (`--shadow-card`) values from the shared design-system tokens

2.5 WHEN the Meal Planner hero section is rendered THEN the system SHALL use a gradient style consistent with the rest of the application (e.g., `linear-gradient(135deg, --color-primary, --color-accent)`) with white/light text, matching the hero banner pattern on other NutriPrint pages

### Unchanged Behavior (Regression Prevention)

3.1 WHEN a user fills in the student details form and clicks "Generate Meal Plan" THEN the system SHALL CONTINUE TO call the `/api/meal/generate` endpoint with the same payload structure and display the returned meal plan

3.2 WHEN a user interacts with the AI Nutrition Advisor (typing questions, selecting quick actions, viewing recommendations) THEN the system SHALL CONTINUE TO function identically — sending requests to `/api/ai-advisor/chat` and rendering responses correctly

3.3 WHEN the meal plan is generated and displayed THEN the system SHALL CONTINUE TO show the weekly summary, nutrition score, day cards, share/print actions, and recipe QR modals with full functionality

3.4 WHEN the page is viewed on mobile or tablet (< 1024px) THEN the system SHALL CONTINUE TO stack sections vertically in a single-column responsive layout

3.5 WHEN form validation errors occur (missing school name, invalid height/weight) THEN the system SHALL CONTINUE TO display inline error messages and prevent form submission

3.6 WHEN a user navigates to the page with a `?plan=<token>` URL parameter THEN the system SHALL CONTINUE TO restore the saved meal plan via the share token lookup
