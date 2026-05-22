"""优才计分测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import QMASScorer


def test_age_eligible():
    scorer = QMASScorer()
    assert scorer.evaluate_age(18)["qualified"]
    assert scorer.evaluate_age(30)["qualified"]
    assert scorer.evaluate_age(39)["qualified"]


def test_age_mid():
    scorer = QMASScorer()
    assert scorer.evaluate_age(40)["qualified"]
    assert scorer.evaluate_age(44)["qualified"]


def test_age_edge():
    scorer = QMASScorer()
    assert scorer.evaluate_age(45)["qualified"]
    assert scorer.evaluate_age(50)["qualified"]


def test_age_ineligible():
    scorer = QMASScorer()
    assert not scorer.evaluate_age(17)["qualified"]
    assert not scorer.evaluate_age(51)["qualified"]
    assert not scorer.evaluate_age(60)["qualified"]


def test_education_phd():
    scorer = QMASScorer()
    r = scorer.evaluate_education("phd")
    assert r["qualified"]


def test_education_master():
    scorer = QMASScorer()
    r = scorer.evaluate_education("master")
    assert r["qualified"]

    # STEM加分
    r = scorer.evaluate_education("master", is_stem=True)
    assert r["qualified"]
    assert r.get("note") is not None


def test_education_dual_bachelor():
    scorer = QMASScorer()
    r = scorer.evaluate_education("bachelor", degree_count=2)
    assert r["qualified"]
    assert r["result"] == "双重学士学位"


def test_education_bachelor_only():
    scorer = QMASScorer()
    r = scorer.evaluate_education("bachelor", degree_count=1)
    assert not r["qualified"]


def test_language_both():
    scorer = QMASScorer()
    r = scorer.evaluate_language(True, True)
    assert r["qualified"]


def test_language_one():
    scorer = QMASScorer()
    r = scorer.evaluate_language(True, False)
    assert r["qualified"]


def test_language_none():
    scorer = QMASScorer()
    r = scorer.evaluate_language(False, False)
    assert not r["qualified"]


def test_experience_10y_5y_senior():
    scorer = QMASScorer()
    r = scorer.evaluate_experience(10, 5)
    assert r["qualified"]


def test_experience_5y_2y_senior():
    scorer = QMASScorer()
    r = scorer.evaluate_experience(5, 2)
    assert r["qualified"]


def test_experience_less_2y():
    scorer = QMASScorer()
    r = scorer.evaluate_experience(1, 0)
    assert not r["qualified"]


def test_income_above_threshold():
    scorer = QMASScorer()
    assert scorer.evaluate_income(1_000_000)["qualified"]
    assert scorer.evaluate_income(2_000_000)["qualified"]


def test_income_below_threshold():
    scorer = QMASScorer()
    assert not scorer.evaluate_income(900_000)["qualified"]


def test_talent_list_match():
    scorer = QMASScorer()
    assert scorer.evaluate_talent_list(True)["qualified"]
    assert not scorer.evaluate_talent_list(False)["qualified"]


def test_overseas_experience():
    scorer = QMASScorer()
    assert scorer.evaluate_overseas_experience(2)["qualified"]
    assert scorer.evaluate_overseas_experience(5)["qualified"]
    assert not scorer.evaluate_overseas_experience(1)["qualified"]


def test_spouse():
    scorer = QMASScorer()
    assert scorer.evaluate_spouse(True, True)["qualified"]
    assert not scorer.evaluate_spouse(False, True)["qualified"]
    assert not scorer.evaluate_spouse(True, False)["qualified"]


def test_achievement_based():
    scorer = QMASScorer()
    assert scorer.evaluate_achievement_based(True, False)["qualified"]
    assert scorer.evaluate_achievement_based(False, True)["qualified"]
    assert not scorer.evaluate_achievement_based(False, False)["qualified"]


def test_full_assessment_high_achiever():
    """模拟高水准申请人的完整评估"""
    scorer = QMASScorer()
    profile = {
        "age": 32,
        "highest_degree": "phd",
        "degree_count": 2,
        "is_stem": True,
        "chinese_proficient": True,
        "english_proficient": True,
        "total_experience_years": 10,
        "senior_experience_years": 5,
        "annual_income_hkd": 1_500_000,
        "num_professional_qualifications": 2,
        "in_talent_list_profession": True,
        "matches_talent_list": True,
        "business_profit_hkd": None,
        "years_at_wellknown_company": 5,
        "years_overseas": 3,
        "has_international_achievements": True,
        "spouse_has_degree": True,
        "spouse_accompanying": True,
        "has_international_award": False,
        "has_industry_contribution": False,
        "financially_independent": True,
        "good_character": True
    }
    result = scorer.full_assessment(profile)
    assert result["summary"]["criteria_met"] >= 10  # 高水准至少10项达标


if __name__ == "__main__":
    test_age_eligible()
    test_age_mid()
    test_age_edge()
    test_age_ineligible()
    test_education_phd()
    test_education_master()
    test_education_dual_bachelor()
    test_education_bachelor_only()
    test_language_both()
    test_language_one()
    test_language_none()
    test_experience_10y_5y_senior()
    test_experience_5y_2y_senior()
    test_experience_less_2y()
    test_income_above_threshold()
    test_income_below_threshold()
    test_talent_list_match()
    test_overseas_experience()
    test_spouse()
    test_achievement_based()
    test_full_assessment_high_achiever()
    print("✅ QMAS 测试全部通过!")
