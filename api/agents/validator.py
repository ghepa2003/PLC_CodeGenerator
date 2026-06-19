import os
import json
import logging
from agents.base_agent import BaseAgent
from prompts.validator_prompt import VALIDATOR_SYSTEM_PROMPT
from config import SPECS_DIR

logger = logging.getLogger(__name__)

class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="validator",
            default_model="openrouter/free"
        )

    async def validate(self, nlp_output: dict, safety_level: str = "medium") -> dict:
        """
        Validates the Intermediate Representation (IR).
        """
        system_prompt = VALIDATOR_SYSTEM_PROMPT

        user_prompt = f"""
        Validate the following parsed PLC IR data:
        {json.dumps(nlp_output, indent=2)}

        Validation rules:
        - Safety Level: {safety_level}
        """

        response_str = await self.call_model(system_prompt, user_prompt, response_format="json")

        try:
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()
            elif "```" in response_str:
                response_str = response_str.split("```")[1].split("```")[0].strip()
            return json.loads(response_str.strip(), strict=False)
        except Exception as e:
            logger.error(f"Error parsing JSON from Validator agent: {e}. Raw response: {response_str}")
            return {
                "valid": False,
                "validated_variables": nlp_output.get("variables", []),
                "validated_rungs": nlp_output.get("rungs", []),
                "warnings": [],
                "errors": [
                    {
                        "level": "ERROR",
                        "code": "VALIDATOR_JSON_ERROR",
                        "message": "Impossibile elaborare i dati di validazione."
                    }
                ]
            }

