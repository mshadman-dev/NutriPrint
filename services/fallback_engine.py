import json
import random
from pathlib import Path
from models.schemas import MealPlan, MealDay, MealItem
from services.diet_filter import DAYS_KN
from services.allergen_map import get_excluded_keywords

# Load foods once at startup
FOODS_PATH = Path(__file__).parent.parent / "data" / "foods.json"
with open(FOODS_PATH, encoding="utf-8") as f:
    ALL_FOODS = json.load(f)

DAYS_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def _filter_foods(region, diet, meal_type, month):
    results = []
    for f in ALL_FOODS:
        if region not in f["regions"]:
            continue
        # diet matching: veg only gets veg; eggetarian gets veg+egg; nonveg gets all
        if diet == "vegetarian" and f["diet_type"] != "vegetarian":
            continue
        if diet == "eggetarian" and f["diet_type"] == "non-vegetarian":
            continue
        # non-vegetarian gets all types — no filter needed
        if meal_type not in f["meal_type"]:
            continue
        if "all" not in f["season_months"] and month.lower() not in f["season_months"]:
            continue
        results.append(f)
    return results

def _to_meal_item(f) -> MealItem:
    serving_size_g = f.get("serving_size_g", 100)
    factor = serving_size_g / 100.0

    calories = round(f["calories_per_100g"] * factor)
    protein_g = round(f["protein_g"] * factor, 2)
    calcium_mg = round(f["calcium_mg"] * factor, 1)
    iron_mg = round(f["iron_mg"] * factor, 2)

    # Scale optional per-100g fields if present
    carbs_g = round(f["carbs_g"] * factor, 2) if "carbs_g" in f else None
    fat_g = round(f["fat_g"] * factor, 2) if "fat_g" in f else None
    fiber_g = round(f["fiber_g"] * factor, 2) if "fiber_g" in f else None

    return MealItem(
        name_en       = f["name_en"],
        name_kn       = f["name_kn"],
        ingredients   = [f["name_en"]],  # simplified
        calories      = calories,
        protein_g     = protein_g,
        calcium_mg    = calcium_mg,
        iron_mg       = iron_mg,
        cost_inr      = f["cost_inr"],
        prep_time_min = f["prep_time_min"],
    )

def generate_fallback_plan(
    school_name      : str,
    student_name     : str,
    teacher_name     : str,
    age_group        : str,
    gender           : str,
    diet_pref        : str,
    region           : str,
    month            : str,
    strategy         : str,
    bmi_class        : str = None,
    allergies        : list = None,
    ai_recommendations: list = None,
) -> MealPlan:
    if ai_recommendations is None:
        ai_recommendations = []
    if allergies is None:
        allergies = []

    # Normalize allergy keywords for case-insensitive matching
    allergy_keywords = [a.strip().lower() for a in allergies if a.strip()]
    
    # Expand allergy keywords using allergen category mapping
    excluded_keywords = get_excluded_keywords(allergy_keywords)

    def _is_allergic(food: dict) -> bool:
        """
        Return True if this food should be excluded due to allergies.
        
        Uses expanded allergen categories to match ingredient keywords
        in food names and highlights. For example, a "milk" allergy
        will match "curd" and "yogurt".
        """
        if not excluded_keywords:
            return False
        
        combined_text = (
            food["name_en"] + " " +
            " ".join(food.get("highlights", []))
        ).lower()
        
        for kw in excluded_keywords:
            if kw in combined_text:
                return True
        return False

    def _get_pool(meal_type: str) -> list:
        """
        Return a filtered food pool for the given meal_type.
        Cascade: region+month → region+all → bare hardcoded item.
        """
        pool = [f for f in _filter_foods(region, diet_pref, meal_type, month)
                if not _is_allergic(f)]
        if not pool:
            # Try season-agnostic fallback
            pool = [f for f in _filter_foods(region, diet_pref, meal_type, "all")
                    if not _is_allergic(f)]
        return pool

    # Hardcoded last-resort items (one per meal_type) used only when the
    # filtered pool is completely empty even after the "all" cascade.
    _last_resort = {
        "breakfast": MealItem(
            name_en="Avalakki Upma", name_kn="ಅವಲಕ್ಕಿ ಉಪ್ಮಾ",
            ingredients=["Avalakki Upma"],
            calories=350, protein_g=9, calcium_mg=180, iron_mg=4,
            cost_inr=20, prep_time_min=15,
        ),
        "lunch": MealItem(
            name_en="Rice+Dal+Sabzi", name_kn="ಅನ್ನ+ದಾಲ್+ಸಬ್ಜಿ",
            ingredients=["Rice", "Dal", "Sabzi"],
            calories=600, protein_g=18, calcium_mg=300, iron_mg=8,
            cost_inr=35, prep_time_min=30,
        ),
        "dinner": MealItem(
            name_en="Chapati+Palya", name_kn="ಚಪಾತಿ+ಪಲ್ಯ",
            ingredients=["Chapati", "Palya"],
            calories=500, protein_g=14, calcium_mg=220, iron_mg=6,
            cost_inr=25, prep_time_min=25,
        ),
    }

    # Build per-meal-type pools once
    breakfast_pool = _get_pool("breakfast")
    lunch_pool     = _get_pool("lunch")
    dinner_pool    = _get_pool("dinner")

    # Track usage counts to enforce the "no item repeated more than twice" rule
    usage: dict[str, int] = {}

    def _pick(pool: list, meal_type: str) -> MealItem:
        """
        Pick a food from pool that has been used fewer than twice.
        Falls back to least-used item, then to last-resort sentinel.
        """
        if not pool:
            return _last_resort[meal_type]

        # Filter to items used < 2 times; if none left, allow least-used
        eligible = [f for f in pool if usage.get(f["name_en"], 0) < 2]
        if not eligible:
            eligible = sorted(pool, key=lambda f: usage.get(f["name_en"], 0))

        # Shuffle eligible set so days are varied
        random.shuffle(eligible)
        chosen = eligible[0]
        usage[chosen["name_en"]] = usage.get(chosen["name_en"], 0) + 1
        return _to_meal_item(chosen)

    # Assemble the 7-day week
    week = []
    for day_en in DAYS_EN:
        b = _pick(breakfast_pool, "breakfast")
        l = _pick(lunch_pool,     "lunch")
        d = _pick(dinner_pool,    "dinner")

        week.append(MealDay(
            day       = day_en,
            day_kn    = DAYS_KN.get(day_en, ""),
            breakfast = b,
            lunch     = l,
            dinner    = d,
        ))

    # ── Aggregate nutritional & cost stats from actual selected items ──────
    all_items = [day.breakfast for day in week] + \
                [day.lunch     for day in week] + \
                [day.dinner    for day in week]

    num_days      = len(DAYS_EN)          # 7
    total_cal     = sum(i.calories  for i in all_items)
    total_protein = sum(i.protein_g for i in all_items)
    total_calcium = sum(i.calcium_mg for i in all_items)
    total_iron    = sum(i.iron_mg    for i in all_items)
    total_cost    = sum(i.cost_inr   for i in all_items)

    avg_daily_cal  = total_cal     / num_days
    avg_protein_g  = total_protein / num_days
    avg_calcium_mg = total_calcium / num_days
    avg_iron_mg    = total_iron    / num_days

    return MealPlan(
        student_name      = student_name,
        school_name       = school_name,
        teacher_name      = teacher_name,
        age_group         = age_group,
        diet_pref         = diet_pref,
        region            = region,
        month             = month,
        strategy          = strategy,
        bmi_class         = bmi_class,
        allergies         = allergies,
        week              = week,
        avg_daily_cal     = round(avg_daily_cal,  1),
        avg_protein_g     = round(avg_protein_g,  1),
        avg_calcium_mg    = round(avg_calcium_mg, 1),
        avg_iron_mg       = round(avg_iron_mg,    2),
        total_cost_inr    = round(total_cost,     2),
        generated_by      = "fallback",
        ai_recommendations= ai_recommendations,
    )
