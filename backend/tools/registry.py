from tools.candidate_research import search_candidates
from tools.onboarding import generate_onboarding_checklist
from tools.offboarding import generate_offboarding_checklist
from tools.compliance import get_country_compliance_info

# Add new tools here — one entry in TOOL_FUNCTIONS and one schema in TOOLS
TOOL_FUNCTIONS = {
    "search_candidates": search_candidates,
    "generate_onboarding_checklist": generate_onboarding_checklist,
    "generate_offboarding_checklist": generate_offboarding_checklist,
    "get_country_compliance_info": get_country_compliance_info,
}

TOOLS = [
    {
        "name": "search_candidates",
        "description": "Search LinkedIn, Indeed, and Glassdoor for job candidates matching a role and location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Job title (e.g. 'Store Manager', 'Sales Associate')"},
                "location": {"type": "string", "description": "City or country (e.g. 'Madrid', 'Amsterdam')"},
                "max_results": {"type": "integer", "description": "Max number of candidates to return (default 10)"},
            },
            "required": ["role", "location"],
        },
    },
    {
        "name": "generate_onboarding_checklist",
        "description": "Generate a complete onboarding checklist for a new Iris Galerie employee. Includes IT systems to set up, legal requirements, and a suggested day 1 schedule — specific to their role and country.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Employee role (e.g. 'Store Manager', 'Sales Associate', 'IT', 'HR')"},
                "store_location": {"type": "string", "description": "Store name or city (e.g. 'Iris Galerie Madrid')"},
                "country": {"type": "string", "description": "Country of employment (Spain, Italy, Netherlands, Poland, Singapore, France)"},
                "start_date": {"type": "string", "description": "Employee start date (e.g. '2026-06-16')"},
            },
            "required": ["role", "store_location", "country", "start_date"],
        },
    },
    {
        "name": "generate_offboarding_checklist",
        "description": "Generate a complete offboarding checklist for a departing Iris Galerie employee. Covers access revocation order, legal final steps by country, equipment return, and data retention.",
        "input_schema": {
            "type": "object",
            "properties": {
                "employee_name": {"type": "string", "description": "Full name of the departing employee"},
                "role": {"type": "string", "description": "Employee's role"},
                "country": {"type": "string", "description": "Country of employment"},
                "last_day": {"type": "string", "description": "Last day of employment (e.g. '2026-06-30')"},
            },
            "required": ["employee_name", "role", "country", "last_day"],
        },
    },
    {
        "name": "get_country_compliance_info",
        "description": "Get employment law and compliance information for a specific country where Iris Galerie operates. Covers working hours, leave, sick pay, notice periods, overtime, and jewelry-sector specific rules.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Country name (Spain, Italy, Netherlands, Poland, Singapore, France)"},
                "topic": {"type": "string", "description": "Optional: specific topic to filter on (e.g. 'sick_leave', 'overtime', 'notice_period')"},
            },
            "required": ["country"],
        },
    },
]


def execute_tool(name: str, inputs: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if not fn:
        return f'{{"error": "Unknown tool: {name}"}}'
    try:
        return fn(**inputs)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'
