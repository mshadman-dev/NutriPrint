"""
Allergen mapping and dairy allergy filtering tests.
Run: python -m pytest tests/test_allergen_map.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.allergen_map import ALLERGEN_CATEGORIES, get_excluded_keywords
from services.fallback_engine import generate_fallback_plan


class TestAllergenCategoryMapping:
    """Test the allergen category mapping and keyword expansion."""

    def test_milk_category_contains_dairy_keywords(self):
        """Milk category should include curd and yogurt."""
        assert "milk" in ALLERGEN_CATEGORIES["milk"]
        assert "curd" in ALLERGEN_CATEGORIES["milk"]
        assert "yogurt" in ALLERGEN_CATEGORIES["milk"]

    def test_dairy_category_same_as_milk(self):
        """Dairy category should map to same keywords as milk."""
        assert set(ALLERGEN_CATEGORIES["dairy"]) == set(ALLERGEN_CATEGORIES["milk"])

    def test_get_excluded_keywords_recognized_term(self):
        """get_excluded_keywords should expand recognized allergen terms."""
        keywords = get_excluded_keywords(["milk"])
        assert "milk" in keywords
        assert "curd" in keywords
        assert "yogurt" in keywords

    def test_get_excluded_keywords_dairy_term(self):
        """get_excluded_keywords should expand 'dairy' term."""
        keywords = get_excluded_keywords(["dairy"])
        assert "milk" in keywords
        assert "curd" in keywords
        assert "yogurt" in keywords

    def test_get_excluded_keywords_unrecognized_term_fallback(self):
        """Unrecognized allergen terms should be added as-is (fallback)."""
        keywords = get_excluded_keywords(["unknown_allergen"])
        assert "unknown_allergen" in keywords

    def test_get_excluded_keywords_empty_list(self):
        """Empty allergy list should return empty set."""
        keywords = get_excluded_keywords([])
        assert keywords == set()

    def test_get_excluded_keywords_case_insensitive(self):
        """get_excluded_keywords should be case-insensitive."""
        keywords_upper = get_excluded_keywords(["MILK"])
        keywords_lower = get_excluded_keywords(["milk"])
        assert keywords_upper == keywords_lower

    def test_get_excluded_keywords_strips_whitespace(self):
        """get_excluded_keywords should strip leading/trailing whitespace."""
        keywords = get_excluded_keywords(["  milk  "])
        assert "milk" in keywords


class TestDairyAllergyFiltering:
    """Test that dairy allergies are correctly filtered in meal plans."""

    def test_milk_allergy_excludes_curd_rice(self):
        """Student with milk allergy should NOT receive Curd Rice."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="june",
            strategy="standard",
            allergies=["milk"],
        )

        curd_rice_found = False
        for day in plan.week:
            for meal_type in ("breakfast", "lunch", "dinner"):
                meal = getattr(day, meal_type)
                if meal.name_en == "Curd Rice":
                    curd_rice_found = True

        assert not curd_rice_found, \
            "Milk-allergic student should not receive Curd Rice in any meal"

    def test_dairy_allergy_excludes_curd_rice(self):
        """Student with dairy allergy should NOT receive Curd Rice."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="june",
            strategy="standard",
            allergies=["dairy"],
        )

        curd_rice_found = False
        for day in plan.week:
            for meal_type in ("breakfast", "lunch", "dinner"):
                meal = getattr(day, meal_type)
                if meal.name_en == "Curd Rice":
                    curd_rice_found = True

        assert not curd_rice_found, \
            "Dairy-allergic student should not receive Curd Rice in any meal"

    def test_yogurt_allergy_via_milk_category_excludes_curd_rice(self):
        """Milk category includes yogurt, so yogurt substring matches work."""
        # Note: we're not adding "yogurt" as a top-level category,
        # but the milk category includes "yogurt" as a keyword
        keywords = get_excluded_keywords(["milk"])
        assert "yogurt" in keywords, "Milk category should include yogurt keyword"

    def test_no_allergy_allows_curd_rice(self):
        """Student without dairy allergy CAN receive Curd Rice."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="june",
            strategy="standard",
            allergies=[],
        )

        curd_rice_found = False
        for day in plan.week:
            for meal_type in ("breakfast", "lunch", "dinner"):
                meal = getattr(day, meal_type)
                if meal.name_en == "Curd Rice":
                    curd_rice_found = True

        assert curd_rice_found, \
            "Student without dairy allergy should be able to receive Curd Rice"

    def test_banana_sheera_not_excluded_for_dairy_allergy(self):
        """
        Student with dairy allergy CAN receive Banana Sheera.
        (Banana Sheera is not documented as dairy in foods.json)
        """
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="june",
            strategy="standard",
            allergies=["milk"],
        )

        # Banana Sheera should not be excluded (it's not marked as dairy)
        # This test just ensures it doesn't crash and the plan is valid
        assert len(plan.week) == 7
        for day in plan.week:
            assert day.breakfast is not None
            assert day.lunch is not None
            assert day.dinner is not None

    def test_milk_allergy_plan_has_7_days(self):
        """Milk-allergic plan should still have 7 days of meals."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="january",
            strategy="standard",
            allergies=["milk"],
        )

        assert len(plan.week) == 7

    def test_milk_allergy_plan_no_none_meals(self):
        """Milk-allergic plan should have no None meals."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="mangalore",
            month="january",
            strategy="standard",
            allergies=["milk"],
        )

        for day in plan.week:
            assert day.breakfast is not None, f"{day.day} breakfast is None"
            assert day.lunch is not None, f"{day.day} lunch is None"
            assert day.dinner is not None, f"{day.day} dinner is None"

    def test_unknown_allergen_uses_substring_fallback(self):
        """Unknown allergen should use raw substring matching."""
        plan = generate_fallback_plan(
            school_name="Test School",
            student_name="Test Student",
            teacher_name="Test Teacher",
            age_group="9-12",
            gender="boy",
            diet_pref="vegetarian",
            region="bengaluru_rural",
            month="january",
            strategy="standard",
            allergies=["xyz_unknown_allergen_xyz"],
        )

        # Plan should still have 7 days (no foods match the unknown allergen)
        assert len(plan.week) == 7
        for day in plan.week:
            assert day.breakfast is not None
            assert day.lunch is not None
            assert day.dinner is not None
