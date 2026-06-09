import anthropic

# Component 5: model routing — Haiku handles classification only.
# Costs ~0.001x of a Sonnet call. No tools, 10 tokens max.

_CATEGORIES = {"onboarding", "offboarding", "compliance", "candidate", "general"}

_PROMPT = """\
Classify this HR request into exactly one category. Reply with ONLY the category name.

Categories:
- onboarding  : new hire setup, IT access, day-1 checklist, starting someone
- offboarding : exit process, revoking access, last day, termination
- compliance  : employment law, sick leave, contracts, working hours, legal requirements
- candidate   : finding candidates, job descriptions, interview questions, recruitment
- general     : anything else

Request: {message}"""


def route(message: str) -> str:
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": _PROMPT.format(message=message)}],
    )
    category = resp.content[0].text.strip().lower()
    return category if category in _CATEGORIES else "general"
