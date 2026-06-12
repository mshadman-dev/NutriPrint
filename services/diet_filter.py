"""
Centralised diet-filtering rules for NutriPrint.

All modules must import from here so the rules stay in one place.
"""

from __future__ import annotations

# ── Canonical diet categories ──────────────────────────────────────────────────
DIET_VEGETARIAN   = "vegetarian"
DIET_EGGETARIAN   = "eggetarian"
DIET_NONVEG       = "non-vegetarian"

# ── Non-veg keyword sets used to detect violations ────────────────────────────
_MEAT_KEYWORDS = {
    "chicken", "koli", "fish", "meen", "mutton", "meat",
    "prawn", "shrimp", "seafood", "crab", "lamb", "pork", "beef",
}
_EGG_KEYWORDS = {"egg", "mutte", "omelette", "omelet"}

# All non-veg keywords (meat + egg)
_NONVEG_KEYWORDS = _MEAT_KEYWORDS | _EGG_KEYWORDS


def _name_contains(name: str, keywords: set) -> bool:
    lower = name.lower()
    return any(kw in lower for kw in keywords)


def is_nonveg_item(name: str) -> bool:
    """Return True if the food name clearly contains meat/seafood/egg."""
    return _name_contains(name, _NONVEG_KEYWORDS)


def is_meat_item(name: str) -> bool:
    """Return True if the food name contains meat or seafood (not egg)."""
    return _name_contains(name, _MEAT_KEYWORDS)


def is_egg_item(name: str) -> bool:
    """Return True if the food name refers to egg/egg-based dishes."""
    return _name_contains(name, _EGG_KEYWORDS)


def is_allowed_for_diet(name: str, diet: str) -> bool:
    """
    Return True if this food name is allowed under the given diet.

    vegetarian  → no eggs, no meat, no seafood
    eggetarian  → eggs allowed, no meat, no seafood
    non-vegetarian → everything allowed
    """
    diet = (diet or "").lower().strip()
    if diet == DIET_NONVEG:
        return True
    if diet == DIET_EGGETARIAN:
        return not is_meat_item(name)
    # default: vegetarian
    return not is_nonveg_item(name)


# ── Per-nutrient food pools, tagged by diet compatibility ─────────────────────
#
# Each entry carries:
#   name     – display name
#   serving  – human-readable portion
#   amount   – nutrient amount for that portion
#   icon     – slug for SVG icon
#   diet     – which diets allow this item
#              "all"  → veg + egg + nonveg
#              "egg"  → eggetarian + nonveg only
#              "nonveg" → nonveg only

FOOD_SERVINGS_ALL = {
    "protein_g": [
        # vegetarian sources
        {"name": "Toor Dal",         "serving": "1 Cup Dal",            "amount": 18, "icon": "dal",        "diet": "all"},
        {"name": "Paneer",           "serving": "100g Paneer",          "amount": 18, "icon": "paneer",     "diet": "all"},
        {"name": "Moong Sprouts",    "serving": "1 Cup Sprouts",        "amount":  7, "icon": "vegetables", "diet": "all"},
        {"name": "Rajma",            "serving": "1 Cup Rajma",          "amount": 15, "icon": "dal",        "diet": "all"},
        {"name": "Horsegram Dal",    "serving": "1 Cup Horsegram",      "amount": 22, "icon": "dal",        "diet": "all"},
        {"name": "Full Cream Milk",  "serving": "1 Cup Milk",           "amount":  8, "icon": "milk",       "diet": "all"},
        {"name": "Curd",             "serving": "1 Cup Curd",           "amount":  7, "icon": "milk",       "diet": "all"},
        {"name": "Groundnuts",       "serving": "30g Groundnuts",       "amount":  8, "icon": "nuts",       "diet": "all"},
        {"name": "Soy Chunks",       "serving": "30g Soy Chunks",       "amount": 14, "icon": "dal",        "diet": "all"},
        # eggetarian sources
        {"name": "Egg",              "serving": "1 Egg",                "amount":  6, "icon": "egg",        "diet": "egg"},
        {"name": "Boiled Egg",       "serving": "2 Boiled Eggs",        "amount": 12, "icon": "egg",        "diet": "egg"},
        # non-veg sources
        {"name": "Chicken Breast",   "serving": "100g Chicken Breast",  "amount": 31, "icon": "chicken",   "diet": "nonveg"},
        {"name": "Fish",             "serving": "100g Fish",            "amount": 22, "icon": "fish",       "diet": "nonveg"},
    ],
    "carbs_g": [
        {"name": "Rice",             "serving": "1 Cup Rice",           "amount": 45, "icon": "rice",       "diet": "all"},
        {"name": "Chapati",          "serving": "2 Chapati",            "amount": 30, "icon": "rice",       "diet": "all"},
        {"name": "Ragi Mudde",       "serving": "1 Ragi Mudde",         "amount": 35, "icon": "rice",       "diet": "all"},
        {"name": "Banana",           "serving": "1 Banana",             "amount": 27, "icon": "fruits",     "diet": "all"},
        {"name": "Jowar Roti",       "serving": "2 Jowar Roti",         "amount": 40, "icon": "rice",       "diet": "all"},
    ],
    "fat_g": [
        {"name": "Groundnuts",       "serving": "30g Nuts",             "amount": 15, "icon": "nuts",       "diet": "all"},
        {"name": "Ghee",             "serving": "1 tbsp Ghee",          "amount": 14, "icon": "milk",       "diet": "all"},
        {"name": "Coconut",          "serving": "2 tbsp Coconut",       "amount": 10, "icon": "fruits",     "diet": "all"},
        {"name": "Paneer",           "serving": "100g Paneer",          "amount": 20, "icon": "paneer",     "diet": "all"},
        {"name": "Full Cream Milk",  "serving": "1 Cup Milk",           "amount":  8, "icon": "milk",       "diet": "all"},
    ],
    "fiber_g": [
        {"name": "Ragi",             "serving": "1 Ragi Mudde",         "amount":  4, "icon": "rice",       "diet": "all"},
        {"name": "Vegetables",       "serving": "1 Cup Mixed Veg",      "amount":  5, "icon": "vegetables", "diet": "all"},
        {"name": "Fruits",           "serving": "1 Apple/Banana",       "amount":  3, "icon": "fruits",     "diet": "all"},
        {"name": "Dal",              "serving": "1 Cup Dal",            "amount":  8, "icon": "dal",        "diet": "all"},
        {"name": "Jowar Roti",       "serving": "2 Jowar Roti",         "amount":  4, "icon": "rice",       "diet": "all"},
    ],
}

# ── Fix-food suggestions per nutrient gap, keyed by diet ──────────────────────

_FIX_FOODS_BY_DIET = {
    "protein_g": {
        DIET_VEGETARIAN: {
            "en": "Horsegram Saaru, Sprouted Moong, Paneer Sabzi, Avarekalu Saaru, Rajma",
            "kn": "ಹುರಳಿ ಸಾರು, ಮೊಳಕೆ ಹೆಸರುಕಾಳು, ಪನೀರ್ ಸಬ್ಜಿ, ಅವರೆಕಾಳು ಸಾರು, ರಾಜ್ಮಾ",
        },
        DIET_EGGETARIAN: {
            "en": "Horsegram Saaru, Boiled Egg, Sprouted Moong, Egg Curry, Paneer Sabzi",
            "kn": "ಹುರಳಿ ಸಾರು, ಮೊಟ್ಟೆ ಬೇಯಿಸಿ, ಮೊಳಕೆ ಹೆಸರುಕಾಳು, ಮೊಟ್ಟೆ ಸಾಲನ್, ಪನೀರ್",
        },
        DIET_NONVEG: {
            "en": "Horsegram Saaru, Egg Curry, Chicken Saaru, Fish Curry, Sprouted Moong",
            "kn": "ಹುರಳಿ ಸಾರು, ಮೊಟ್ಟೆ ಸಾಲನ್, ಕೋಳಿ ಸಾರು, ಮೀನು ಸಾಲನ್, ಮೊಳಕೆ ಹೆಸರುಕಾಳು",
        },
    },
    "calories": {
        DIET_VEGETARIAN: {
            "en": "Ragi Mudde, Groundnut Laddu, Ghee Rice, Banana Sheera",
            "kn": "ರಾಗಿ ಮುದ್ದೆ, ಕಡಲೆಕಾಯಿ ಉಂಡೆ, ತುಪ್ಪದ ಅನ್ನ, ಬಾಳೆಹಣ್ಣಿನ ಶಿರಾ",
        },
        DIET_EGGETARIAN: {
            "en": "Ragi Mudde, Groundnut Laddu, Ghee Rice, Egg Sheera, Banana Sheera",
            "kn": "ರಾಗಿ ಮುದ್ದೆ, ಕಡಲೆಕಾಯಿ ಉಂಡೆ, ತುಪ್ಪದ ಅನ್ನ, ಮೊಟ್ಟೆ ಶಿರಾ, ಬಾಳೆಹಣ್ಣಿನ ಶಿರಾ",
        },
        DIET_NONVEG: {
            "en": "Ragi Mudde, Groundnut Laddu, Ghee Rice, Egg Sheera, Chicken Rice",
            "kn": "ರಾಗಿ ಮುದ್ದೆ, ಕಡಲೆಕಾಯಿ ಉಂಡೆ, ತುಪ್ಪದ ಅನ್ನ, ಮೊಟ್ಟೆ ಶಿರಾ, ಕೋಳಿ ಅನ್ನ",
        },
    },
    "calcium_mg": {
        # Calcium sources are all vegetarian — same for all diets
        DIET_VEGETARIAN: {
            "en": "Drumstick Leaves, Ragi Dosa, Curd Rice, Ragi Malt",
            "kn": "ನುಗ್ಗೆ ಸೊಪ್ಪು, ರಾಗಿ ದೋಸೆ, ಮೊಸರು ಅನ್ನ, ರಾಗಿ ಮಾಲ್ಟ್",
        },
        DIET_EGGETARIAN: {
            "en": "Drumstick Leaves, Ragi Dosa, Curd Rice, Ragi Malt",
            "kn": "ನುಗ್ಗೆ ಸೊಪ್ಪು, ರಾಗಿ ದೋಸೆ, ಮೊಸರು ಅನ್ನ, ರಾಗಿ ಮಾಲ್ಟ್",
        },
        DIET_NONVEG: {
            "en": "Drumstick Leaves, Ragi Dosa, Curd Rice, Ragi Malt, Fish (calcium-rich)",
            "kn": "ನುಗ್ಗೆ ಸೊಪ್ಪು, ರಾಗಿ ದೋಸೆ, ಮೊಸರು ಅನ್ನ, ರಾಗಿ ಮಾಲ್ಟ್, ಮೀನು",
        },
    },
    "iron_mg": {
        DIET_VEGETARIAN: {
            "en": "Banana Flower Curry, Palak Dal, Methi Paratha, Dill Leaves Dal",
            "kn": "ಬಾಳೆ ಹೂವಿನ ಪಲ್ಯ, ಪಾಲಕ್ ಬೇಳೆ, ಮೆಂತ್ಯ ಪರಾಠ, ಸಬ್ಬಸಿಗೆ ಸೊಪ್ಪು ಬೇಳೆ",
        },
        DIET_EGGETARIAN: {
            "en": "Banana Flower Curry, Palak Dal, Methi Paratha, Boiled Egg with Spinach",
            "kn": "ಬಾಳೆ ಹೂವಿನ ಪಲ್ಯ, ಪಾಲಕ್ ಬೇಳೆ, ಮೆಂತ್ಯ ಪರಾಠ, ಮೊಟ್ಟೆ ಪಾಲಕ್",
        },
        DIET_NONVEG: {
            "en": "Banana Flower Curry, Palak Dal, Methi Paratha, Chicken Liver, Fish Curry",
            "kn": "ಬಾಳೆ ಹೂವಿನ ಪಲ್ಯ, ಪಾಲಕ್ ಬೇಳೆ, ಮೆಂತ್ಯ ಪರಾಠ, ಕೋಳಿ ಯಕೃತ್, ಮೀನು ಸಾಲನ್",
        },
    },
}


def get_fix_foods(nutrient_key: str, diet: str) -> dict:
    """
    Return {en, kn} fix-food suggestion for a nutrient deficiency, respecting diet.
    Falls back to vegetarian if the diet is not recognised.
    """
    diet = (diet or DIET_VEGETARIAN).lower().strip()
    pool = _FIX_FOODS_BY_DIET.get(nutrient_key, {})
    if diet not in pool:
        diet = DIET_VEGETARIAN
    return pool.get(diet, {"en": "", "kn": ""})


def filter_food_servings(nutrient_key: str, diet: str) -> list:
    """
    Return the food-serving entries allowed for the given diet and nutrient.
    Returned list is always safe to show without further filtering.
    """
    diet = (diet or DIET_VEGETARIAN).lower().strip()
    all_foods = FOOD_SERVINGS_ALL.get(nutrient_key, [])

    allowed = []
    for f in all_foods:
        food_diet = f.get("diet", "all")
        if food_diet == "all":
            allowed.append(f)
        elif food_diet == "egg" and diet in (DIET_EGGETARIAN, DIET_NONVEG):
            allowed.append(f)
        elif food_diet == "nonveg" and diet == DIET_NONVEG:
            allowed.append(f)

    return allowed


# ── Strategy note injection ────────────────────────────────────────────────────

_STRATEGY_NOTES_BY_DIET = {
    "high_protein": {
        DIET_VEGETARIAN:
            "Prioritize high-protein vegetarian foods: horsegram, paneer, moong dal, "
            "rajma, sprouted legumes, groundnuts, soy chunks. Every meal must exceed 8g protein. "
            "NO eggs, chicken, fish, or meat.",
        DIET_EGGETARIAN:
            "Prioritize high-protein foods: eggs, horsegram, paneer, moong dal, rajma. "
            "Every meal must exceed 8g protein. NO chicken, fish, or meat.",
        DIET_NONVEG:
            "Prioritize high-protein foods: chicken, eggs, fish, horsegram, paneer, moong dal. "
            "Every meal must exceed 8g protein.",
    },
    "calcium_iron": {
        DIET_VEGETARIAN:
            "Prioritize calcium and iron rich vegetarian foods: Ragi Mudde, Drumstick leaves, "
            "Palak Dal, Banana flower, Methi Paratha, Curd Rice. Critical for anaemia prevention. "
            "NO eggs, chicken, fish, or meat.",
        DIET_EGGETARIAN:
            "Prioritize calcium and iron rich foods: Ragi Mudde, Drumstick leaves, Palak Dal, "
            "Banana flower, Boiled Egg. Critical for anaemia prevention. NO chicken, fish, or meat.",
        DIET_NONVEG:
            "Prioritize calcium and iron rich foods: Ragi Mudde, Drumstick leaves, Palak Dal, "
            "Banana flower, Boiled Egg, Fish Curry. Critical for anaemia prevention.",
    },
    "standard": {
        DIET_VEGETARIAN:  "Balanced macros following ICMR RDA. Vegetarian foods only.",
        DIET_EGGETARIAN:  "Balanced macros following ICMR RDA. Eggs are allowed.",
        DIET_NONVEG:      "Balanced macros following ICMR RDA.",
    },
    "calorie_control": {
        DIET_VEGETARIAN:
            "Use low-calorie high-fiber foods. Avoid ghee-heavy or fried items. "
            "Max 400 cal per meal. Vegetarian foods only.",
        DIET_EGGETARIAN:
            "Use low-calorie high-fiber foods. Avoid ghee-heavy or fried items. "
            "Max 400 cal per meal. Eggs are allowed.",
        DIET_NONVEG:
            "Use low-calorie high-fiber foods. Avoid ghee-heavy or fried items. "
            "Max 400 cal per meal.",
    },
}


def get_strategy_note(strategy: str, diet: str) -> str:
    """Return the strategy description appropriate for the given diet."""
    diet = (diet or DIET_VEGETARIAN).lower().strip()
    pool = _STRATEGY_NOTES_BY_DIET.get(strategy, {})
    return pool.get(diet, pool.get(DIET_VEGETARIAN, "Balanced macros following ICMR RDA."))


# ── Meal-item diet validator / auto-replacer ───────────────────────────────────

# Vegetarian substitution map: non-veg item keyword → veg replacement display name
_VEG_SUBSTITUTIONS = {
    "chicken":    "Horsegram Saaru (ಹುರಳಿ ಸಾರು)",
    "koli":       "Horsegram Saaru (ಹುರಳಿ ಸಾರು)",
    "fish":       "Palak Dal (ಪಾಲಕ್ ಬೇಳೆ)",
    "meen":       "Palak Dal (ಪಾಲಕ್ ಬೇಳೆ)",
    "prawn":      "Avarekalu Saaru (ಅವರೆಕಾಳು ಸಾರು)",
    "shrimp":     "Avarekalu Saaru (ಅವರೆಕಾಳು ಸಾರು)",
    "mutton":     "Rajma Curry (ರಾಜ್ಮಾ ಕರಿ)",
    "meat":       "Rajma Curry (ರಾಜ್ಮಾ ಕರಿ)",
    "egg":        "Paneer Bhurji (ಪನೀರ್ ಭುರ್ಜಿ)",
    "mutte":      "Paneer Bhurji (ಪನೀರ್ ಭುರ್ಜಿ)",
    "omelette":   "Paneer Bhurji (ಪನೀರ್ ಭುರ್ಜಿ)",
    "omelet":     "Paneer Bhurji (ಪನೀರ್ ಭುರ್ಜಿ)",
}

# Eggetarian substitution map: only meat → veg replacement (eggs stay)
_EGG_SUBSTITUTIONS = {
    "chicken":  "Egg Curry (ಮೊಟ್ಟೆ ಸಾಲನ್)",
    "koli":     "Egg Curry (ಮೊಟ್ಟೆ ಸಾಲನ್)",
    "fish":     "Boiled Egg with Palak Dal (ಮೊಟ್ಟೆ ಪಾಲಕ್ ಬೇಳೆ)",
    "meen":     "Boiled Egg with Palak Dal (ಮೊಟ್ಟೆ ಪಾಲಕ್ ಬೇಳೆ)",
    "prawn":    "Egg Bhurji (ಮೊಟ್ಟೆ ಭುರ್ಜಿ)",
    "shrimp":   "Egg Bhurji (ಮೊಟ್ಟೆ ಭುರ್ಜಿ)",
    "mutton":   "Egg Masala (ಮೊಟ್ಟೆ ಮಸಾಲ)",
    "meat":     "Egg Masala (ಮೊಟ್ಟೆ ಮಸಾಲ)",
}


def _find_substitution(name: str, sub_map: dict) -> str | None:
    lower = name.lower()
    for kw, replacement in sub_map.items():
        if kw in lower:
            return replacement
    return None


def enforce_diet_on_item(item_name: str, diet: str) -> tuple[bool, str]:
    """
    Check whether item_name is allowed for diet.
    Returns (is_valid, replacement_name).
    If valid: replacement_name == item_name.
    If invalid: replacement_name is the suggested substitute.
    """
    diet = (diet or DIET_VEGETARIAN).lower().strip()

    if is_allowed_for_diet(item_name, diet):
        return True, item_name

    if diet == DIET_VEGETARIAN:
        replacement = _find_substitution(item_name, _VEG_SUBSTITUTIONS)
    elif diet == DIET_EGGETARIAN:
        replacement = _find_substitution(item_name, _EGG_SUBSTITUTIONS)
    else:
        return True, item_name  # non-veg: everything allowed

    return False, replacement or "Mixed Vegetable Curry (ತರಕಾರಿ ಸಾಲನ್)"


def validate_and_fix_plan(plan_data: dict, diet: str) -> tuple[dict, list[str]]:
    """
    Walk every meal in plan_data["week"] and replace any item that violates
    the diet preference.  Returns (fixed_plan_data, list_of_violation_messages).
    Non-destructive — returns a shallow copy with the week list replaced.
    """
    violations: list[str] = []
    new_week = []

    for day in plan_data.get("week", []):
        new_day = dict(day)
        for slot in ("breakfast", "lunch", "dinner"):
            meal = day.get(slot, {})
            if not meal:
                continue
            name = meal.get("name_en", "")
            valid, replacement = enforce_diet_on_item(name, diet)
            if not valid:
                violations.append(
                    f"{day.get('day','?')} {slot}: '{name}' → replaced with '{replacement}'"
                )
                meal = dict(meal)
                meal["name_en"] = replacement
                # Clear name_kn since it no longer matches; caller can re-look up
                meal["name_kn"] = ""
                new_day = dict(new_day)
                new_day[slot] = meal
        new_week.append(new_day)

    new_plan = dict(plan_data)
    new_plan["week"] = new_week
    return new_plan, violations
