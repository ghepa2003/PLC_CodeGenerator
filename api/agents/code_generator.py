import os
import json
import logging
from agents.base_agent import BaseAgent
from prompts.codegen_prompt import CODEGEN_SYSTEM_PROMPT
from config import SPECS_DIR

logger = logging.getLogger(__name__)

class CodeGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="code_generator",
            default_model="openrouter/free"
        )

    async def generate(self, validator_output: dict, plc_type: str = "siemens") -> dict:
        """
        Generates Structured Text IEC 61131-3 code from validated IR data.
        """
        system_prompt = CODEGEN_SYSTEM_PROMPT

        user_prompt = f"""
        Generate Structured Text code from the following validated IR data:
        {json.dumps(validator_output, indent=2)}

        PLC specifications:
        - Target PLC: {plc_type}
        """

        response_str = await self.call_model(system_prompt, user_prompt, response_format="json")

        try:
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()
            elif "```" in response_str:
                response_str = response_str.split("```")[1].split("```")[0].strip()
            return json.loads(response_str.strip(), strict=False)
        except Exception as e:
            logger.error(f"Error parsing JSON from Code Generator agent: {e}. Raw response: {response_str}")
            return {
                "ladder_code": "(* Errore di generazione del codice *)",
                "variable_declarations": "VAR\nEND_VAR"
            }

