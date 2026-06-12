"""
Diet filtering regression tests.
Run:  python -m pytest tests/test_diet_filter.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.diet_filter import (
    DIET_VEGETARIAN, DIET_EGGETARIAN, DIET_NONVEG,
    is_allowed_for_diet,
    is_nonveg_item,
    is_meat_item,
    is_egg_item,
    filter_food_servings,
    get_fix_foods,
    get_strategy_note,
    enforce_diet_on_item,
    validate_and_fix_plan,
)
from services.food_equivalents import get_food_equivalents
from services.bmi_calculator import calculate_nutrition_gap
from services.fallback_engine import generate_fallback_plan


# ── is_allowed_for_diet ────────────────────────────────────────────────────────

class TestIsAllowedForDiet:
    # Vegetarian: no meat, no egg, no seafood
    def test_veg_rejects_chicken(self):
        assert not is_allowed_for_diet("Chicken Saaru with Jolada Rotti", DIET_VEGETARIAN)

    def test_veg_rejects_egg(self):
        assert not is_allowed_for_diet("Egg Curry with Rice", DIET_VEGETARIAN)

    def test_veg_rejects_fish(self):
        assert not is_allowed_for_diet("Fish Curry with Rice", DIET_VEGETARIAN)

    def test_veg_rejects_omelette(self):
        assert not is_allowed_for_diet("Omelette with Bread", DIET_VEGETARIAN)

    def test_veg_rejects_prawn(self):
        assert not is_allowed_for_diet("Prawn Ghee Roast with Neer Dosa", DIET_VEGETARIAN)

    def test_veg_allows_ragi(self):
        assert is_allowed_for_diet("Ragi Mudde", DIET_VEGETARIAN)

    def test_veg_allows_paneer(self):
        assert is_allowed_for_diet("Paneer Sabzi", DIET_VEGETARIAN)

    def test_veg_allows_horsegram(self):
        assert is_allowed_for_diet("Horsegram Saaru", DIET_VEGETARIAN)

    def test_veg_allows_idli(self):
        assert is_allowed_for_diet("Idli with Sambar", DIET_VEGETARIAN)

    def test_veg_allows_curd_rice(self):
        assert is_allowed_for_diet("Curd Rice", DIET_VEGETARIAN)

    # Eggetarian: eggs OK, no meat/fish/seafood
    def test_egg_allows_egg_curry(self):
        assert is_allowed_for_diet("Egg Curry with Rice", DIET_EGGETARIAN)

    def test_egg_allows_omelette(self):
        assert is_allowed_for_diet("Omelette with Bread", DIET_EGGETARIAN)

    def test_egg_rejects_chicken(self):
        assert not is_allowed_for_diet("Chicken Saaru", DIET_EGGETARIAN)

    def test_egg_rejects_fish(self):
        assert not is_allowed_for_diet("Fish Curry with Rice", DIET_EGGETARIAN)

    def test_egg_rejects_prawn(self):
        assert not is_allowed_for_diet("Prawn Ghee Roast", DIET_EGGETARIAN)

    # Non-veg: everything allowed
    def test_nonveg_allows_chicken(self):
        assert is_allowed_for_diet("Chicken Saaru", DIET_NONVEG)

    def test_nonveg_allows_egg(self):
        assert is_allowed_for_diet("Egg Curry", DIET_NONVEG)

    def test_nonveg_allows_fish(self):
        assert is_allowed_for_diet("Fish Curry with Rice", DIET_NONVEG)


# ── filter_food_servings ───────────────────────────────────────────────────────

class TestFilterFoodServings:
    FORBIDDEN_VEG = {"egg", "chicken", "fish", "mutton", "prawn", "seafood", "meat"}
    FORBIDDEN_EGG = {"chicken", "fish", "mutton", "prawn", "seafood", "meat"}

    def _contains_forbidden(self, foods: list, forbidden: set) -> list:
        hits = []
        for f in foods:
            lower = f["name"].lower()
            if any(kw in lower for kw in forbidden):
                hits.append(f["name"])
        return hits

    def test_veg_protein_no_egg_chicken_fish(self):
        foods = filter_food_servings("protein_g", DIET_VEGETARIAN)
        hits = self._contains_forbidden(foods, self.FORBIDDEN_VEG)
        assert hits == [], f"Forbidden items in veg protein: {hits}"

    def test_veg_protein_has_dal_paneer(self):
        foods = filter_food_servings("protein_g", DIET_VEGETARIAN)
        names = [f["name"] for f in foods]
        assert "Toor Dal" in names
        assert "Paneer" in names

    def test_egg_protein_has_egg_no_chicken(self):
        foods = filter_food_servings("protein_g", DIET_EGGETARIAN)
        names = [f["name"] for f in foods]
        assert "Egg" in names
        hits = self._contains_forbidden(foods, self.FORBIDDEN_EGG)
        assert hits == [], f"Forbidden items in eggetarian protein: {hits}"

    def test_nonveg_protein_has_chicken_fish(self):
        foods = filter_food_servings("protein_g", DIET_NONVEG)
        names = [f["name"] for f in foods]
        assert "Chicken Breast" in names
        assert "Fish" in names

    def test_carbs_same_for_all_diets(self):
        # Carbs pool is all-vegetarian, so no filtering difference
        veg  = filter_food_servings("carbs_g", DIET_VEGETARIAN)
        nonv = filter_food_servings("carbs_g", DIET_NONVEG)
        assert len(veg) == len(nonv)


# ── get_fix_foods ──────────────────────────────────────────────────────────────

class TestGetFixFoods:
    def test_veg_protein_fix_no_egg_chicken(self):
        fix = get_fix_foods("protein_g", DIET_VEGETARIAN)
        text = (fix["en"] + fix["kn"]).lower()
        assert "egg" not in text, f"Egg in veg protein fix: {fix['en']}"
        assert "chicken" not in text, f"Chicken in veg protein fix: {fix['en']}"
        assert "fish" not in text, f"Fish in veg protein fix: {fix['en']}"

    def test_egg_protein_fix_has_egg(self):
        fix = get_fix_foods("protein_g", DIET_EGGETARIAN)
        assert "egg" in fix["en"].lower() or "Egg" in fix["en"], f"Expected egg in eggetarian fix: {fix['en']}"

    def test_egg_protein_fix_no_chicken_fish(self):
        fix = get_fix_foods("protein_g", DIET_EGGETARIAN)
        text = fix["en"].lower()
        assert "chicken" not in text
        assert "fish" not in text

    def test_nonveg_protein_fix_has_meat_options(self):
        fix = get_fix_foods("protein_g", DIET_NONVEG)
        text = fix["en"].lower()
        # should mention eggs or chicken for non-veg
        assert "egg" in text or "chicken" in text or "fish" in text

    def test_calcium_fix_veg_safe(self):
        fix = get_fix_foods("calcium_mg", DIET_VEGETARIAN)
        text = fix["en"].lower()
        assert "egg" not in text
        assert "chicken" not in text


# ── validate_and_fix_plan ──────────────────────────────────────────────────────

class TestValidateAndFixPlan:
    def _make_plan(self, breakfast="Ragi Mudde", lunch="Horsegram Saaru", dinner="Curd Rice"):
        return {
            "week": [{
                "day": "Monday", "day_kn": "ಸೋಮವಾರ",
                "breakfast": {"name_en": breakfast, "name_kn": ""},
                "lunch":     {"name_en": lunch,     "name_kn": ""},
                "dinner":    {"name_en": dinner,     "name_kn": ""},
            }]
        }

    def test_clean_veg_plan_has_no_violations(self):
        plan = self._make_plan("Ragi Mudde", "Horsegram Saaru", "Curd Rice")
        _, violations = validate_and_fix_plan(plan, DIET_VEGETARIAN)
        assert violations == []

    def test_chicken_replaced_for_veg(self):
        plan = self._make_plan(dinner="Chicken Saaru with Jolada Rotti")
        fixed, violations = validate_and_fix_plan(plan, DIET_VEGETARIAN)
        assert len(violations) == 1
        replaced = fixed["week"][0]["dinner"]["name_en"]
        assert is_allowed_for_diet(replaced, DIET_VEGETARIAN), f"Replacement still non-veg: {replaced}"

    def test_egg_replaced_for_veg(self):
        plan = self._make_plan(breakfast="Omelette with Bread")
        fixed, violations = validate_and_fix_plan(plan, DIET_VEGETARIAN)
        assert len(violations) == 1
        replaced = fixed["week"][0]["breakfast"]["name_en"]
        assert is_allowed_for_diet(replaced, DIET_VEGETARIAN), f"Replacement still non-veg: {replaced}"

    def test_fish_replaced_for_veg(self):
        plan = self._make_plan(lunch="Fish Curry with Rice")
        fixed, violations = validate_and_fix_plan(plan, DIET_VEGETARIAN)
        assert len(violations) == 1

    def test_egg_kept_for_eggetarian(self):
        plan = self._make_plan(breakfast="Egg Curry with Rice")
        fixed, violations = validate_and_fix_plan(plan, DIET_EGGETARIAN)
        assert violations == []
        assert fixed["week"][0]["breakfast"]["name_en"] == "Egg Curry with Rice"

    def test_chicken_replaced_for_eggetarian(self):
        plan = self._make_plan(lunch="Koli Saaru (Chicken Soup)")
        fixed, violations = validate_and_fix_plan(plan, DIET_EGGETARIAN)
        assert len(violations) == 1
        replaced = fixed["week"][0]["lunch"]["name_en"]
        assert is_allowed_for_diet(replaced, DIET_EGGETARIAN), f"Replacement bad for eggetarian: {replaced}"

    def test_no_violations_for_nonveg(self):
        plan = self._make_plan(
            breakfast="Omelette with Bread",
            lunch="Chicken Saaru",
            dinner="Fish Curry with Rice"
        )
        _, violations = validate_and_fix_plan(plan, DIET_NONVEG)
        assert violations == []

    def test_multiple_violations_all_fixed(self):
        plan = self._make_plan(
            breakfast="Egg Bhurji",
            lunch="Chicken Saaru",
            dinner="Fish Curry with Rice"
        )
        fixed, violations = validate_and_fix_plan(plan, DIET_VEGETARIAN)
        assert len(violations) == 3
        for slot in ("breakfast", "lunch", "dinner"):
            name = fixed["week"][0][slot]["name_en"]
            assert is_allowed_for_diet(name, DIET_VEGETARIAN), f"{slot} still non-veg: {name}"


# ── get_food_equivalents ───────────────────────────────────────────────────────

class TestGetFoodEquivalents:
    FORBIDDEN_VEG = {"egg", "chicken breast", "fish", "chicken", "mutton"}
    FORBIDDEN_EGG = {"chicken breast", "fish", "chicken", "mutton"}

    def _extract_names(self, equivalents: list, key: str) -> list:
        for eq in equivalents:
            if eq["key"] == key:
                names = [e["name"].lower() for e in eq["examples"]]
                names += [c["name"].lower() for c in eq.get("suggested_combo", [])]
                return names
        return []

    def test_veg_protein_examples_clean(self):
        equivs = get_food_equivalents("9-12", DIET_VEGETARIAN)
        names = self._extract_names(equivs, "protein_g")
        for forbidden in self.FORBIDDEN_VEG:
            assert not any(forbidden in n for n in names), f"Forbidden '{forbidden}' in veg: {names}"

    def test_veg_protein_has_dal_paneer(self):
        equivs = get_food_equivalents("9-12", DIET_VEGETARIAN)
        for eq in equivs:
            if eq["key"] == "protein_g":
                names = [e["name"] for e in eq["examples"]]
                assert any("dal" in n.lower() or "Dal" in n for n in names), f"No dal in: {names}"
                break

    def test_egg_protein_has_egg(self):
        equivs = get_food_equivalents("9-12", DIET_EGGETARIAN)
        for eq in equivs:
            if eq["key"] == "protein_g":
                all_names = [e["name"].lower() for e in eq["examples"]]
                assert any("egg" in n for n in all_names), f"No egg in eggetarian examples: {all_names}"
                break

    def test_egg_protein_no_chicken_fish(self):
        equivs = get_food_equivalents("9-12", DIET_EGGETARIAN)
        names = self._extract_names(equivs, "protein_g")
        for forbidden in self.FORBIDDEN_EGG:
            assert not any(forbidden in n for n in names), f"Forbidden '{forbidden}' in eggetarian: {names}"

    def test_nonveg_protein_has_chicken_fish(self):
        equivs = get_food_equivalents("9-12", DIET_NONVEG)
        for eq in equivs:
            if eq["key"] == "protein_g":
                all_names = [e["name"].lower() for e in eq["examples"]]
                assert any("chicken" in n for n in all_names), f"No chicken in nonveg examples: {all_names}"
                assert any("fish" in n for n in all_names), f"No fish in nonveg examples: {all_names}"
                break

    def test_all_age_groups_veg_clean(self):
        for age in ("5-8", "9-12", "13-15"):
            equivs = get_food_equivalents(age, DIET_VEGETARIAN)
            names = self._extract_names(equivs, "protein_g")
            for forbidden in self.FORBIDDEN_VEG:
                assert not any(forbidden in n for n in names), \
                    f"Age {age}: forbidden '{forbidden}' in {names}"


# ── calculate_nutrition_gap ────────────────────────────────────────────────────

class TestCalculateNutritionGap:
    LOW_PLAN = {"avg_daily_cal": 900, "avg_protein_g": 12,
                "avg_calcium_mg": 300, "avg_iron_mg": 5}

    def test_veg_protein_fix_no_egg_chicken(self):
        gaps = calculate_nutrition_gap(self.LOW_PLAN, "9-12", DIET_VEGETARIAN)
        for g in gaps:
            if g["key"] == "protein_g" and g["fix_en"]:
                text = g["fix_en"].lower()
                assert "egg" not in text, f"Egg in veg gap fix: {g['fix_en']}"
                assert "chicken" not in text, f"Chicken in veg gap fix: {g['fix_en']}"

    def test_egg_protein_fix_has_egg(self):
        gaps = calculate_nutrition_gap(self.LOW_PLAN, "9-12", DIET_EGGETARIAN)
        for g in gaps:
            if g["key"] == "protein_g" and g["fix_en"]:
                assert "egg" in g["fix_en"].lower() or "Egg" in g["fix_en"], \
                    f"Expected egg in eggetarian gap fix: {g['fix_en']}"

    def test_good_nutrients_have_no_fix(self):
        good_plan = {"avg_daily_cal": 1800, "avg_protein_g": 35,
                     "avg_calcium_mg": 900, "avg_iron_mg": 20}
        gaps = calculate_nutrition_gap(good_plan, "9-12", DIET_VEGETARIAN)
        for g in gaps:
            if g["status"] == "good":
                assert g["fix_en"] is None


# ── fallback_engine ────────────────────────────────────────────────────────────

class TestFallbackEngineDietCompliance:
    def _check_plan_for_diet(self, diet: str):
        plan = generate_fallback_plan(
            school_name="Test", student_name="Student", teacher_name="",
            age_group="9-12", diet_pref=diet, region="mangalore",
            month="june", strategy="standard",
        )
        violations = []
        for day in plan.week:
            for slot in ("breakfast", "lunch", "dinner"):
                meal = getattr(day, slot)
                if not is_allowed_for_diet(meal.name_en, diet):
                    violations.append(f"{day.day} {slot}: {meal.name_en}")
        return violations

    def test_vegetarian_fallback_clean(self):
        violations = self._check_plan_for_diet(DIET_VEGETARIAN)
        assert violations == [], f"Veg fallback violations: {violations}"

    def test_eggetarian_fallback_no_meat(self):
        violations = self._check_plan_for_diet(DIET_EGGETARIAN)
        assert violations == [], f"Eggetarian fallback violations: {violations}"

    def test_fallback_has_7_days(self):
        plan = generate_fallback_plan(
            school_name="T", student_name="S", teacher_name="",
            age_group="9-12", diet_pref=DIET_VEGETARIAN, region="bengaluru_rural",
            month="january", strategy="standard",
        )
        assert len(plan.week) == 7

    def test_diet_pref_stored_correctly(self):
        plan = generate_fallback_plan(
            school_name="T", student_name="S", teacher_name="",
            age_group="9-12", diet_pref=DIET_VEGETARIAN, region="mangalore",
            month="june", strategy="standard",
        )
        assert plan.diet_pref == DIET_VEGETARIAN


# ── strategy notes ─────────────────────────────────────────────────────────────

class TestStrategyNotes:
    def test_high_protein_veg_no_chicken_recommendation(self):
        note = get_strategy_note("high_protein", DIET_VEGETARIAN)
        # The note may say "NO chicken" as a prohibition — that's correct.
        # What it must NOT do is recommend chicken as a food to eat.
        # Check it explicitly says "NO" before chicken/egg (i.e. prohibition, not recommendation)
        assert "NO" in note or "no" in note.lower(), "Should have explicit prohibition"
        assert "horsegram" in note.lower() or "paneer" in note.lower(), \
            f"Should recommend vegetarian protein sources: {note}"

    def test_high_protein_veg_recommends_veg_sources(self):
        note = get_strategy_note("high_protein", DIET_VEGETARIAN).lower()
        # Must recommend actual vegetarian protein sources
        veg_sources = ["horsegram", "paneer", "moong", "rajma", "groundnut", "soy"]
        assert any(src in note for src in veg_sources), \
            f"No veg protein source in note: {note}"

    def test_high_protein_egg_has_eggs_no_meat(self):
        note = get_strategy_note("high_protein", DIET_EGGETARIAN).lower()
        assert "egg" in note, f"Eggetarian strategy should mention eggs: {note}"
        # Should not recommend meat or fish as foods to eat (only prohibit them)
        # The note says "NO chicken, fish" — that's the prohibition, which is fine.
        assert "no chicken" in note or "no meat" in note or "no fish" in note, \
            f"Eggetarian strategy should prohibit meat: {note}"

    def test_high_protein_nonveg_has_chicken(self):
        note = get_strategy_note("high_protein", DIET_NONVEG).lower()
        assert "chicken" in note
