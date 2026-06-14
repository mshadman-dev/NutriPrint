"""
Food quantity → nutrient mapping for practical serving examples.
Used in printable reports, meal summaries, and nutrition gap UI.

All public functions now accept an optional `diet_pref` parameter so that
vegetarian users never see chicken, egg, or fish suggestions.
"""

from services.diet_filter import filter_food_servings, DIET_VEGETARIAN, ICMR_RDA

NUTRIENT_LABELS = {
    "protein_g": {"label": "Protein",        "unit": "g",  "icon": "💪"},
    "carbs_g":   {"label": "Carbohydrates",   "unit": "g",  "icon": "🍚"},
    "fat_g":     {"label": "Fats",            "unit": "g",  "icon": "🥑"},
    "fiber_g":   {"label": "Fiber",           "unit": "g",  "icon": "🌿"},
}

# ICMR fiber targets by age (not in ICMR_RDA dict)
FIBER_RDA  = {"5-8": 15, "9-12": 20, "13-15": 25}
# Estimated daily fat target (~30 % of calories)
FAT_RDA    = {"5-8": 45, "9-12": 57, "13-15": 70}
# Estimated daily carbs (~55 % of calories)
CARBS_RDA  = {"5-8": 185, "9-12": 233, "13-15": 288}


# ── helpers ────────────────────────────────────────────────────────────────────

def _suggest_combination(foods: list, target: float) -> list:
    """Greedy combination to reach ~target nutrient amount."""
    if target <= 0 or not foods:
        return []

    combo: list = []
    remaining = target
    sorted_foods = sorted(foods, key=lambda f: f["amount"], reverse=True)

    for food in sorted_foods:
        if remaining <= 0:
            break
        count = max(1, round(remaining / food["amount"]))
        count = min(count, 3)
        combo.append({
            "serving": food["serving"],
            "name":    food["name"],
            "icon":    food["icon"],
            "count":   count,
            "total":   round(count * food["amount"], 1),
        })
        remaining -= count * food["amount"]
        if len(combo) >= 3:
            break

    return combo


def get_nutrient_targets(age_group: str) -> dict:
    rda = ICMR_RDA.get(age_group, ICMR_RDA["9-12"])
    return {
        "protein_g": rda["protein_g"],
        "carbs_g":   CARBS_RDA.get(age_group, CARBS_RDA["9-12"]),
        "fat_g":     FAT_RDA.get(age_group, FAT_RDA["9-12"]),
        "fiber_g":   FIBER_RDA.get(age_group, FIBER_RDA["9-12"]),
    }


# ── public API ─────────────────────────────────────────────────────────────────

def get_food_equivalents(age_group: str, diet_pref: str = DIET_VEGETARIAN) -> list:
    """
    Return food-equivalent blocks for protein, carbs, fats, fiber.

    All items in the returned list are safe to display for the given diet.
    Vegetarian users will never see chicken, egg, or fish entries.
    """
    diet_pref = (diet_pref or DIET_VEGETARIAN).lower().strip()
    targets = get_nutrient_targets(age_group)
    results = []

    for key in ("protein_g", "carbs_g", "fat_g", "fiber_g"):
        # Pull only foods allowed for this diet
        foods  = filter_food_servings(key, diet_pref)
        target = targets[key]
        meta   = NUTRIENT_LABELS[key]

        # Put diet-specific foods (eggs for eggetarian, meat for nonveg) at the
        # front of the examples list so they're always visible.
        diet_specific = [f for f in foods if f.get("diet") != "all"]
        veg_foods     = [f for f in foods if f.get("diet") == "all"]
        ordered_foods = diet_specific + veg_foods

        examples = [
            {
                "serving": f["serving"],
                "name":    f["name"],
                "amount":  f["amount"],
                "icon":    f["icon"],
                "display": f"{f['serving']} = {f['amount']}{meta['unit']} {meta['label']}",
            }
            for f in ordered_foods[:5]
        ]

        combo = _suggest_combination(foods, target)

        results.append({
            "nutrient":       meta["label"],
            "key":            key,
            "unit":           meta["unit"],
            "icon":           meta["icon"],
            "target":         target,
            "examples":       examples,
            "suggested_combo": combo,
        })

    return results


def estimate_meal_macros(calories: float, protein_g: float) -> dict:
    """Estimate carbs and fat when not stored in meal data."""
    protein_cal = protein_g * 4
    remaining   = max(0, calories - protein_cal)
    carbs_g     = round(remaining * 0.55 / 4, 1)
    fat_g       = round(remaining * 0.45 / 9, 1)
    fiber_g     = round(carbs_g * 0.12, 1)
    return {"carbs_g": carbs_g, "fat_g": fat_g, "fiber_g": fiber_g}
