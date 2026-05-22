"""端到端集成测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import CrossComparer, FAQFinder


def test_cross_comparer_high_earner():
    """高收入人士：高才通A类 + 优才应该都符合"""
    comparer = CrossComparer()
    profile = {
        "age": 35,
        "highest_degree": "master",
        "degree_count": 1,
        "is_stem": False,
        "chinese_proficient": True,
        "english_proficient": True,
        "total_experience_years": 8,
        "senior_experience_years": 3,
        "annual_income_hkd": 3_000_000,
        "num_professional_qualifications": 1,
        "in_talent_list_profession": False,
        "matches_talent_list": False,
        "has_eligible_bachelor": True,
        "work_experience_years": 8,
        "graduated_within_5_years": False,
        "has_job_offer": False,
        "business_profit_hkd": None,
        "years_at_wellknown_company": 3,
        "years_overseas": 0,
        "has_international_achievements": False,
        "spouse_has_degree": True,
        "spouse_accompanying": True,
        "has_international_award": False,
        "has_industry_contribution": False,
        "financially_independent": True,
        "good_character": True
    }
    result = comparer.compare(profile)
    assert result["results"]["TTPS"]["eligible"]
    assert not result["no_plan_eligible"]


def test_cross_comparer_low_income_no_degree():
    """低收入+无学历：应无计划符合"""
    comparer = CrossComparer()
    profile = {
        "age": 25,
        "highest_degree": "bachelor",
        "degree_count": 1,
        "is_stem": False,
        "chinese_proficient": True,
        "english_proficient": False,
        "total_experience_years": 1,
        "senior_experience_years": 0,
        "annual_income_hkd": 300_000,
        "num_professional_qualifications": 0,
        "in_talent_list_profession": False,
        "matches_talent_list": False,
        "has_eligible_bachelor": False,
        "work_experience_years": 1,
        "graduated_within_5_years": True,
        "has_job_offer": False,
        "business_profit_hkd": None,
        "years_at_wellknown_company": 0,
        "years_overseas": 0,
        "has_international_achievements": False,
        "spouse_has_degree": False,
        "spouse_accompanying": False,
        "has_international_award": False,
        "has_industry_contribution": False,
        "financially_independent": True,
        "good_character": True
    }
    result = comparer.compare(profile)
    assert result["no_plan_eligible"]


def test_faq_search():
    results = FAQFinder.search("收入")
    assert len(results) > 0
    assert any("收入" in r["question"] for r in results)


def test_glossary_search():
    results = FAQFinder.search_glossary("优才")
    assert len(results) > 0


if __name__ == "__main__":
    test_cross_comparer_high_earner()
    test_cross_comparer_low_income_no_degree()
    test_faq_search()
    test_glossary_search()
    print("✅ 集成测试全部通过!")
