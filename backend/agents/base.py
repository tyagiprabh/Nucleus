import json
import anthropic
from typing import Generator


class BaseAgent:
    """
    Base class for all Nucleus agents.

    Subclasses define:
      model          — which Claude model to use (component 5: model routing)
      max_iterations — hard iteration ceiling (component 4: turn budget)
      system_prompt  — scoped to this agent's domain only (component 1)
      tools          — only the tools this agent needs (component 2)
    """

    model: str = "claude-sonnet-4-6"
    max_iterations: int = 5
    system_prompt: str = ""
    tools: list = []
    name: str = ""

    def __init__(self):
        self.client = anthropic.Anthropic()

    def run(self, messages: list, context: str = "") -> Generator[dict, None, None]:
        """
        Run the agent loop. Yields SSE event dicts and appends all turns to
        `messages` in-place so the caller's session history stays current.

        context — on-demand string injected at the top of the system prompt
                  (component 6: RAG hook — pass retrieved docs here).
        Yields:
          {"type": "tool",     "name": <tool_name>}
          {"type": "response", "text": <final_reply>}
          {"type": "error",    "text": <message>}
        """
        system = f"Relevant context:\n{context}\n\n{self.system_prompt}" if context else self.system_prompt
        tool_kwargs = {"tools": self.tools} if self.tools else {}

        for _ in range(self.max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system,
                messages=messages,
                **tool_kwargs,
            )

            assistant_turn = {"role": "assistant", "content": self._serialize(response.content)}
            messages.append(assistant_turn)

            if response.stop_reason == "end_turn":
                reply = next((b.text for b in response.content if hasattr(b, "text")), "")
                yield {"type": "response", "text": reply}
                return

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        yield {"type": "tool", "name": block.name}
                        result = self._execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})

        yield {"type": "error", "text": "Reached processing limit. Please try a more specific question."}

    def _execute_tool(self, name: str, inputs: dict) -> str:
        return json.dumps({"error": f"Tool '{name}' not implemented in {self.__class__.__name__}"})

    def _serialize(self, content) -> list:
        result = []
        for b in content:
            if b.type == "text":
                result.append({"type": "text", "text": b.text})
            elif b.type == "tool_use":
                result.append({"type": "tool_use", "id": b.id, "name": b.name, "input": b.input})
        return result
