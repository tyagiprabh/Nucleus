import json

# Deactivation order matters — revoke access before removing records
DEACTIVATION_ORDER = [
    {"system": "CEGID Y2", "action": "Deactivate POS user account", "priority": "immediate"},
    {"system": "Google Workspace", "action": "Suspend account, transfer Drive files to manager, set out-of-office", "priority": "immediate"},
    {"system": "NX Witness", "action": "Remove camera access", "priority": "immediate"},
    {"system": "n8n", "action": "Remove n8n user (if applicable)", "priority": "same_day"},
    {"system": "Freshservice", "action": "Deactivate agent/requester account", "priority": "same_day"},
    {"system": "Odoo", "action": "Archive employee record, keep HR data per retention policy", "priority": "same_day"},
    {"system": "AWS", "action": "Revoke IAM access (if applicable)", "priority": "immediate"},
]

COUNTRY_FINAL_STEPS = {
    "Spain": ["Issue certificado de empresa within 10 days", "Notify Seguridad Social of termination", "Calculate finiquito (severance)"],
    "Italy": ["Comunicazione di cessazione to Centro per l'Impiego", "Calculate TFR (severance fund)", "Issue CU (tax certificate) by March following year"],
    "Netherlands": ["Notify Belastingdienst", "Issue jaaropgave (annual tax statement)", "Check WW (unemployment) entitlement notice"],
    "Poland": ["Notify ZUS within 7 days", "Issue świadectwo pracy (employment certificate) on last day", "Calculate odprawa if applicable"],
    "Singapore": ["Final CPF contribution in last payroll", "Issue IR21 if employee is leaving Singapore", "Return work pass if applicable"],
    "France": ["Issue certificat de travail and reçu pour solde de tout compte on last day", "Notify URSSAF", "Calculate solde de tout compte"],
}


def generate_offboarding_checklist(employee_name: str, role: str, country: str, last_day: str) -> str:
    legal_steps = COUNTRY_FINAL_STEPS.get(country, ["Check local employment law for termination requirements"])

    checklist = {
        "employee": {
            "name": employee_name,
            "role": role,
            "country": country,
            "last_day": last_day,
        },
        "access_revocation": DEACTIVATION_ORDER,
        "data_retention_note": "Keep HR records for 5 years (EU GDPR minimum). Archive, do not delete.",
        "legal_final_steps": legal_steps,
        "exit_interview": [
            "Schedule 30-min exit interview with HR",
            "Send exit survey link",
            "Document reason for departure",
        ],
        "equipment_return": [
            "Laptop / tablet",
            "Store keys / access cards",
            "Uniform",
            "Any CEGID hardware (card reader, scanner)",
        ],
        "knowledge_transfer": [
            "Document open tasks and hand over to colleague",
            "Share passwords stored in personal accounts (use company password manager)",
            "Update store procedures if employee owned any documentation",
        ],
    }

    return json.dumps(checklist, indent=2)
