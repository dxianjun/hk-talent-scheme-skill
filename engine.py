"""
HK Talent Scheme - 推理引擎 (Rule Engine)
零 LLM 依赖，纯硬编码规则，确保政策引用准确率 100%
"""

import json
import os
from typing import Dict, List, Optional, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")


def _load_json(rel_path: str) -> dict:
    with open(os.path.join(KNOWLEDGE_DIR, rel_path), "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────
# 数据加载（惰性加载）
# ──────────────────────────────────────────────

def load_scoring_rules() -> dict:
    return _load_json("qmas/scoring_rules.json")


def load_talent_list() -> dict:
    return _load_json("qmas/talent_list.json")


def load_qmas_faq() -> dict:
    return _load_json("qmas/faq.json")


def load_ttps_categories() -> dict:
    return _load_json("ttps/category_rules.json")


def load_ttps_universities() -> dict:
    return _load_json("ttps/qualifying_universities.json")


def load_ttps_faq() -> dict:
    return _load_json("ttps/faq.json")


def load_asmtp_rules() -> dict:
    return _load_json("asmtp/qualification_rules.json")


def load_asmtp_faq() -> dict:
    return _load_json("asmtp/faq.json")


def load_glossary() -> dict:
    return _load_json("common/glossary.json")


# ──────────────────────────────────────────────
# QMAS 优才计分器
# ──────────────────────────────────────────────

class QMASScorer:
    """综合计分制 - 12项评核准则评估"""

    def __init__(self):
        self.rules = load_scoring_rules()

    def evaluate_age(self, age: int) -> dict:
        """评估年龄准则（准则1）"""
        try:
            age = int(age)
        except (ValueError, TypeError):
            return {"qualified": False, "reason": "年龄格式无效", "criterion_id": 1}
        if age < 18:
            return {"qualified": False, "reason": "申请人必须年满18岁", "criterion_id": 1}
        if 18 <= age <= 39:
            return {"qualified": True, "result": "18-39岁", "criterion_id": 1}
        elif 40 <= age <= 44:
            return {"qualified": True, "result": "40-44岁", "criterion_id": 1}
        elif 45 <= age <= 50:
            return {"qualified": True, "result": "45-50岁", "criterion_id": 1}
        else:
            return {"qualified": False, "result": "51岁及以上", "criterion_id": 1}

    def evaluate_education(self, highest_degree: str, degree_count: int = 1, is_stem: bool = False) -> dict:
        """评估学历/专业资格（准则2）"""
        result = {"criterion_id": 2, "is_stem": is_stem}
        if highest_degree == "phd":
            result["qualified"] = True
            result["result"] = "博士学位"
        elif highest_degree == "master":
            result["qualified"] = True
            result["result"] = "硕士学位"
        elif highest_degree == "bachelor" and degree_count >= 2:
            result["qualified"] = True
            result["result"] = "双重学士学位"
        elif highest_degree == "bachelor":
            result["qualified"] = False
            result["result"] = "仅持有学士学位"
        else:
            result["qualified"] = False
            result["result"] = "无认可大学学位"
        if result["qualified"] and is_stem and highest_degree in ("phd", "master"):
            result["note"] = "STEM科目硕士/博士学位，可能获得额外考虑"
        return result

    def evaluate_language(self, chinese_proficient: bool, english_proficient: bool) -> dict:
        """评估语言能力（准则3）"""
        if chinese_proficient and english_proficient:
            return {"qualified": True, "result": "具备良好中英文能力", "criterion_id": 3}
        elif chinese_proficient or english_proficient:
            return {"qualified": True, "result": "具备良好中文或英文能力（其中一种）", "criterion_id": 3}
        else:
            return {"qualified": False, "result": "不具备良好中文或英文能力", "criterion_id": 3}

    def evaluate_experience(self, total_years: int, senior_years: int = 0) -> dict:
        """评估工作经验（准则4）"""
        if total_years >= 10 and senior_years >= 5:
            return {"qualified": True, "result": "不少于10年经验，其中至少5年高级职位", "criterion_id": 4}
        elif total_years >= 10 and senior_years >= 2:
            return {"qualified": True, "result": "不少于10年经验，其中至少2年高级职位", "criterion_id": 4}
        elif total_years >= 5 and senior_years >= 2:
            return {"qualified": True, "result": "不少于5年经验，其中至少2年高级职位", "criterion_id": 4}
        elif total_years >= 5:
            return {"qualified": True, "result": "不少于5年经验", "criterion_id": 4}
        elif total_years >= 2:
            return {"qualified": True, "result": "不少于2年经验", "criterion_id": 4}
        else:
            return {"qualified": False, "result": "少于2年经验", "criterion_id": 4}

    def evaluate_income(self, annual_income_hkd: float) -> dict:
        """评估年收入（准则5）"""
        if annual_income_hkd >= 1_000_000:
            return {"qualified": True, "result": f"年收入达港币{annual_income_hkd:,.0f}元", "criterion_id": 5}
        else:
            return {"qualified": False, "result": f"年收入低于港币100万元", "criterion_id": 5}

    def evaluate_professional_qualifications(self, num_qualifications: int, in_talent_list: bool = False) -> dict:
        """评估专业资格（准则6）"""
        if num_qualifications >= 2 and in_talent_list:
            return {"qualified": True, "result": "持有2个或以上专业资格且属于人才清单专业", "criterion_id": 6}
        elif num_qualifications >= 2:
            return {"qualified": True, "result": "持有2个或以上专业资格", "criterion_id": 6}
        elif num_qualifications >= 1 and in_talent_list:
            return {"qualified": True, "result": "持有1个专业资格且属于人才清单专业", "criterion_id": 6}
        elif num_qualifications >= 1:
            return {"qualified": True, "result": "持有1个专业资格", "criterion_id": 6}
        else:
            return {"qualified": False, "result": "无专业资格", "criterion_id": 6}

    def evaluate_talent_list(self, matches_talent_list: bool) -> dict:
        """评估人才清单（准则7）"""
        if matches_talent_list:
            return {"qualified": True, "result": "符合人才清单要求", "criterion_id": 7}
        else:
            return {"qualified": False, "result": "不符合人才清单要求", "criterion_id": 7}

    def evaluate_business_ownership(self, business_profit_hkd: Optional[float] = None) -> dict:
        """评估业务所有权（准则8）"""
        if business_profit_hkd is None:
            return {"qualified": False, "result": "并非拥有业务", "criterion_id": 8}
        if business_profit_hkd >= 5_000_000:
            return {"qualified": True, "result": f"企业年利润达港币{business_profit_hkd:,.0f}元", "criterion_id": 8}
        elif business_profit_hkd >= 1_000_000:
            return {"qualified": True, "result": f"企业年利润达港币{business_profit_hkd:,.0f}元", "criterion_id": 8}
        else:
            return {"qualified": False, "result": "企业利润未达港币100万元", "criterion_id": 8}

    def evaluate_well_known_company(self, years_at_wellknown: int) -> dict:
        """评估知名企业/跨国公司工作经验（准则9）"""
        if years_at_wellknown >= 3:
            return {"qualified": True, "result": f"拥有不少于3年知名企业/跨国公司经验", "criterion_id": 9}
        else:
            return {"qualified": False, "result": f"少于3年知名企业/跨国公司经验", "criterion_id": 9}

    def evaluate_overseas_experience(self, years_overseas: int) -> dict:
        """评估海外工作经验（准则10）"""
        if years_overseas >= 2:
            return {"qualified": True, "result": f"拥有不少于2年海外工作经验", "criterion_id": 10}
        else:
            return {"qualified": False, "result": f"少于2年海外工作经验或没有海外经验", "criterion_id": 10}

    def evaluate_international_achievements(self, has_achievements: bool) -> dict:
        """评估国际认可成就（准则11）"""
        if has_achievements:
            return {"qualified": True, "result": "在专业领域取得国际认可成就", "criterion_id": 11}
        else:
            return {"qualified": False, "result": "无国际认可成就", "criterion_id": 11}

    def evaluate_spouse(self, spouse_has_degree: bool, spouse_accompanying: bool) -> dict:
        """评估配偶条件（准则12）"""
        if spouse_accompanying and spouse_has_degree:
            return {"qualified": True, "result": "随行配偶具有大学学位或以上学历", "criterion_id": 12}
        elif spouse_accompanying and not spouse_has_degree:
            return {"qualified": False, "result": "随行配偶学历低于大学学位", "criterion_id": 12}
        else:
            return {"qualified": False, "result": "无随行配偶", "criterion_id": 12}

    def evaluate_achievement_based(self, has_international_award: bool, has_industry_contribution: bool) -> dict:
        """成就计分制评估"""
        if has_international_award or has_industry_contribution:
            return {
                "qualified": True,
                "result": "符合成就计分制要求",
                "details": {
                    "award": has_international_award,
                    "contribution": has_industry_contribution
                }
            }
        return {"qualified": False, "result": "不符合成就计分制要求"}

    def full_assessment(self, profile: dict) -> dict:
        """完整优才评估"""
        results = []
        total_criteria = 12
        met_criteria = 0

        # 准则1: 年龄
        r = self.evaluate_age(profile.get("age", 0))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则2: 学历
        r = self.evaluate_education(
            profile.get("highest_degree", ""),
            profile.get("degree_count", 1),
            profile.get("is_stem", False)
        )
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则3: 语言
        r = self.evaluate_language(
            profile.get("chinese_proficient", False),
            profile.get("english_proficient", False)
        )
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则4: 工作经验
        r = self.evaluate_experience(
            profile.get("total_experience_years", 0),
            profile.get("senior_experience_years", 0)
        )
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则5: 年收入
        r = self.evaluate_income(profile.get("annual_income_hkd", 0))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则6: 专业资格
        r = self.evaluate_professional_qualifications(
            profile.get("num_professional_qualifications", 0),
            profile.get("in_talent_list_profession", False)
        )
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则7: 人才清单
        r = self.evaluate_talent_list(profile.get("matches_talent_list", False))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则8: 业务所有权
        r = self.evaluate_business_ownership(profile.get("business_profit_hkd"))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则9: 知名企业经验
        r = self.evaluate_well_known_company(profile.get("years_at_wellknown_company", 0))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则10: 海外经验
        r = self.evaluate_overseas_experience(profile.get("years_overseas", 0))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则11: 国际成就
        r = self.evaluate_international_achievements(profile.get("has_international_achievements", False))
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 准则12: 配偶条件
        r = self.evaluate_spouse(
            profile.get("spouse_has_degree", False),
            profile.get("spouse_accompanying", False)
        )
        results.append(r)
        if r["qualified"]:
            met_criteria += 1

        # 成就计分制检查
        achievement_result = self.evaluate_achievement_based(
            profile.get("has_international_award", False),
            profile.get("has_industry_contribution", False)
        )

        return {
            "plan": "QMAS",
            "assessment_type": "综合计分制" if not achievement_result["qualified"] else "成就计分制",
            "basic_requirements_met": self._check_basic_requirements(profile),
            "criteria_results": results,
            "summary": {
                "criteria_met": met_criteria,
                "criteria_total": total_criteria,
                "proportion": f"{met_criteria}/{total_criteria}"
            },
            "achievement_based": achievement_result,
            "overall_assessment": self._overall_verdict(met_criteria, total_criteria, achievement_result["qualified"])
        }

    def _check_basic_requirements(self, profile: dict) -> dict:
        rules = self.rules.get("basic_requirements", {})
        checks = {
            "age_18_plus": profile.get("age", 0) >= 18,
            "financial_capability": profile.get("financially_independent", True),
            "good_character": profile.get("good_character", True)
        }
        checks["all_met"] = all(checks.values())
        return checks

    def _overall_verdict(self, met: int, total: int, achievement_mode: bool) -> str:
        if achievement_mode:
            return "符合成就计分制要求，建议通过成就计分制申请"
        if met >= 6:
            return f"符合{met}/{total}项准则，达到基本申请门槛。符合较多评核准则将获更优先考虑。"
        elif met >= 4:
            return f"符合{met}/{total}项准则，接近门槛但未明确达标。入境处处长有绝对酌情权。"
        else:
            return f"仅符合{met}/{total}项准则，未达到基本申请门槛。"


# ──────────────────────────────────────────────
# TTPS 高才通类别判定器
# ──────────────────────────────────────────────

class TTPSEvaluator:
    """高才通 A/B/C 三类判定"""

    def __init__(self):
        self.categories = load_ttps_categories()

    def check_university(self, university_name: str) -> dict:
        """检查大学是否在合资格名单中"""
        if not university_name or not university_name.strip():
            return {"found": False, "university": university_name}
        data = load_ttps_universities()
        for region, region_data in data["universities_by_region"].items():
            for uni in region_data["universities"]:
                if university_name.lower() in uni.lower():
                    return {"found": True, "university": uni, "region": region}
        return {"found": False, "university": university_name}

    def evaluate(self, profile: dict) -> dict:
        """判定高才通类别"""
        annual_income = profile.get("annual_income_hkd", 0) or 0
        has_eligible_degree = profile.get("has_eligible_bachelor", False)
        work_experience_years = profile.get("work_experience_years", 0) or 0
        graduated_within_5_years = profile.get("graduated_within_5_years", True)
        is_local_non_graduate = profile.get("is_local_non_graduate", False)
        nationality = profile.get("nationality", "")
        country_excluded = nationality in ["Afghanistan", "Afghan", "Cuba", "Cuban", "North Korea", "North Korean",
                                           "朝鲜", "阿富汗", "古巴"]

        applicable_categories = []
        details = {}

        # A类：高收入
        if annual_income >= 2_500_000:
            applicable_categories.append({
                "category": "A",
                "name": "A类：高收入人士",
                "stay": "36个月",
                "quota": "无配额限制",
                "requirement_met": True,
                "detail": f"年收入达港币{annual_income:,.0f}元，达到250万门槛"
            })
        else:
            details["A类"] = f"年收入港币{annual_income:,.0f}元，未达250万门槛"

        # B类：合资格大学+3年经验
        uni_check = None
        if has_eligible_degree:
            uni_check = {"found": True}
        elif profile.get("university_name"):
            uni_check = self.check_university(profile["university_name"])
        else:
            uni_check = {"found": False}

        if has_eligible_degree and work_experience_years >= 3 and graduated_within_5_years:
            applicable_categories.append({
                "category": "B",
                "name": "B类：合资格大学学士+3年工作经验",
                "stay": "24个月",
                "quota": "无配额限制",
                "requirement_met": True,
                "detail": "持有合资格大学学士学位+不少于3年工作经验"
            })
        else:
            reasons = []
            if not has_eligible_degree:
                reasons.append("非合资格大学学士")
            if work_experience_years < 3:
                reasons.append(f"工作经验{work_experience_years}年，不足3年")
            if not graduated_within_5_years:
                reasons.append("毕业超过5年")
            details["B类"] = "、".join(reasons)

        # C类：合资格大学+经验少于3年
        if has_eligible_degree and work_experience_years < 3 and graduated_within_5_years:
            if is_local_non_graduate:
                details["C类"] = "C类不适用于在港修读全日制课程获得学士学位的非本地学生"
            else:
                applicable_categories.append({
                    "category": "C",
                    "name": "C类：合资格大学学士+工作经验少于3年",
                    "stay": "24个月",
                    "quota": "受年度配额限制，先到先得",
                    "requirement_met": True,
                    "detail": "持有合资格大学学士学位+工作经验少于3年"
                })

        return {
            "plan": "TTPS",
            "country_excluded": country_excluded,
            "universities_check": uni_check,
            "applicable_categories": applicable_categories,
            "details": details,
            "recommendation": "建议申请" + applicable_categories[0]["name"] if applicable_categories else "目前不符合任何类别条件",
            "has_qualifying_category": len(applicable_categories) > 0
        }


# ──────────────────────────────────────────────
# ASMTP 专才资格判定器
# ──────────────────────────────────────────────

class ASMTPEvaluator:
    """专才计划双端判定"""

    def __init__(self):
        self.rules = load_asmtp_rules()

    def evaluate_applicant(self, profile: dict) -> dict:
        """评估申请人端资格"""
        checks = []
        all_pass = True

        # 1. 无犯罪
        no_criminal = profile.get("no_criminal_record", True)
        checks.append({
            "check": "无严重犯罪记录",
            "pass": no_criminal,
            "detail": "通过" if no_criminal else "有犯罪记录"
        })
        if not no_criminal:
            all_pass = False

        # 2. 学历/资历
        has_degree = profile.get("has_bachelor_degree", False)
        has_alternative_qualifications = profile.get("has_alternative_qualifications", False)
        edu_pass = has_degree or has_alternative_qualifications
        checks.append({
            "check": "教育背景（学士学位或等同的专业能力）",
            "pass": edu_pass,
            "detail": "有学士学位" if has_degree else ("有替代资历证明" if has_alternative_qualifications else "不符合学历要求")
        })
        if not edu_pass:
            all_pass = False

        # 3. 已获聘用
        has_job_offer = profile.get("has_job_offer", False)
        checks.append({
            "check": "已确实获得香港公司聘用",
            "pass": has_job_offer,
            "detail": "已获聘用" if has_job_offer else "尚未获聘用"
        })
        if not has_job_offer:
            all_pass = False

        # 4. 工作与学历/经验相关
        job_relevant = profile.get("job_relevant_to_qualifications", True)
        checks.append({
            "check": "工作与学历或工作经验相关",
            "pass": job_relevant,
            "detail": "相关" if job_relevant else "不相关"
        })
        if not job_relevant:
            all_pass = False

        return {
            "applicant_checks": checks,
            "all_applicant_requirements_met": all_pass
        }

    def evaluate_employer(self, profile: dict) -> dict:
        """评估雇主端资格"""
        checks = []

        # 市场薪酬
        market_salary = profile.get("salary_market_rate", True)
        checks.append({
            "check": "薪酬福利与本地专才市场水平大致相同",
            "pass": market_salary,
            "detail": "符合市场水平" if market_salary else "低于市场水平"
        })

        # 本地招聘困难
        local_recruitment_difficult = profile.get("local_recruitment_difficult", True)
        checks.append({
            "check": "不能轻易觅得本地人担任该职位",
            "pass": local_recruitment_difficult,
            "detail": "确实存在招聘困难" if local_recruitment_difficult else "可找到本地人担任"
        })

        # 雇主公司成立时间
        company_age_months = profile.get("company_age_months", 36)
        if company_age_months < 12:
            has_business_plan = profile.get("has_business_plan", False)
            checks.append({
                "check": "新公司（12个月内）- 需提交业务计划",
                "pass": has_business_plan,
                "detail": "已准备业务计划" if has_business_plan else "缺少详细业务计划"
            })

        return {
            "employer_checks": checks,
            "all_employer_requirements_met": all(c["pass"] for c in checks)
        }

    def evaluate(self, profile: dict) -> dict:
        """完整专才评估"""
        applicant_result = self.evaluate_applicant(profile)
        employer_result = self.evaluate_employer(profile)

        overall = applicant_result["all_applicant_requirements_met"] and employer_result["all_employer_requirements_met"]

        return {
            "plan": "ASMTP",
            "applicant": applicant_result,
            "employer": employer_result,
            "overall_eligible": overall,
            "recommendation": "符合专才计划申请资格" if overall else "不符合全部申请资格，请查看具体未达标项"
        }


# ──────────────────────────────────────────────
# 三计划交叉对比
# ──────────────────────────────────────────────

class CrossComparer:
    """三个计划的交叉对比推荐"""

    def __init__(self):
        self.qmas = QMASScorer()
        self.ttps = TTPSEvaluator()
        self.asmtp = ASMTPEvaluator()

    def compare(self, profile: dict) -> dict:
        """对比三个计划，输出推荐排序"""
        results = {}

        # QMAS
        qmas_result = self.qmas.full_assessment(profile)
        results["QMAS"] = {
            "eligible": qmas_result["overall_assessment"].startswith("符合"),
            "assessment": qmas_result["summary"]["proportion"],
            "detail": qmas_result["overall_assessment"]
        }

        # TTPS
        ttps_result = self.ttps.evaluate(profile)
        results["TTPS"] = {
            "eligible": ttps_result["has_qualifying_category"],
            "categories": [c["name"] for c in ttps_result["applicable_categories"]],
            "detail": "可申请" + ", ".join(c["name"] for c in ttps_result["applicable_categories"]) if ttps_result["has_qualifying_category"] else "不符合任何类别"
        }

        # ASMTP
        asmtp_result = self.asmtp.evaluate(profile)
        results["ASMTP"] = {
            "eligible": asmtp_result["overall_eligible"],
            "detail": "符合" if asmtp_result["overall_eligible"] else "部分条件未满足"
        }

        # 推荐排序
        rankings = []
        if results["TTPS"]["eligible"]:
            rankings.append({
                "rank": 1,
                "plan": "TTPS 高才通计划",
                "reason": "审批较快（约4周），无需事先获聘，首次逗留24-36个月"
            })
        if results["QMAS"]["eligible"]:
            rankings.append({
                "rank": len(rankings) + 1,
                "plan": "QMAS 优才计划",
                "reason": "无需事先获聘，适合综合条件优秀的人士"
            })
        if results["ASMTP"]["eligible"]:
            rankings.append({
                "rank": len(rankings) + 1,
                "plan": "ASMTP 专才计划",
                "reason": "须有雇主担保，适合已获香港公司聘用人士"
            })

        return {
            "results": results,
            "recommendations": rankings,
            "no_plan_eligible": len(rankings) == 0
        }


# ──────────────────────────────────────────────
# FAQ 查询
# ──────────────────────────────────────────────

class FAQFinder:
    """FAQ 知识库查询"""

    @staticmethod
    def search(keyword: str) -> List[dict]:
        """在三个计划的 FAQ 中搜索匹配的问题"""
        results = []
        sources = [
            ("QMAS (优才)", load_qmas_faq()),
            ("TTPS (高才通)", load_ttps_faq()),
            ("ASMTP (专才)", load_asmtp_faq()),
        ]
        keyword = keyword.lower()
        for plan_name, faq_data in sources:
            for item in faq_data.get("faq_list", []):
                if keyword in item["question"].lower() or keyword in item["answer"].lower():
                    results.append({
                        "plan": plan_name,
                        "question": item["question"],
                        "answer": item["answer"]
                    })
        return results

    @staticmethod
    def search_glossary(keyword: str) -> List[dict]:
        """搜索术语表"""
        data = load_glossary()
        keyword = keyword.lower()
        results = []
        for term in data.get("terms", []):
            if (keyword in term["term"].lower() or
                keyword in term["chinese"].lower() or
                keyword in term["description"].lower()):
                results.append(term)
        return results
