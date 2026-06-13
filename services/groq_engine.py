import json
from groq import Groq
from config import GROQ_API_KEY
from models.schemas import MealPlan, MealDay, MealItem, AIRecommendation
from services.fallback_engine import generate_fallback_plan, DAYS_KN
from services.diet_filter import (
    DIET_VEGETARIAN, DIET_EGGETARIAN, DIET_NONVEG,
    get_strategy_note, validate_and_fix_plan,
)

client = Groq(api_key=GROQ_API_KEY)

ICMR_RDA = {
    "5-8":   {"calories": 1350, "protein_g": 20, "calcium_mg": 600,  "iron_mg": 13},
    "9-12":  {"calories": 1700, "protein_g": 30, "calcium_mg": 800,  "iron_mg": 16},
    "13-15": {"calories": 2100, "protein_g": 45, "calcium_mg": 800,  "iron_mg": 22},
}


def _build_prompt(data: dict) -> str:
    rda           = ICMR_RDA.get(data["age_group"], ICMR_RDA["9-12"])
    diet_pref     = data["diet_pref"]
    strategy_note = get_strategy_note(data["strategy"], diet_pref)

    # Build explicit diet block for the prompt
    if diet_pref == DIET_VEGETARIAN:
        diet_block = (
            "DIET: vegetarian — ABSOLUTELY NO eggs, meat, chicken, fish, seafood, mutton, "
            "prawn, or any animal flesh in ANY meal across ALL 7 days. "
            "Use only: dal, paneer, curd, milk, vegetables, fruits, grains, nuts, legumes, "
            "Ragi Mudde, Jowar Roti, Idli, Dosa, Upma, Sambar, Horsegram, Sprouted Moong, "
            "Avarekalu, Bisibelebath, Khichdi, Curd Rice."
        )
    elif diet_pref == DIET_EGGETARIAN:
        diet_block = (
            "DIET: eggetarian — Eggs are allowed. ABSOLUTELY NO meat, chicken, fish, seafood, "
            "mutton, prawn, or any other animal flesh. "
            "Use: eggs, dal, paneer, curd, milk, vegetables, fruits, grains, nuts, legumes."
        )
    else:
        diet_block = (
            "DIET: non-vegetarian — All foods allowed including eggs, chicken, fish, seafood."
        )

    return f"""You are a certified child nutritionist for Karnataka schools, India.
Generate a 7-day weekly meal plan as valid JSON only.

STUDENT PROFILE:
- Age Group: {data['age_group']} years
- Region: {data['region']} (Karnataka)
- Month: {data['month']} (use seasonal ingredients)
- BMI Classification: {data.get('bmi_class', 'normal')}
- Strategy: {data['strategy']} — {strategy_note}
- Allergies to avoid: {data.get('allergies', [])}

{diet_block}

ICMR DAILY TARGETS:
- Calories: {rda['calories']} kcal
- Protein: {rda['protein_g']}g
- Calcium: {rda['calcium_mg']}mg
- Iron: {rda['iron_mg']}mg

STRICT RULES:
1. Use ONLY locally available Karnataka foods for the {data['region']} region.
2. Each individual meal cost must be under ₹50.
3. No meal name repeated more than twice across the 7 days.
4. Include Kannada name for every meal.
5. Use seasonal ingredients appropriate for {data['month']}.
6. All 7 days must be complete with breakfast, lunch, and dinner.
7. DIET COMPLIANCE IS NON-NEGOTIABLE — re-read the DIET block above before writing
   every single meal. Generating a non-compliant meal invalidates the entire plan.

RESPOND WITH ONLY THIS JSON — NO other text, no markdown, no explanation:
{{
  "week": [
    {{
      "day": "Monday",
      "day_kn": "ಸೋಮವಾರ",
      "breakfast": {{
        "name_en": "...",
        "name_kn": "...",
        "ingredients": ["...", "..."],
        "calories": 0,
        "protein_g": 0,
        "calcium_mg": 0,
        "iron_mg": 0,
        "cost_inr": 0,
        "prep_time_min": 0
      }},
      "lunch": {{ "name_en": "...", "name_kn": "...", "ingredients": [], "calories": 0, "protein_g": 0, "calcium_mg": 0, "iron_mg": 0, "cost_inr": 0, "prep_time_min": 0 }},
      "dinner": {{ "name_en": "...", "name_kn": "...", "ingredients": [], "calories": 0, "protein_g": 0, "calcium_mg": 0, "iron_mg": 0, "cost_inr": 0, "prep_time_min": 0 }}
    }}
  ]
}}
"""


def generate_groq_plan(
    school_name       : str,
    student_name      : str,
    teacher_name      : str,
    age_group         : str,
    diet_pref         : str,
    region            : str,
    month             : str,
    strategy          : str,
    bmi_class         : str  = None,
    allergies         : list = None,
    ai_recommendations: list = None,
) -> MealPlan:

    if allergies is None:
        allergies = []
    if ai_recommendations is None:
        ai_recommendations = []

    diet_pref = (diet_pref or DIET_VEGETARIAN).lower().strip()

    prompt_data = {
        "age_group": age_group,
        "diet_pref": diet_pref,
        "region":    region,
        "month":     month,
        "strategy":  strategy,
        "bmi_class": bmi_class,
        "allergies": allergies,
    }

    try:
        response = client.chat.completions.create(
            model           = "llama-3.1-8b-instant",
            messages        = [{"role": "user", "content": _build_prompt(prompt_data)}],
            max_tokens      = 3000,
            temperature     = 0.4,
            response_format = {"type": "json_object"},
        )

        raw  = response.choices[0].message.content
        data = json.loads(raw)

        # ── Post-generation diet validation ───────────────────────────────────
        # Even with a strong prompt, LLMs can slip. Validate every meal name
        # and replace any violations with the closest compliant substitute.
        data, violations = validate_and_fix_plan(data, diet_pref)
        if violations:
            print(
                f"[groq_engine] Diet violations auto-fixed for {student_name} "
                f"({diet_pref}): {violations}"
            )

        # ── Build MealPlan from (now-validated) Groq response ─────────────────
        week: list[MealDay] = []
        total_cal = total_pro = total_cal_mg = total_iron = total_cost = 0.0

        for day_data in data["week"]:
            meals: dict = {}
            for meal_type in ("breakfast", "lunch", "dinner"):
                m = day_data.get(meal_type)
                if not m or not isinstance(m, dict):
                    raise ValueError(f"Missing or invalid {meal_type} in Groq response")
                item = MealItem(
                    name_en       = m["name_en"],
                    name_kn       = m.get("name_kn", ""),
                    ingredients   = m.get("ingredients", []),
                    calories      = float(m.get("calories", 0)),
                    protein_g     = float(m.get("protein_g", 0)),
                    calcium_mg    = float(m.get("calcium_mg", 0)),
                    iron_mg       = float(m.get("iron_mg", 0)),
                    cost_inr      = float(m.get("cost_inr", 0)),
                    prep_time_min = int(m.get("prep_time_min", 20)),
                )
                meals[meal_type] = item
                total_cal    += item.calories
                total_pro    += item.protein_g
                total_cal_mg += item.calcium_mg
                total_iron   += item.iron_mg
                total_cost   += item.cost_inr

            week.append(MealDay(
                day       = day_data["day"],
                day_kn    = day_data.get("day_kn", DAYS_KN.get(day_data["day"], "")),
                breakfast = meals["breakfast"],
                lunch     = meals["lunch"],
                dinner    = meals["dinner"],
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
            avg_daily_cal     = round(total_cal    / 7, 1),
            avg_protein_g     = round(total_pro    / 7, 2),
            avg_calcium_mg    = round(total_cal_mg / 7, 1),
            avg_iron_mg       = round(total_iron   / 7, 2),
            total_cost_inr    = round(total_cost,       2),
            generated_by      = "groq",
            ai_recommendations = ai_recommendations,
        )

    except Exception as e:
        print(f"⚠️ Groq failed: {e} — switching to fallback engine")
        return generate_fallback_plan(
            school_name, student_name, teacher_name,
            age_group, diet_pref, region, month, strategy, bmi_class,
            ai_recommendations=ai_recommendations,
        )


# ── AI Nutrition Advisor ───────────────────────────────────────────────────────

def _build_advisor_prompt(question: str, profile: dict, history: list,
                           language: str) -> str:
    diet  = (profile.get("diet_pref") or DIET_VEGETARIAN).lower().strip()
    age   = profile.get("age") or profile.get("age_group") or "school-age"
    bmi   = profile.get("bmi_class") or "normal"
    name  = profile.get("student_name") or "the student"
    notes = profile.get("health_notes") or ""

    # Build diet-safe food list for the advisor context
    if diet == DIET_VEGETARIAN:
        allowed = (
            "vegetarian foods only: dal, paneer, curd, milk, ragi, jowar, "
            "sprouted moong, horsegram, avarekalu, groundnuts, seasonal vegetables and fruits. "
            "Do NOT mention eggs, chicken, fish, or meat in any recommendation."
        )
    elif diet == DIET_EGGETARIAN:
        allowed = (
            "eggs and vegetarian foods: eggs, dal, paneer, curd, milk, ragi, jowar, "
            "sprouted moong, horsegram, seasonal vegetables and fruits. "
            "Do NOT mention chicken, fish, or meat."
        )
    else:
        allowed = (
            "all foods including eggs, chicken, fish, and vegetarian options."
        )

    lang_instruction = (
        "Respond in Kannada (ಕನ್ನಡ)." if language == "kn"
        else "Respond in English." if language == "en"
        else "Respond in the same language as the question."
    )

    history_text = ""
    for msg in (history or [])[-6:]:  # last 3 turns
        role    = "Teacher" if msg.get("role") == "user" else "NutriPrint AI"
        content = msg.get("content", "")
        history_text += f"{role}: {content}\n"

    return f"""You are NutriPrint AI Advisor — a certified child nutrition expert for Karnataka schools.

STUDENT PROFILE:
- Name: {name}
- Age: {age}
- BMI Status: {bmi}
- Diet: {diet}
- Health notes: {notes or 'none'}

DIET CONSTRAINT: Recommend {allowed}

{f'CONVERSATION SO FAR:{chr(10)}{history_text}' if history_text else ''}

TEACHER QUESTION: {question}

INSTRUCTIONS:
1. Answer the question with practical, actionable nutrition advice.
2. Suggest 2-3 specific Karnataka foods relevant to the student's profile.
3. Keep recommendations safe for school-age children.
4. {lang_instruction}
5. After your answer, provide 1-3 structured recommendations in this EXACT JSON format
   (append it after your text answer, separated by ---JSON---):

---JSON---
{{
  "recommendations": [
    {{
      "title": "Short title",
      "short_action": "One-line action for poster",
      "detailed_explanation": "2-3 sentence explanation",
      "parent_guidance": "Practical tip for parents",
      "language": "{language if language in ('en','kn') else 'en'}"
    }}
  ]
}}
"""


def ask_nutrition_advisor(
    question : str,
    profile  : dict,
    history  : list = None,
    language : str  = "en",
) -> dict:
    """
    NutriPrint AI Advisor — diet-aware nutrition Q&A.
    Returns {answer, recommendations, generated_by}.
    """
    diet_pref = (profile.get("diet_pref") or DIET_VEGETARIAN).lower().strip()

    try:
        prompt = _build_advisor_prompt(question, profile, history or [], language)

        response = client.chat.completions.create(
            model       = "llama-3.1-8b-instant",
            messages    = [{"role": "user", "content": prompt}],
            max_tokens  = 1200,
            temperature = 0.5,
        )

        raw_text = response.choices[0].message.content.strip()

        # Split answer from structured JSON block
        recommendations: list[dict] = []
        answer = raw_text

        if "---JSON---" in raw_text:
            parts  = raw_text.split("---JSON---", 1)
            answer = parts[0].strip()
            try:
                json_data        = json.loads(parts[1].strip())
                recommendations  = json_data.get("recommendations", [])
            except (json.JSONDecodeError, IndexError):
                recommendations = []

        # Sanitise recommendations: remove any that mention forbidden foods for this diet
        safe_recs = []
        for rec in recommendations:
            # Check title and short_action for diet violations
            combined = f"{rec.get('title','')} {rec.get('short_action','')} {rec.get('detailed_explanation','')} {rec.get('parent_guidance','')}"
            from services.diet_filter import is_allowed_for_diet, is_nonveg_item, is_meat_item, is_egg_item
            # Simple check: if vegetarian and any meat/egg keyword in the text, skip
            skip = False
            if diet_pref == DIET_VEGETARIAN:
                lower = combined.lower()
                forbidden = {"chicken","egg","fish","mutton","meat","prawn","shrimp","seafood","koli","meen","mutte"}
                if any(kw in lower for kw in forbidden):
                    skip = True
            elif diet_pref == DIET_EGGETARIAN:
                lower = combined.lower()
                forbidden = {"chicken","fish","mutton","meat","prawn","shrimp","seafood","koli","meen"}
                if any(kw in lower for kw in forbidden):
                    skip = True
            if not skip:
                safe_recs.append(rec)

        return {
            "answer":          answer,
            "recommendations": safe_recs,
            "generated_by":    "groq",
        }

    except Exception as e:
        print(f"⚠️ AI Advisor failed: {e}")
        # Diet-appropriate fallback message
        if diet_pref == DIET_VEGETARIAN:
            fallback = (
                "For a vegetarian student, focus on Ragi Mudde, Horsegram Saaru, "
                "Sprouted Moong, Paneer, Curd Rice, and seasonal vegetables to meet "
                "protein, calcium, and iron needs."
            )
        elif diet_pref == DIET_EGGETARIAN:
            fallback = (
                "For an eggetarian student, boiled eggs with Ragi Mudde, Horsegram Saaru, "
                "and Palak Dal provide excellent protein, calcium, and iron."
            )
        else:
            fallback = (
                "Ensure balanced meals with Karnataka regional foods. "
                "Include Ragi, seasonal vegetables, and adequate protein daily."
            )

        return {
            "answer":          fallback,
            "recommendations": [],
            "generated_by":    "fallback",
        }
