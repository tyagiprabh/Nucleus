# Agent: Router — Intent Classifier

## Role
Not a persona — a silent classifier. The router runs before any specialist agent and decides which one should handle the request. It never responds to the user directly.

## Model
`claude-haiku-4-5` — classification requires no reasoning, just pattern matching. At ~0.001x the cost of Sonnet per call, this is the biggest cost lever in the system.

## Categories
| Category | Routes to | Triggers |
|----------|-----------|----------|
| `onboarding` | Aria | new hire, IT setup, day-1, start date, access setup |
| `offboarding` | Felix | exit, last day, termination, revoke access, leaving |
| `compliance` | Lex | employment law, sick leave, notice period, overtime, legal |
| `candidate` | Scout | find candidates, job description, interview questions, recruitment |
| `general` | Nucleus | everything else |

## Fallback
Any unrecognised or ambiguous classification defaults to `general` (Nucleus). It never fails silently.

## Why it exists
Without a router, every request would go to a general agent with all tools loaded — wasting context tokens on irrelevant tool schemas and increasing the chance of wrong tool calls. The router keeps each agent lean.
