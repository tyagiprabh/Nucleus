import json

COMPLIANCE_DB = {
    "Spain": {
        "max_working_hours_per_week": 40,
        "minimum_wage_2026_monthly_eur": 1134,
        "annual_leave_days": 22,
        "sick_leave": "First 3 days: no pay (unless collective agreement). Day 4+: Social Security pays 60% up to day 20, 75% from day 21.",
        "notice_period": "Minimum 15 days for employee. Employer: 20 days salary per year worked if unfair dismissal.",
        "overtime_rules": "Max 80h/year overtime. Must be compensated in rest time or paid at minimum 1.25x rate.",
        "key_law": "Estatuto de los Trabajadores (ET)",
        "jewelry_specific": "Anti-money laundering (AML) training required for staff handling high-value transactions >€10,000.",
    },
    "Italy": {
        "max_working_hours_per_week": 40,
        "minimum_wage_2026_monthly_eur": None,
        "annual_leave_days": 20,
        "sick_leave": "INPS pays from day 4. First 3 days employer may cover per collective agreement (CCNL).",
        "notice_period": "Defined by CCNL (collective agreement). Typically 1-3 months depending on seniority.",
        "overtime_rules": "Max 250h/year. Rate defined by CCNL, typically 25-30% premium.",
        "key_law": "Codice del Lavoro + CCNL Commercio",
        "jewelry_specific": "D.Lgs 231/2001 anti-corruption compliance. AML obligations for high-value goods.",
    },
    "Netherlands": {
        "max_working_hours_per_week": 40,
        "minimum_wage_2026_monthly_eur": 2069,
        "annual_leave_days": 20,
        "sick_leave": "Employer pays 70% (min minimum wage) for up to 2 years of illness. Wet Poortwachter re-integration obligation.",
        "notice_period": "1 month (< 5 years service). Increases by 1 month per 5 years, max 4 months.",
        "overtime_rules": "No statutory rate — defined by collective agreement (CAO).",
        "key_law": "Burgerlijk Wetboek (BW) Book 7 + Wet Werk en Zekerheid",
        "jewelry_specific": "Wwft (AML) compliance for high-value goods dealers.",
    },
    "Poland": {
        "max_working_hours_per_week": 40,
        "minimum_wage_2026_monthly_pln": 4666,
        "annual_leave_days": 20,
        "sick_leave": "Employer pays first 33 days/year (14 days if over 50). ZUS pays from day 34.",
        "notice_period": "2 weeks (< 6 months), 1 month (6 months–3 years), 3 months (3+ years).",
        "overtime_rules": "Max 150h/year standard overtime. 50% premium weekdays, 100% nights/weekends.",
        "key_law": "Kodeks pracy (Labour Code)",
        "jewelry_specific": "BHP (safety) training mandatory before work starts — no exceptions. AML law applies to jewelry sector.",
    },
    "Singapore": {
        "max_working_hours_per_week": 44,
        "minimum_wage_2026": "No statutory minimum wage (except cleaning/security sectors)",
        "annual_leave_days": 7,
        "sick_leave": "14 days outpatient (< 1 year service: pro-rated). 60 days hospitalisation.",
        "notice_period": "Defined in contract. EA minimum: 1 day–4 weeks depending on service length.",
        "overtime_rules": "1.5x rate for non-managers working >44h/week. PMEs exempt from OT provisions.",
        "key_law": "Employment Act (MOM)",
        "jewelry_specific": "MAS AML requirements for high-value dealers. Precious Stones and Precious Metals Act (PSPM Act).",
    },
    "France": {
        "max_working_hours_per_week": 35,
        "minimum_wage_2026_monthly_eur": 1767,
        "annual_leave_days": 25,
        "sick_leave": "Social Security pays from day 4 (3-day waiting period). Many CCNs eliminate waiting period.",
        "notice_period": "1 month (non-cadre), 3 months (cadre). Defined by convention collective.",
        "overtime_rules": "25% premium for hours 36-43, 50% from hour 44+. Quota: 220h/year.",
        "key_law": "Code du travail + Convention Collective Commerce de Détail",
        "jewelry_specific": "Tracfin (AML) declarations required for suspicious transactions. Bijouterie-joaillerie sector has specific IDCC.",
    },
}


def get_country_compliance_info(country: str, topic: str = "general") -> str:
    info = COMPLIANCE_DB.get(country)
    if not info:
        available = list(COMPLIANCE_DB.keys())
        return json.dumps({"error": f"No data for '{country}'", "available_countries": available})

    result = {"country": country, "compliance_info": info}

    if topic != "general":
        topic_lower = topic.lower()
        filtered = {k: v for k, v in info.items() if topic_lower in k.lower() or topic_lower in str(v).lower()}
        result["compliance_info"] = filtered if filtered else info

    return json.dumps(result, indent=2)
