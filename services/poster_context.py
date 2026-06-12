"""
Shared template context helpers for poster and report pages.
Diet preference is now threaded through every helper so that
vegetarian/eggetarian users never see non-compliant food suggestions.
"""

from services.bmi_calculator import (
    calculate_nutrition_gap, ICMR_RDA, ADVICE as BMI_ADVICE,
)
from services.food_equivalents import get_food_equivalents, estimate_meal_macros
from services.food_images import get_food_icon, NUTRIENT_ICONS
from services.diet_filter import DIET_VEGETARIAN, validate_and_fix_plan


def build_poster_context(plan, share_token: str, base_url: str) -> dict:
    try:
        plan_data = plan.model_dump()
    except AttributeError:
        plan_data = plan.dict()

    age_group = plan_data.get("age_group", "9-12")
    diet_pref = (plan_data.get("diet_pref") or DIET_VEGETARIAN).lower().strip()

    # ── Diet safety net ───────────────────────────────────────────────────────
    plan_data, violations = validate_and_fix_plan(plan_data, diet_pref)
    if violations:
        print(
            f"[poster_context] Diet violations fixed for "
            f"{plan_data.get('student_name','?')} ({diet_pref}): {violations}"
        )

    # ── Nutrition gap with diet-appropriate fix suggestions ───────────────────
    gaps = calculate_nutrition_gap(plan_data, age_group, diet_pref)

    # ── Food equivalents with diet filtering ──────────────────────────────────
    equivalents = get_food_equivalents(age_group, diet_pref)

    # ── BMI advice text (for health report) ───────────────────────────────────
    bmi_class = plan_data.get("bmi_class") or ""
    bmi_advice = BMI_ADVICE.get(bmi_class, {})

    # ── AI recommendations by destination ────────────────────────────────────
    ai_recommendations = plan_data.get("ai_recommendations") or []

    def by_destination(destination: str, limit=None):
        items = [
            rec for rec in ai_recommendations
            if destination in (rec.get("destinations") or [])
        ]
        return items[:limit] if limit else items

    # ── Template helper functions ─────────────────────────────────────────────
    def food_icon_lookup(name):
        return get_food_icon(name)

    def meal_macros(meal):
        if hasattr(meal, "model_dump"):
            m = meal.model_dump()
        elif isinstance(meal, dict):
            m = meal
        else:
            m = dict(meal)
        return estimate_meal_macros(m.get("calories", 0), m.get("protein_g", 0))

    # Rebuild plan object if any items were replaced for diet compliance
    if violations:
        try:
            from models.schemas import MealPlan
            plan = MealPlan(**plan_data)
        except Exception:
            pass  # keep original plan object if rebuild fails

    return {
        "plan":                      plan,
        "share_token":               share_token,
        "base_url":                  base_url,
        "nutrition_gaps":            gaps,
        "food_equivalents":          equivalents,
        "nutrient_icons":            NUTRIENT_ICONS,
        "icmr_rda":                  ICMR_RDA.get(age_group, ICMR_RDA["9-12"]),
        "bmi_advice":                bmi_advice,
        "food_icon_lookup":          food_icon_lookup,
        "meal_macros":               meal_macros,
        "ai_report_recommendations": by_destination("report"),
        "ai_parent_recommendations": by_destination("parent"),
        "ai_poster_recommendations": by_destination("poster", 5),
    }
