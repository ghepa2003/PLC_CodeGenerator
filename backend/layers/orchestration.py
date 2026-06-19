import time
import os
import logging
from datetime import datetime
from enum import Enum
from agents.nlp_processor import NLPAgent
from agents.validator import ValidatorAgent
from agents.code_generator import CodeGeneratorAgent
from agents.optimizer import OptimizerAgent
from models.ladder_model import LadderOutputSchema, Metadata, LogMessage
from utils.svg_generator import generate_ladder_svg
from utils.xml_generator import generate_plcopen_xml
from config import SPECS_DIR

logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    PARSE = "parse"
    VALIDATE = "validate"
    GENERATE = "generate"
    OPTIMIZE = "optimize"
    TEST = "test"
    RETURN = "return"

class Orchestrator:
    def __init__(self):
        self.nlp_agent = NLPAgent()
        self.validator_agent = ValidatorAgent()
        self.code_gen_agent = CodeGeneratorAgent()
        self.optimizer_agent = OptimizerAgent()

    async def execute_workflow(self, input_nl: str, plc_type: str, safety_level: str) -> dict:
        start_time = time.time()
        state = WorkflowState.PARSE
        
        # Centralized state storage
        nlp_out = {}
        validated_out = {}
        gen_out = {}
        opt_out = {}
        warnings = []
        errors = []
        clarifying_questions = []
        
        # Load glossary from specs
        glossary = ""
        glossary_path = os.path.join(SPECS_DIR, "directive_glossary.md")
        if os.path.exists(glossary_path):
            try:
                with open(glossary_path, "r", encoding="utf-8") as f:
                    glossary = f.read()
            except Exception as e:
                logger.error(f"Failed to load glossary: {e}")

        # Execute states
        while state != WorkflowState.RETURN:
            logger.info(f"Orchestration State: {state.value}")
            
            if state == WorkflowState.PARSE:
                nlp_out = await self.nlp_agent.process(input_nl, glossary=glossary)
                # Check for NLP level ambiguities
                if nlp_out.get("ambiguities"):
                    clarifying_questions.extend(nlp_out["ambiguities"])
                state = WorkflowState.VALIDATE

            elif state == WorkflowState.VALIDATE:
                validated_out = await self.validator_agent.validate(nlp_out, safety_level=safety_level)
                
                # Check validation success
                if not validated_out.get("valid", True):
                    # If invalid, stop workflow and return validation errors
                    for err in validated_out.get("errors", []):
                        errors.append(LogMessage(
                            level="ERROR",
                            code=err.get("code", "VALIDATION_FAILED"),
                            message=err.get("message", "Controlla la logica inserita."),
                            suggestions=err.get("suggestions", [])
                        ))
                    state = WorkflowState.RETURN
                else:
                    # Collect warnings
                    for warn in validated_out.get("warnings", []):
                        warnings.append(LogMessage(
                            level="WARNING",
                            code=warn.get("code", "WARNING"),
                            message=warn.get("message", ""),
                            suggestions=warn.get("suggestions", [])
                        ))
                    state = WorkflowState.GENERATE

            elif state == WorkflowState.GENERATE:
                gen_out = await self.code_gen_agent.generate(validated_out, plc_type=plc_type)
                state = WorkflowState.OPTIMIZE

            elif state == WorkflowState.OPTIMIZE:
                opt_out = await self.optimizer_agent.optimize(gen_out)
                state = WorkflowState.TEST

            elif state == WorkflowState.TEST:
                # Add optional test checks here. Currently transitions to return
                state = WorkflowState.RETURN

        # If errors occurred in validation, return early with failed status
        if errors:
            execution_time = int((time.time() - start_time) * 1000)
            return LadderOutputSchema(
                success=False,
                ladder_code="",
                visualization="",
                metadata=Metadata(
                    execution_time_ms=execution_time,
                    model_used=self.nlp_agent.default_model,
                    timestamp=datetime.utcnow().isoformat() + "Z"
                ),
                warnings=warnings,
                errors=errors,
                clarifying_questions=clarifying_questions
            ).model_dump()

        # Extract rungs and variables for metrics
        rungs = validated_out.get("validated_rungs", [])
        variables = validated_out.get("validated_variables", [])

        # Pass the validated IR to SVG generator (note: SVG generator needs an update later)
        # We will pass rungs directly
        svg_code = generate_ladder_svg(rungs)

        execution_time = int((time.time() - start_time) * 1000)
        
        # Calculate metrics
        total_rungs = len(rungs)
        total_contacts = sum(len(rung.get("conditions", [])) for rung in rungs)
        total_coils = sum(len(rung.get("actions", [])) for rung in rungs)

        # Calculate a mock complexity score
        complexity = min(1.0, (total_rungs * 0.15) + (total_contacts * 0.05))

        # Final ST code could be combined with variable declarations
        final_code = ""
        var_decls = gen_out.get("variable_declarations", "")
        body_code = opt_out.get("optimized_code", gen_out.get("ladder_code", ""))
        
        if var_decls:
            final_code += f"{var_decls}\n\n"
        final_code += body_code

        # Add optimizer notes to warnings
        for opt in opt_out.get("optimizations_made", []):
            warnings.append(LogMessage(
                level="INFO",
                code="OPTIMIZATION_APPLIED",
                message=f"Ottimizzazione applicata: {opt}"
            ))

        # Generate CODESYS XML
        xml_codesys = generate_plcopen_xml(body_code, var_decls)

        return LadderOutputSchema(
            success=True,
            ladder_code=final_code,
            visualization=svg_code,
            metadata=Metadata(
                total_rungs=total_rungs,
                total_contacts=total_contacts,
                total_coils=total_coils,
                complexity_score=round(complexity, 2),
                execution_time_ms=execution_time,
                model_used=f"{self.nlp_agent.default_model} + {self.code_gen_agent.default_model}",
                timestamp=datetime.utcnow().isoformat() + "Z"
            ),
            warnings=warnings,
            errors=[],
            clarifying_questions=clarifying_questions,
            xml_codesys=xml_codesys
        ).model_dump()
