import json

SCHEMA = {
    "name": "generate_onboarding_checklist",
    "description": "Generate a complete onboarding checklist for a new Iris Galerie employee. Includes IT systems to set up, legal requirements, and a suggested day-1 schedule — specific to their role and country.",
    "input_schema": {
        "type": "object",
        "properties": {
            "role":           {"type": "string", "description": "Employee role (e.g. 'Store Manager', 'Sales Associate')"},
            "store_location": {"type": "string", "description": "Store city (e.g. 'Madrid', 'Amsterdam')"},
            "country":        {"type": "string", "description": "Country: Spain, Italy, Netherlands, Poland, Singapore, France"},
            "start_date":     {"type": "string", "description": "Start date (e.g. '2026-06-16')"},
        },
        "required": ["role", "store_location", "country", "start_date"],
    },
}

# Systems required per role at Iris Galerie
ROLE_SYSTEMS = {
    "store_manager":   ["CEGID Y2 (store + manager permissions)", "Google Workspace", "Freshservice", "NX Witness cameras", "Odoo HR"],
    "sales_associate": ["CEGID Y2 (cashier permissions)", "Google Workspace", "Freshservice", "NX Witness cameras"],
    "it":              ["CEGID Y2 (admin)", "Google Workspace (admin)", "Freshservice (agent)", "NX Witness (admin)", "Odoo (admin)", "n8n", "AWS access"],
    "hr":              ["Google Workspace", "Freshservice", "Odoo HR (full access)"],
    "back_office":     ["CEGID Y2 (back office)", "Google Workspace", "Freshservice", "Odoo"],
    "default":         ["Google Workspace", "Freshservice"],
}

# Country-specific legal requirements
COUNTRY_REQUIREMENTS = {
    "Spain": {
        "probation_months": 6,
        "mandatory_briefings": ["GDPR / LOPD data protection", "Health & safety (PRL)", "Anti-money laundering (jewelry-specific)"],
        "social_registration": "Register employee with Seguridad Social before day 1",
        "contract_note": "Contrato de trabajo must be registered with SEPE within 10 days",
    },
    "Italy": {
        "probation_months": 6,
        "mandatory_briefings": ["GDPR data protection", "Health & safety (D.Lgs 81/08)", "Privacy policy"],
        "social_registration": "INPS registration required before start date",
        "contract_note": "Comunicazione di assunzione to Centro per l'Impiego within 24h of start",
    },
    "Netherlands": {
        "probation_months": 2,
        "mandatory_briefings": ["GDPR / AVG data protection", "Arbo (working conditions) briefing"],
        "social_registration": "Register with Belastingdienst (tax authority)",
        "contract_note": "Arbeidsovereenkomst — max 2 months probation for contracts < 6 months",
    },
    "Poland": {
        "probation_months": 3,
        "mandatory_briefings": ["BHP safety training (mandatory before work starts)", "GDPR / RODO", "Fire safety briefing"],
        "social_registration": "ZUS registration within 7 days of start",
        "contract_note": "Umowa o pracę — BHP training certificate required before employee can work",
    },
    "Singapore": {
        "probation_months": 3,
        "mandatory_briefings": ["PDPA (Personal Data Protection Act)", "Workplace Safety & Health", "MOM employment notice"],
        "social_registration": "CPF contributions from first payroll",
        "contract_note": "Employment contract must comply with Employment Act (MOM)",
    },
    "France": {
        "probation_months": 2,
        "mandatory_briefings": ["RGPD data protection", "Sécurité au travail", "Règlement intérieur"],
        "social_registration": "DPAE (Déclaration Préalable à l'Embauche) before day 1",
        "contract_note": "Contrat de travail — DPAE mandatory, registered with URSSAF",
    },
}


def generate_onboarding_checklist(role: str, store_location: str, country: str, start_date: str) -> str:
    role_key = role.lower().replace(" ", "_")
    systems = ROLE_SYSTEMS.get(role_key, ROLE_SYSTEMS["default"])
    legal = COUNTRY_REQUIREMENTS.get(country, {
        "probation_months": 3,
        "mandatory_briefings": ["GDPR data protection", "Health & safety"],
        "social_registration": "Check local requirements",
        "contract_note": "Verify local employment law",
    })

    checklist = {
        "employee": {
            "role": role,
            "store": store_location,
            "country": country,
            "start_date": start_date,
        },
        "it_setup": {
            "accounts_to_create": systems,
            "estimated_setup_time": f"{len(systems) * 30} minutes",
        },
        "legal_before_day_1": {
            "social_registration": legal["social_registration"],
            "contract_note": legal["contract_note"],
            "probation_period": f"{legal['probation_months']} months",
        },
        "mandatory_briefings_on_day_1": legal["mandatory_briefings"],
        "suggested_day_1_schedule": [
            "09:00 — Welcome meeting with manager",
            "10:00 — IT setup (accounts, credentials)",
            "11:30 — Store tour + team introductions",
            "13:00 — Lunch with team",
            "14:00 — Mandatory briefings",
            "16:00 — CEGID Y2 / systems training",
            "17:00 — Q&A + wrap up",
        ],
    }

    return json.dumps(checklist, indent=2)
