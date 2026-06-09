import os
from google import genai
from google.genai import types

# Component 5: model routing — Flash handles classification only.
# Cheap, fast, no tools needed — just pattern matching.

_CATEGORIES = {"onboarding", "offboarding", "compliance", "candidate", "general"}

_PROMPT = """\
Classify this HR request into exactly one category. Reply with ONLY the category name, nothing else.

Categories:
- onboarding  : new hire setup, IT access, day-1 checklist, starting someone
- offboarding : exit process, revoking access, last day, termination
- compliance  : employment law, sick leave, contracts, working hours, legal requirements
- candidate   : finding candidates, job descriptions, interview questions, recruitment
- general     : anything else

Request: {message}"""


def route(message: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{"role": "user", "parts": [{"text": _PROMPT.format(message=message)}]}],
        config=types.GenerateContentConfig(max_output_tokens=10),
    )
    category = response.text.strip().lower()
    return category if category in _CATEGORIES else "general"
