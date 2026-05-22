"""高才通判定测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import TTPSEvaluator


def test_category_a_eligible():
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 3_000_000,
        "has_eligible_bachelor": False,
        "work_experience_years": 0,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "Chinese"
    })
    assert result["has_qualifying_category"]
    categories = [c["category"] for c in result["applicable_categories"]]
    assert "A" in categories


def test_category_b_eligible():
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 500_000,
        "has_eligible_bachelor": True,
        "work_experience_years": 5,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "Chinese"
    })
    assert result["has_qualifying_category"]
    categories = [c["category"] for c in result["applicable_categories"]]
    assert "B" in categories


def test_category_c_eligible():
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 500_000,
        "has_eligible_bachelor": True,
        "work_experience_years": 1,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "Chinese"
    })
    assert result["has_qualifying_category"]
    categories = [c["category"] for c in result["applicable_categories"]]
    assert "C" in categories


def test_category_c_excluded_for_local_non_graduate():
    """本地非本地毕业生不能申请C类"""
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 500_000,
        "has_eligible_bachelor": True,
        "work_experience_years": 1,
        "graduated_within_5_years": True,
        "is_local_non_graduate": True,
        "nationality": "Chinese"
    })
    categories = [c["category"] for c in result["applicable_categories"]]
    assert "C" not in categories
    assert "C类" in str(result.get("details", {}))


def test_not_eligible():
    """收入不高，又没合资格大学学位"""
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 200_000,
        "has_eligible_bachelor": False,
        "work_experience_years": 0,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "Chinese"
    })
    assert not result["has_qualifying_category"]


def test_country_excluded():
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 3_000_000,
        "has_eligible_bachelor": True,
        "work_experience_years": 5,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "朝鲜"
    })
    assert result["country_excluded"]


def test_university_check():
    evaluator = TTPSEvaluator()
    result = evaluator.check_university("清华大学")
    assert result["found"]

    result = evaluator.check_university("Massachusetts Institute of Technology")
    assert result["found"]

    result = evaluator.check_university("nonexistent university")
    assert not result["found"]


def test_both_a_and_b():
    """同时符合A类和B类"""
    evaluator = TTPSEvaluator()
    result = evaluator.evaluate({
        "annual_income_hkd": 3_000_000,
        "has_eligible_bachelor": True,
        "work_experience_years": 5,
        "graduated_within_5_years": True,
        "is_local_non_graduate": False,
        "nationality": "Chinese"
    })
    categories = [c["category"] for c in result["applicable_categories"]]
    assert "A" in categories
    assert "B" in categories


if __name__ == "__main__":
    test_category_a_eligible()
    test_category_b_eligible()
    test_category_c_eligible()
    test_category_c_excluded_for_local_non_graduate()
    test_not_eligible()
    test_country_excluded()
    test_university_check()
    test_both_a_and_b()
    print("✅ TTPS 测试全部通过!")
