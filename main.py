"""
HK Talent Scheme Skill - 主入口编排
使用方法: python3 main.py "我想申请高才通，年薪300万"
"""

import sys
import json
from engine import (
    QMASScorer, TTPSEvaluator, ASMTPEvaluator,
    CrossComparer, FAQFinder
)


def format_qmas_result(result: dict) -> str:
    """格式化优才评估结果为可读文本"""
    lines = []
    lines.append("## 📋 优才计划 (QMAS) 评估结果\n")

    # 基本要求
    basics = result.get("basic_requirements_met", {})
    lines.append("### 基本要求")
    for k, v in basics.items():
        if k == "all_met":
            continue
        label = {"age_18_plus": "年龄≥18岁", "financial_capability": "财政能力", "good_character": "良好品格"}
        check = "✅" if v else "❌"
        lines.append(f"- {check} {label.get(k, k)}")
    lines.append("")

    # 12项准则
    lines.append("### 12项评核准则")
    for r in result.get("criteria_results", []):
        cid = r.get("criterion_id", "?")
        icon = "✅" if r.get("qualified") else "❌"
        lines.append(f"- **准则{cid}**: {icon} {r.get('result', '-')}")
    lines.append("")

    # 总结
    summary = result.get("summary", {})
    lines.append(f"### 总结")
    lines.append(f"- 达标准则: **{summary.get('criteria_met', 0)}/{summary.get('criteria_total', 12)}**")
    lines.append(f"- 总体评估: {result.get('overall_assessment', '-')}")

    # 成就计分制
    ach = result.get("achievement_based", {})
    if ach.get("qualified"):
        lines.append(f"- ✅ 同时符合成就计分制要求")

    return "\n".join(lines)


def format_ttps_result(result: dict) -> str:
    """格式化高才通评估结果"""
    lines = []
    lines.append("## 📋 高才通计划 (TTPS) 评估结果\n")

    if result.get("country_excluded"):
        lines.append("⚠️ **提醒**: 您的国籍可能不适用于本计划（阿富汗、古巴、朝鲜国民除外）\n")

    cats = result.get("applicable_categories", [])
    if cats:
        for c in cats:
            lines.append(f"✅ **{c['category']}类**: {c['name']}")
            lines.append(f"  - 逗留期限: {c['stay']}")
            lines.append(f"  - 配额: {c['quota']}")
            lines.append(f"  - 详情: {c['detail']}")
    else:
        lines.append("❌ 目前不符合任何高才通类别条件")
        for plan, reason in result.get("details", {}).items():
            lines.append(f"  - {plan}: {reason}")

    return "\n".join(lines)


def format_asmtp_result(result: dict) -> str:
    """格式化专才评估结果"""
    lines = []
    lines.append("## 📋 专才计划 (ASMTP) 评估结果\n")

    lines.append("### 申请人条件")
    for check in result.get("applicant", {}).get("applicant_checks", []):
        icon = "✅" if check["pass"] else "❌"
        lines.append(f"- {icon} {check['check']}: {check['detail']}")

    lines.append("\n### 雇主条件")
    for check in result.get("employer", {}).get("employer_checks", []):
        icon = "✅" if check["pass"] else "❌"
        lines.append(f"- {icon} {check['check']}: {check['detail']}")

    lines.append(f"\n### 总体")
    icon = "✅" if result.get("overall_eligible") else "❌"
    lines.append(f"- {icon} {result.get('recommendation', '-')}")

    return "\n".join(lines)


def format_comparison(result: dict) -> str:
    """格式化三计划对比结果"""
    lines = []
    lines.append("## 🔄 三计划交叉对比\n")

    res = result.get("results", {})
    for plan, data in res.items():
        icon = "✅" if data["eligible"] else "❌"
        lines.append(f"### {icon} {plan}")
        lines.append(f"  - 详情: {data.get('detail', '-')}")
        if "categories" in data and data["categories"]:
            for cat in data["categories"]:
                lines.append(f"    - {cat}")
        lines.append("")

    if result.get("no_plan_eligible"):
        lines.append("⚠️ 目前您不符合以上三个计划的申请条件。建议咨询专业移民顾问。\n")
    else:
        lines.append("### 🏆 推荐排序\n")
        for rec in result.get("recommendations", []):
            lines.append(f"**第{rec['rank']}优先**: {rec['plan']}")
            lines.append(f"  - 理由: {rec['reason']}")

    return "\n".join(lines)


def intent_router(query: str) -> str:
    """意图路由 - 判断用户想查询什么"""
    q = query.lower()

    # 检测对比意图
    if any(kw in q for kw in ["对比", "比较", "recommend", "哪个好", "适合我", "选哪个", "推荐"]):
        return "compare"

    # 检测优才
    if any(kw in q for kw in ["优才", "qmas", "综合计分", "成就计分"]):
        return "qmas"

    # 检测高才通
    if any(kw in q for kw in ["高才", "ttps", "高端人才"]):
        return "ttps"

    # 检测专才
    if any(kw in q for kw in ["专才", "asmtp", "输入内地人才"]):
        return "asmtp"

    # FAQ/术语查询
    if any(kw in q for kw in ["faq", "常见问题", "什么是", "意思", "术语", "glossary"]):
        return "faq"

    # 默认：对比
    return "compare"


def main():
    if len(sys.argv) < 2:
        print("用法: python3 main.py \"您的查询\"")
        print("示例: python3 main.py \"我想申请高才通，年薪300万，有合资格大学学士学位\"")
        sys.exit(1)

    query = sys.argv[1]

    # 解析意图
    intent = intent_router(query)

    # 从查询中提取数值信息（简化版，实际生产可用NLP）
    import re

    # 提取年龄
    age_match = re.search(r'(\d+)\s*岁', query)
    age = int(age_match.group(1)) if age_match else 35

    # 提取年薪（万）
    income_match = re.search(r'(\d+)\s*万', query)
    annual_income = float(income_match.group(1)) * 10000 if income_match else 0

    # 提取工作经验
    exp_match = re.search(r'(\d+)\s*年经验', query)
    work_exp = int(exp_match.group(1)) if exp_match else 0

    # 构建profile
    profile = {
        "age": age,
        "highest_degree": "master",
        "degree_count": 1,
        "chinese_proficient": True,
        "english_proficient": True,
        "total_experience_years": work_exp,
        "senior_experience_years": max(0, work_exp - 2),
        "annual_income_hkd": annual_income,
        "num_professional_qualifications": 1,
        "in_talent_list_profession": False,
        "matches_talent_list": False,
        "has_eligible_bachelor": True,
        "work_experience_years": work_exp,
        "graduated_within_5_years": True,
        "has_job_offer": False,
    }

    print(f"🔍 意图: {intent}")
    print(f"👤 解析的申请画像: 年龄{age}岁, 年收入{annual_income:,.0f}港币, {work_exp}年经验\n")

    if intent == "qmas":
        scorer = QMASScorer()
        result = scorer.full_assessment(profile)
        print(format_qmas_result(result))

    elif intent == "ttps":
        evaluator = TTPSEvaluator()
        result = evaluator.evaluate(profile)
        print(format_ttps_result(result))

    elif intent == "asmtp":
        profile["has_job_offer"] = "聘用" in query or "offer" in query.lower()
        evaluator = ASMTPEvaluator()
        result = evaluator.evaluate(profile)
        print(format_asmtp_result(result))

    elif intent == "faq":
        keyword = query.replace("什么是", "").replace("意思", "").replace("术语", "").strip()
        faq_results = FAQFinder.search(keyword)
        gloss_results = FAQFinder.search_glossary(keyword)
        print("## 📖 FAQ / 术语查询结果\n")
        if faq_results:
            print("### FAQ 匹配：")
            for item in faq_results[:5]:
                print(f"- [{item['plan']}] {item['question']}")
        if gloss_results:
            print("\n### 术语匹配：")
            for item in gloss_results[:5]:
                print(f"- **{item['term']}** ({item['chinese']}): {item['description']}")
        if not faq_results and not gloss_results:
            print("未找到匹配结果。")

    else:  # compare
        comparer = CrossComparer()
        result = comparer.compare(profile)
        print(format_comparison(result))


if __name__ == "__main__":
    main()
