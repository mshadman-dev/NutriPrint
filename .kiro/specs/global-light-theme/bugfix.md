# Bugfix Requirements Document

## Introduction

The NutriPrint application currently renders with a dark theme (dark backgrounds, light text, dark surface colors) across all pages due to inline styles in `base.html` and dark CSS variables in `design-system.css` overriding the well-designed light theme tokens already defined in `base.css`. This makes the application look unprofessional and inconsistent with the project's presentation materials. The fix requires converting the entire UI to a clean, modern light theme while preserving all existing layouts, functionality, JavaScript logic, API endpoints, and backend code.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the application renders any page THEN the system displays a dark background (#060a0e) and light text (#E2E8F0) due to inline styles in base.html overriding the light theme tokens in base.css

1.2 WHEN the header/navigation bar renders THEN the system displays a dark glass-morphism background (rgba(6,10,14,0.88)) with dark borders (#1a2332) that is inconsistent with a professional light theme

1.3 WHEN the mobile navigation menu is toggled THEN the system displays a dark background (#0d1117) with dark borders (#1a2332)

1.4 WHEN design-system.css loads THEN the system sets dark CSS variables (--background: #131313, --surface: #0d1117, --surface-light: #161b22, --text: #e2e8f0) that override the light tokens in base.css

1.5 WHEN the Meal Planner page renders THEN the system displays dark-themed inline styles (--bg: #060a0e, --surface: #0d1117) for form cards, inputs, placeholders, and result overrides

1.6 WHEN the AI Advisor component renders THEN the system uses dark design-system.css variables for surfaces, borders, text, and card backgrounds, making the advisor appear dark

1.7 WHEN card components (.shell-card, .soft-card, .metric-card) render within page templates THEN the system applies glass-morphism and light backgrounds that conflict visually with the dark page background, creating an inconsistent appearance

1.8 WHEN the footer renders THEN the system inherits the dark body background and uses dark-specific styling

1.9 WHEN individual page templates (BMI, Food Catalog, Dashboard, About, Login) render their inline style blocks THEN the system applies dark-specific colors, backgrounds, and borders that override base.css light tokens

### Expected Behavior (Correct)

2.1 WHEN the application renders any page THEN the system SHALL display a white/light gray background (#FFFFFF / #F8FAFC) with dark readable text (#0F172A) using the light theme tokens already defined in base.css

2.2 WHEN the header/navigation bar renders THEN the system SHALL display a clean white/translucent-white background (rgba(255,255,255,0.92)) with subtle light borders, matching the .site-header styles defined in base.css

2.3 WHEN the mobile navigation menu is toggled THEN the system SHALL display a light background with subtle borders consistent with the light theme

2.4 WHEN design-system.css loads THEN the system SHALL set CSS variables that align with the light theme (light backgrounds, dark text, subtle borders) instead of dark values

2.5 WHEN the Meal Planner page renders THEN the system SHALL use light-themed colors for form cards (white/soft gray backgrounds), inputs (light backgrounds with subtle borders), and result areas consistent with the global light theme

2.6 WHEN the AI Advisor component renders THEN the system SHALL use light-themed variables for surfaces (white), borders (subtle gray), and text (dark), making the advisor consistent with the overall light theme

2.7 WHEN card components (.shell-card, .soft-card, .metric-card) render THEN the system SHALL display white surface backgrounds with subtle gray borders and soft shadows on a light page background, appearing cohesive and professional

2.8 WHEN the footer renders THEN the system SHALL display a light-themed footer with appropriate contrast and readability

2.9 WHEN individual page templates render THEN the system SHALL use light-themed colors in any inline style blocks, or the inline dark overrides SHALL be removed so that base.css light tokens take effect

### Unchanged Behavior (Regression Prevention)

3.1 WHEN any JavaScript file executes THEN the system SHALL CONTINUE TO function identically — no JS files shall be modified

3.2 WHEN any FastAPI endpoint is called THEN the system SHALL CONTINUE TO return the same responses — no backend code shall be modified

3.3 WHEN any API call is made from the frontend THEN the system SHALL CONTINUE TO use the same URLs, parameters, and request formats

3.4 WHEN any page layout is rendered THEN the system SHALL CONTINUE TO use the same grid structures, flex layouts, spacing, and element positioning

3.5 WHEN the splash screen renders THEN the system SHALL CONTINUE TO display its gradient loading animation (the splash screen gradient is acceptable as a loading state)

3.6 WHEN BMI badge classifications are displayed THEN the system SHALL CONTINUE TO use the same color-coded badge styles (blue for underweight, green for normal, orange for overweight, red for obese)

3.7 WHEN user authentication workflows execute THEN the system SHALL CONTINUE TO function identically (login, logout, session management, route protection)

3.8 WHEN the Meal Planner form validation and generation workflow executes THEN the system SHALL CONTINUE TO validate inputs and generate meal plans identically

3.9 WHEN the AI Advisor chat functionality is used THEN the system SHALL CONTINUE TO send/receive messages, display recommendations, and allow selection identically

3.10 WHEN the Food Catalog filter chips and search functionality are used THEN the system SHALL CONTINUE TO filter and display food cards identically

3.11 WHEN hero banner sections with gradient backgrounds render THEN the system SHALL CONTINUE TO display their branded gradient styles (these are accent elements, not page backgrounds)

---

## Bug Condition (Formal)

```pascal
FUNCTION isBugCondition(X)
  INPUT: X of type PageRenderContext
  OUTPUT: boolean
  
  // Returns true when the page rendering is affected by dark theme overrides
  RETURN X.hasInlineDarkStyles OR X.usesDesignSystemDarkVariables OR X.hasTemplateDarkOverrides
END FUNCTION
```

## Property Specification

```pascal
// Property: Fix Checking — Light Theme Rendering
FOR ALL X WHERE isBugCondition(X) DO
  result ← renderPage'(X)
  ASSERT result.bodyBackground IN {#FFFFFF, #F8FAFC}
    AND result.textColor = #0F172A
    AND result.surfaceColor = #FFFFFF
    AND result.headerBackground = rgba(255,255,255,0.92)
    AND result.cardBackgrounds = #FFFFFF
    AND result.borders ARE subtle gray (not dark)
END FOR
```

## Preservation Goal

```pascal
// Property: Preservation Checking — Functionality Unchanged
FOR ALL X WHERE NOT isBugCondition(X) DO
  ASSERT F(X) = F'(X)
END FOR

// Specifically:
// - All JavaScript behavior is identical
// - All API responses are identical
// - All page layouts/grids are identical
// - All user workflows are identical
// - Splash screen gradient is preserved
// - Hero banner gradients are preserved
// - Badge color semantics are preserved
```
