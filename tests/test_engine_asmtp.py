"""专才判定测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engine import ASMTPEvaluator


def test_fully_eligible():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": True,
        "has_bachelor_degree": True,
        "has_alternative_qualifications": False,
        "has_job_offer": True,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 36
    })
    assert result["overall_eligible"]


def test_no_criminal_record():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": False,
        "has_bachelor_degree": True,
        "has_alternative_qualifications": False,
        "has_job_offer": True,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 36
    })
    assert not result["overall_eligible"]


def test_no_degree_but_alternative():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": True,
        "has_bachelor_degree": False,
        "has_alternative_qualifications": True,
        "has_job_offer": True,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 36
    })
    assert result["overall_eligible"]


def test_no_job_offer():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": True,
        "has_bachelor_degree": True,
        "has_alternative_qualifications": False,
        "has_job_offer": False,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 36
    })
    assert not result["overall_eligible"]


def test_new_company_no_business_plan():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": True,
        "has_bachelor_degree": True,
        "has_alternative_qualifications": False,
        "has_job_offer": True,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 6,
        "has_business_plan": False
    })
    assert not result["overall_eligible"]


def test_new_company_with_business_plan():
    evaluator = ASMTPEvaluator()
    result = evaluator.evaluate({
        "no_criminal_record": True,
        "has_bachelor_degree": True,
        "has_alternative_qualifications": False,
        "has_job_offer": True,
        "job_relevant_to_qualifications": True,
        "salary_market_rate": True,
        "local_recruitment_difficult": True,
        "company_age_months": 6,
        "has_business_plan": True
    })
    assert result["overall_eligible"]


if __name__ == "__main__":
    test_fully_eligible()
    test_no_criminal_record()
    test_no_degree_but_alternative()
    test_no_job_offer()
    test_new_company_no_business_plan()
    test_new_company_with_business_plan()
    print("✅ ASMTP 测试全部通过!")
