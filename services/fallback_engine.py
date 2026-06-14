import json
import random
from pathlib import Path
from models.schemas import MealPlan, MealDay, MealItem

# Load foods once at startup
FOODS_PATH = Path(__file__).parent.parent / "data" / "foods.json"
with open(FOODS_PATH, encoding="utf-8") as f:
    ALL_FOODS = json.load(f)

DAYS_EN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
DAYS_KN = {
    "Monday":"ಸೋಮವಾರ","Tuesday":"ಮಂಗಳವಾರ",
    "Wednesday":"ಬುಧವಾರ","Thursday":"ಗುರುವಾರ",
    "Friday":"ಶುಕ್ರವಾರ","Saturday":"ಶನಿವಾರ","Sunday":"ಭಾನುವಾರ"
}

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
    return MealItem(
        name_en       = f["name_en"],
        name_kn       = f["name_kn"],
        ingredients   = [f["name_en"]],  # simplified
        calories      = f["calories_per_100g"],
        protein_g     = f["protein_g"],
        calcium_mg    = f["calcium_mg"],
        iron_mg       = f["iron_mg"],
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
    ai_recommendations: list = None,
) -> MealPlan:
    if ai_recommendations is None:
        ai_recommendations = []

    # Hardcoded fallback as requested
    hardcoded_schedule = [
        ("Monday",    "Ragi mudde+Sambar", "Rice+Dal+Sabzi", "Chapati+Palya",   142),
        ("Tuesday",   "Avalakki upma",     "Bisibelebath",   "Rice+Rasam",      138),
        ("Wednesday", "Idli+Chutney",      "Rice+Rajma",     "Roti+Dal",        145),
        ("Thursday",  "Dosa+Sambar",       "Pulao+Raita",    "Rice+Sambar",     140),
        ("Friday",    "Upma+Chutney",      "Rice+Curry",     "Chapati+Sabzi",   143),
        ("Saturday",  "Poha+Banana",       "Curd rice",      "Khichdi",         135),
        ("Sunday",    "Puri+Sabzi",        "Special rice",   "Khichdi+Ghee",    148),
    ]

    week = []
    total_cost = 0

    for day_en, b_name, l_name, d_name, cost in hardcoded_schedule:
        cost_per_meal = cost / 3
        
        b = MealItem(name_en=b_name, name_kn="", ingredients=[], calories=400, protein_g=12, calcium_mg=200, iron_mg=5, cost_inr=cost_per_meal, prep_time_min=20)
        l = MealItem(name_en=l_name, name_kn="", ingredients=[], calories=600, protein_g=18, calcium_mg=300, iron_mg=8, cost_inr=cost_per_meal, prep_time_min=30)
        d = MealItem(name_en=d_name, name_kn="", ingredients=[], calories=500, protein_g=15, calcium_mg=250, iron_mg=6, cost_inr=cost_per_meal, prep_time_min=25)

        total_cost += cost

        week.append(MealDay(
            day       = day_en,
            day_kn    = DAYS_KN.get(day_en, ""),
            breakfast = b,
            lunch     = l,
            dinner    = d,
        ))

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
        week              = week,
        avg_daily_cal     = 1500.0,
        avg_protein_g     = 45.0,
        avg_calcium_mg    = 750.0,
        avg_iron_mg       = 19.0,
        total_cost_inr    = float(total_cost),
        generated_by      = "fallback",
        ai_recommendations= ai_recommendations,
    )