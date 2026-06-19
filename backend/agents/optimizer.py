import os
import json
import logging
from agents.base_agent import BaseAgent
from config import SPECS_DIR

logger = logging.getLogger(__name__)

class OptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="optimizer",
            default_model="openrouter/free"
        )
        self.spec_file = os.path.join(SPECS_DIR, "executive_optimizer.md")

    async def optimize(self, generator_output: dict) -> dict:
        """
        Optimizes Structured Text and logic rungs.
        """
        system_prompt = ""
        if os.path.exists(self.spec_file):
            try:
                with open(self.spec_file, "r", encoding="utf-8") as f:
                    system_prompt = f.read()
            except Exception as e:
                logger.error(f"Failed to read Optimizer agent spec: {e}")
        
        if not system_prompt:
            system_prompt = "You are a PLC code optimizer. Simplify Structured Text expressions to minimize contacts and redundancy."

        user_prompt = f"""
        Optimize the following generated PLC Structured Text code:
        {json.dumps(generator_output, indent=2)}

        Return a JSON object containing the optimized Structured Text and a list of changes made.
        """

        response_str = await self.call_model(system_prompt, user_prompt, response_format="json")

        try:
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()
            elif "```" in response_str:
                response_str = response_str.split("```")[1].split("```")[0].strip()
                
            return json.loads(response_str.strip())
        except Exception as e:
            logger.error(f"Error parsing JSON from Optimizer agent: {e}. Raw response: {response_str}")
            return {
                "optimized_code": generator_output.get("ladder_code", ""),
                "optimizations_made": []
            }
