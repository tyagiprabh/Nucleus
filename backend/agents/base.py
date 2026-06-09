import os
import json
from google import genai
from google.genai import types
from typing import Generator


def _build_gemini_tools(anthropic_schemas: list):
    """Convert Anthropic-format tool schemas to Gemini Tool objects."""
    if not anthropic_schemas:
        return None

    _type_map = {
        "string": types.Type.STRING,
        "integer": types.Type.INTEGER,
        "number": types.Type.NUMBER,
        "boolean": types.Type.BOOLEAN,
        "object": types.Type.OBJECT,
    }

    declarations = []
    for schema in anthropic_schemas:
        props = {}
        for k, v in schema["input_schema"].get("properties", {}).items():
            props[k] = types.Schema(
                type=_type_map.get(v["type"], types.Type.STRING),
                description=v.get("description", ""),
            )

        declarations.append(types.FunctionDeclaration(
            name=schema["name"],
            description=schema["description"],
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties=props,
                required=schema["input_schema"].get("required", []),
            ),
        ))

    return [types.Tool(function_declarations=declarations)]


class BaseAgent:
    """
    Base class for all Nucleus agents.

    Subclasses define:
      model          — Gemini model (component 5: model routing)
      max_iterations — hard iteration ceiling (component 4: turn budget)
      system_prompt  — scoped to this agent's domain (component 1)
      tools          — Anthropic-format schemas, converted to Gemini on init (component 2)
    """

    model: str = "gemini-2.0-flash"
    max_iterations: int = 5
    system_prompt: str = ""
    tools: list = []
    name: str = ""

    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self._gemini_tools = _build_gemini_tools(self.tools)

    def run(self, messages: list, context: str = "") -> Generator[dict, None, None]:
        """
        Run the agent loop. Yields event dicts and appends all turns to
        `messages` in-place so the caller's session history stays current.

        messages — Gemini-format: [{"role": "user"|"model", "parts": [...]}]
        context  — on-demand string injected into system prompt (component 6: RAG hook)

        Yields:
          {"type": "tool",     "name": <tool_name>}
          {"type": "response", "text": <final_reply>}
          {"type": "error",    "text": <message>}
        """
        system = f"Relevant context:\n{context}\n\n{self.system_prompt}" if context else self.system_prompt

        config_kwargs = {"system_instruction": system}
        if self._gemini_tools:
            config_kwargs["tools"] = self._gemini_tools

        config = types.GenerateContentConfig(**config_kwargs)

        for _ in range(self.max_iterations):
            response = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                config=config,
            )

            if not response.candidates:
                yield {"type": "error", "text": "No response from model (possible safety filter)."}
                return

            parts = response.candidates[0].content.parts
            fc_parts = [p for p in parts if p.function_call and p.function_call.name]

            if fc_parts:
                messages.append({
                    "role": "model",
                    "parts": [
                        {"function_call": {"name": p.function_call.name, "args": dict(p.function_call.args)}}
                        for p in fc_parts
                    ],
                })

                tool_results = []
                for p in fc_parts:
                    fc = p.function_call
                    yield {"type": "tool", "name": fc.name}
                    result_str = self._execute_tool(fc.name, dict(fc.args))
                    try:
                        result_data = json.loads(result_str)
                    except Exception:
                        result_data = {"output": result_str}
                    tool_results.append({
                        "function_response": {"name": fc.name, "response": result_data}
                    })

                messages.append({"role": "user", "parts": tool_results})

            else:
                text_parts = [p.text for p in parts if hasattr(p, "text") and p.text]
                reply = "\n".join(text_parts).strip()
                messages.append({"role": "model", "parts": [{"text": reply}]})
                yield {"type": "response", "text": reply}
                return

        yield {"type": "error", "text": "Reached processing limit. Please try a more specific question."}

    def _execute_tool(self, name: str, inputs: dict) -> str:
        return json.dumps({"error": f"Tool '{name}' not implemented in {self.__class__.__name__}"})
