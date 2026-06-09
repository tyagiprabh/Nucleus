from agents.onboarding import OnboardingAgent
from agents.offboarding import OffboardingAgent
from agents.compliance import ComplianceAgent
from agents.candidate import CandidateAgent
from agents.general import GeneralAgent

AGENTS = {
    "onboarding":  OnboardingAgent(),
    "offboarding": OffboardingAgent(),
    "compliance":  ComplianceAgent(),
    "candidate":   CandidateAgent(),
    "general":     GeneralAgent(),
}


def get_agent(name: str) -> "BaseAgent":
    return AGENTS.get(name, AGENTS["general"])
