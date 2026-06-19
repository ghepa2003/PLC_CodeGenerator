import os
import json
import logging
from agents.base_agent import BaseAgent
from prompts.nlp_prompt import NLP_SYSTEM_PROMPT
from config import SPECS_DIR

logger = logging.getLogger(__name__)

class NLPAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="nlp_processor",
            default_model="openrouter/free"
        )

    async def process(self, input_nl: str, glossary: str = "") -> dict:
        """
        Parses natural language input to structured intent objects (IR).
        """
        system_prompt = NLP_SYSTEM_PROMPT

        user_prompt = f"""
        Process the following natural language input:
        "{input_nl}"

        PLC Glossary context:
        {glossary}
        """

        response_str = await self.call_model(system_prompt, user_prompt, response_format="json")
        
        # Parse output to dict
        try:
            # Clean possible markdown wrap (if model did not follow response_format strictly)
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()
            elif "```" in response_str:
                response_str = response_str.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_str.strip())
        except Exception as e:
            logger.error(f"Error parsing JSON from NLP agent response: {e}. Raw response: {response_str}")
            return {
                "variables": [],
                "rungs": [],
                "clarifying_questions": ["Fallita l'estrazione strutturata dei dati logici."]
            }

