from __future__ import annotations

from typing import Any

from models.schemas import MealPlan
from services.fallback_engine import generate_fallback_plan


PILOT_TEACHER = {
    "name": "Kavya Rao",
    "email": "kavya.rao@nutriprint.in",
    "school": "Government Higher Primary School, Moodbidri",
    "district": "Dakshina Kannada",
}

PILOT_STUDENTS = [
    {
        "name": "Aarav Hegde",
        "age": 11,
        "gender": "boy",
        "height_cm": 142,
        "weight_kg": 34,
        "bmi": 16.9,
        "classification": "normal",
        "percentile": 45,
    },
    {
        "name": "Nisha Poojary",
        "age": 10,
        "gender": "girl",
        "height_cm": 134,
        "weight_kg": 26,
        "bmi": 14.5,
        "classification": "underweight",
        "percentile": 7,
    },
    {
        "name": "Kiran Gowda",
        "age": 12,
        "gender": "boy",
        "height_cm": 148,
        "weight_kg": 43,
        "bmi": 19.6,
        "classification": "normal",
        "percentile": 58,
    },
    {
        "name": "Meera Naik",
        "age": 13,
        "gender": "girl",
        "height_cm": 151,
        "weight_kg": 57,
        "bmi": 25.0,
        "classification": "overweight",
        "percentile": 86,
    },
    {
        "name": "Samarth Shetty",
        "age": 9,
        "gender": "boy",
        "height_cm": 130,
        "weight_kg": 24,
        "bmi": 14.2,
        "classification": "underweight",
        "percentile": 9,
    },
    {
        "name": "Anika D'Souza",
        "age": 11,
        "gender": "girl",
        "height_cm": 139,
        "weight_kg": 34,
        "bmi": 17.6,
        "classification": "normal",
        "percentile": 49,
    },
]

PILOT_HISTORY = {
    "Aarav Hegde": [
        {"date": "10/04/2026", "bmi": 16.2, "classification": "normal", "label": "Baseline", "age": 11, "gender": "boy"},
        {"date": "10/05/2026", "bmi": 16.6, "classification": "normal", "label": "Month 1", "age": 11, "gender": "boy"},
        {"date": "10/06/2026", "bmi": 16.9, "classification": "normal", "label": "Month 2", "age": 11, "gender": "boy"},
    ],
    "Nisha Poojary": [
        {"date": "12/04/2026", "bmi": 13.8, "classification": "underweight", "label": "Baseline", "age": 10, "gender": "girl"},
        {"date": "12/05/2026", "bmi": 14.1, "classification": "underweight", "label": "Month 1", "age": 10, "gender": "girl"},
        {"date": "12/06/2026", "bmi": 14.5, "classification": "underweight", "label": "Month 2", "age": 10, "gender": "girl"},
    ],
    "Kiran Gowda": [
        {"date": "08/04/2026", "bmi": 19.0, "classification": "normal", "label": "Baseline", "age": 12, "gender": "boy"},
        {"date": "08/05/2026", "bmi": 19.3, "classification": "normal", "label": "Month 1", "age": 12, "gender": "boy"},
        {"date": "08/06/2026", "bmi": 19.6, "classification": "normal", "label": "Month 2", "age": 12, "gender": "boy"},
    ],
    "Meera Naik": [
        {"date": "15/04/2026", "bmi": 25.9, "classification": "overweight", "label": "Baseline", "age": 13, "gender": "girl"},
        {"date": "15/05/2026", "bmi": 25.4, "classification": "overweight", "label": "Month 1", "age": 13, "gender": "girl"},
        {"date": "15/06/2026", "bmi": 25.0, "classification": "overweight", "label": "Month 2", "age": 13, "gender": "girl"},
    ],
    "Samarth Shetty": [
        {"date": "18/04/2026", "bmi": 13.7, "classification": "underweight", "label": "Baseline", "age": 9, "gender": "boy"},
        {"date": "18/05/2026", "bmi": 14.0, "classification": "underweight", "label": "Month 1", "age": 9, "gender": "boy"},
        {"date": "18/06/2026", "bmi": 14.2, "classification": "underweight", "label": "Month 2", "age": 9, "gender": "boy"},
    ],
    "Anika D'Souza": [
        {"date": "20/04/2026", "bmi": 17.1, "classification": "normal", "label": "Baseline", "age": 11, "gender": "girl"},
        {"date": "20/05/2026", "bmi": 17.4, "classification": "normal", "label": "Month 1", "age": 11, "gender": "girl"},
        {"date": "13/06/2026", "bmi": 17.6, "classification": "normal", "label": "Month 2", "age": 11, "gender": "girl"},
    ],
}

PILOT_STATS = {
    "total_students": 38,
    "total_plans": 31,
    "total_assessments": 38,
    "total_foods": 72,
    "plans_this_month": 12,
    "teacher_name": PILOT_TEACHER["name"],
    "school_name": PILOT_TEACHER["school"],
}

_PILOT_PLANS: dict[str, tuple[dict[str, Any], MealPlan]] = {}


def register_pilot_plan(plan: MealPlan) -> str:
    token = plan.share_token or "pilot-plan-aarav"
    try:
        payload = plan.model_dump()
    except AttributeError:
        payload = plan.dict()

    row = {
        "id": plan.plan_id or token,
        "student_name": plan.student_name,
        "school_name": plan.school_name,
        "teacher_name": plan.teacher_name,
        "age_group": plan.age_group,
        "diet_pref": plan.diet_pref,
        "region": plan.region,
        "month": plan.month,
        "strategy": plan.strategy,
        "bmi_class": plan.bmi_class,
        "plan_json": payload,
        "share_token": token,
    }
    _PILOT_PLANS[token] = (row, plan)
    return token


def get_pilot_plan(token: str) -> tuple[dict[str, Any], MealPlan] | None:
    if token in _PILOT_PLANS:
        return _PILOT_PLANS[token]
    if token in {"pilot-plan-aarav", "pilot-plan-nisha", "pilot-plan-meera"}:
        return _PILOT_PLANS.get(_ensure_default_plan(token))
    return None


def _ensure_default_plan(token: str = "pilot-plan-aarav") -> str:
    if token in _PILOT_PLANS:
        return token

    student = {
        "pilot-plan-aarav": ("Aarav Hegde", "normal", "standard"),
        "pilot-plan-nisha": ("Nisha Poojary", "underweight", "high_protein"),
        "pilot-plan-meera": ("Meera Naik", "overweight", "calorie_control"),
    }.get(token, ("Aarav Hegde", "normal", "standard"))

    plan = generate_fallback_plan(
        school_name=PILOT_TEACHER["school"],
        student_name=student[0],
        teacher_name=PILOT_TEACHER["name"],
        age_group="9-12",
        gender="student",
        diet_pref="vegetarian",
        region="mangalore",
        month="june",
        strategy=student[2],
        bmi_class=student[1],
        ai_recommendations=[
            {
                "title": "Strengthen weekday protein",
                "short_action": "Add dal, ragi, curd, and sprouted moong across the week.",
                "detailed_explanation": "The plan prioritises affordable Karnataka foods that support growth, iron intake, and steady school-day energy.",
                "parent_guidance": "Send one protein-rich snack such as groundnut laddu or sprouted moong twice a week.",
                "language": "en",
            }
        ],
    )
    plan.plan_id = token.replace("pilot-plan", "pilot")
    plan.share_token = token
    register_pilot_plan(plan)
    return token


_ensure_default_plan()
