import json
import logging
import re
import datetime
from openai import AsyncOpenAI
from config import OPENROUTER_API_KEY
from utils.xml_generator import generate_plcopen_xml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, agent_id: str, default_model: str):
        self.agent_id = agent_id
        self.default_model = default_model
        self.is_mock = OPENROUTER_API_KEY == "sk-or-v1-mock-key-antigravity" or not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("your_")
        
        if not self.is_mock:
            self.client = AsyncOpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.io/api/v1",
                default_headers={
                    "HTTP-Referer": "https://github.com/ghepa2003/PLC_CodeGenerator",
                    "X-Title": "PLC Code Generator"
                }
            )
        else:
            logger.info(f"Agent {self.agent_id} started in MOCK mode because no valid OpenRouter API key was detected.")

    def self_id_for_log(self) -> str:
        return self.agent_id

    async def call_model(self, system_prompt: str, user_prompt: str, response_format: str = "json") -> str:
        """
        Calls OpenRouter with the given system and user prompts.
        If in MOCK mode, uses local mock logic.
        """
        if self.is_mock:
            return self._mock_call(user_prompt)

        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            # Clean up potential markdown formatting from models
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return content
        except Exception as e:
            logger.error(f"Error calling OpenRouter for agent {self.agent_id}: {str(e)}")
            # Fallback to mock logic if the API call fails
            logger.warning("Attempting to fallback to mock response due to API error...")
            return self._mock_call(user_prompt)

    def _mock_call(self, user_prompt: str) -> str:
        """
        Dynamic Mock implementation that parses user's NL input to generate
        meaningful, custom Structured Text code, XML schema, and SVG ladder logic views.
        """
        # Try to extract JSON directly if it's Validator or CodeGen
        if "{" in user_prompt and "}" in user_prompt:
            try:
                start_idx = user_prompt.find("{")
                end_idx = user_prompt.rfind("}") + 1
                json_str = user_prompt[start_idx:end_idx]
                data = json.loads(json_str)
                # If it successfully parsed and has typical keys
                if any(k in data for k in ["variables", "rungs", "validated_variables", "validated_rungs", "entities"]):
                    return self._generate_dynamic_mock_response_from_json(data, user_prompt)
            except Exception:
                pass

        # 1. Extract natural language input for NLP Processor
        nl_input = ""
        match = re.search(r'Process the following natural language input:\s*"(.*?)"', user_prompt, re.DOTALL | re.IGNORECASE)
        if not match:
            match = re.search(r'Process this natural language input:\s*"(.*?)"', user_prompt, re.DOTALL | re.IGNORECASE)
            
        if match:
            nl_input = match.group(1).strip()
        else:
            nl_input = user_prompt.strip()

        # Parse NL input dynamically
        parsed_data = self._compile_nl_heuristics(nl_input)
        return self._generate_dynamic_mock_response_from_json(parsed_data, user_prompt)

    def _compile_nl_heuristics(self, nl_input: str) -> dict:
        """
        Analyzes the NL input text and generates structured variables and logic rules.
        """
        # Clean text
        text = nl_input.replace("\n", " ").strip()
        
        # Word extraction matching names: words with underscores or standard names
        all_words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', text)
        import string
        
        # Remove punctuation
        translator = str.maketrans('', '', string.punctuation)
        clean_input = nl_input.translate(translator)
        all_words = clean_input.split()
        
        # Stopwords to filter out
        stopwords = {
            "se", "quando", "allora", "poi", "e", "o", "oppure", "non", "con", "per", "di", "a", "da", "in", "su",
            "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "del", "al", "allo", "alla", "ai", "agli", "alle",
            "if", "then", "and", "or", "not", "with", "for", "to", "in", "on", "at", "by", "from", "of",
            "is", "are", "be", "attiva", "accendi", "spegni", "ferma", "avvia", "disattiva", "arresta",
            "premuto", "attivo", "chiuso", "aperto", "true", "false", "on", "off", "sec", "secondi", "minuti",
            "viene", "si", "accende", "gialla", "rossa", "verde", "blu", "questo", "quello", "che", "cui", "come"
        }
        
        # Candidate entities
        candidates = []
        for w in all_words:
            w_lower = w.lower()
            if w_lower not in stopwords and (len(w) > 2 or w in ["A", "B", "C"]) and not w.isdigit():
                candidates.append(w)
                
        # Deduplicate candidates while keeping order
        candidates = list(dict.fromkeys(candidates))
        
        # Classify candidates into inputs/outputs/timers
        entities = []
        inputs_list = []
        outputs_list = []
        timers_list = []
        
        for w in candidates:
            w_lower = w.lower()
            
            # Classification
            if any(x in w_lower for x in ["timer", "ritardo", "delay"]):
                e_type = "timer"
                timers_list.append(w)
            elif any(x in w_lower for x in ["motore", "pompa", "valvola", "allarme", "alarm", "led", "luce", "motor", "pump", "valve", "signal", "solenoide", "output", "actuator", "attuatore"]):
                e_type = "output_digital"
                outputs_list.append(w)
            else:
                # Default classification based on context or name
                if any(x in w_lower for x in ["temp", "pressione", "livello", "level", "press", "flow", "analogico"]):
                    e_type = "input_analog"
                else:
                    e_type = "input_digital"
                inputs_list.append(w)
                
            entities.append({
                "entity_id": w,
                "entity_name": w.replace("_", " ").title(),
                "entity_type": e_type,
                "normally_open": True
            })

        # Ensure we have at least one input and one output
        if not inputs_list:
            entities.append({
                "entity_id": "sensor_trigger",
                "entity_name": "Sensor Trigger",
                "entity_type": "input_digital",
                "normally_open": True
            })
            inputs_list.append("sensor_trigger")
        if not outputs_list:
            entities.append({
                "entity_id": "actuator_output",
                "entity_name": "Actuator Output",
                "entity_type": "output_digital",
                "normally_open": True
            })
            outputs_list.append("actuator_output")

        # Split input into rules (by periods or "se"/"if" transitions)
        sentences = re.split(r'\.|\bse\b|\bif\b', text, flags=re.IGNORECASE)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 8]
        
        intent_objects = []
        intent_count = 1
        
        # If no sentences parsed, make a single default rule linking first input to first output
        if not sentences:
            sentences = [f"attiva {outputs_list[0]} se {inputs_list[0]} premuto"]

        for sent in sentences:
            sent_lower = sent.lower()
            
            # Find output mentioned in this sentence
            target_out = None
            for out in outputs_list:
                if out.lower() in sent_lower:
                    target_out = out
                    break
            
            if not target_out:
                # Default to first output
                target_out = outputs_list[0]
                
            # Determine action: SET or RESET
            action_type = "SET"
            if any(x in sent_lower for x in ["spegni", "ferma", "disattiva", "arresta", "reset", "unlatch", "off", "chiudi"]):
                action_type = "RESET"
                
            # Find inputs mentioned in this sentence
            conditions = []
            for inp in inputs_list:
                if inp.lower() in sent_lower:
                    operator = "TRUE"
                    value = None
                    
                    # Heuristics for analog inputs comparison
                    if "input_analog" in [e["entity_type"] for e in entities if e["entity_id"] == inp]:
                        # Look for comparisons like "> 80" or "superiore a 50"
                        match_num = re.search(r'(?:>|<|=|>=|<=)\s*(\d+)', sent_lower)
                        if not match_num:
                            match_num = re.search(r'(?:superiore|maggiore|greater)\s*(?:a|di|than)?\s*(\d+)', sent_lower)
                            if match_num:
                                operator = "GT"
                                value = float(match_num.group(1))
                            else:
                                match_num = re.search(r'(?:inferiore|minore|less)\s*(?:a|di|than)?\s*(\d+)', sent_lower)
                                if match_num:
                                    operator = "LT"
                                    value = float(match_num.group(1))
                        else:
                            operator_symbol = re.search(r'(>|<|=|>=|<=)', sent_lower).group(1)
                            operator = {"&gt;": "GT", ">": "GT", "<": "LT", "=": "EQ", ">=": "GE", "<=": "LE"}.get(operator_symbol, "GT")
                            value = float(match_num.group(1))
                    else:
                        # Digital input: check for Normally Closed (NC) terms
                        if any(x in sent_lower for x in ["non", "not", "chiuso", "released", "false"]):
                            operator = "RELEASED"
                            
                    conditions.append({
                        "entity_id": inp,
                        "operator": operator,
                        "value": value
                    })
            
            # If timer block needed (e.g. contains duration)
            duration_ms = None
            match_time = re.search(r'(\d+)\s*(?:secondi|sec|seconds|s\b)', sent_lower)
            if match_time:
                duration_ms = int(match_time.group(1)) * 1000
                
            if duration_ms and target_out:
                # Create a timer block intent first
                t_name = f"timer_{target_out}"
                # Add timer entity if not exists
                if not any(e["entity_id"] == t_name for e in entities):
                    entities.append({
                        "entity_id": t_name,
                        "entity_name": f"Timer {target_out.replace('_', ' ').title()}",
                        "entity_type": "timer",
                        "normally_open": True
                    })
                
                # Rule to start timer
                intent_objects.append({
                    "intent_id": f"intent_{intent_count:03d}",
                    "intent_type": "timer_trigger",
                    "conditions": [{
                        "entity_id": target_out,
                        "operator": "TRUE",
                        "value": None
                    }],
                    "logic_gate": "AND",
                    "negations": [],
                    "action": {
                        "action_type": "SET",
                        "target_id": t_name,
                        "duration_ms": duration_ms
                    }
                })
                intent_count += 1
                
                # Rule to turn off output using timer completion
                intent_objects.append({
                    "intent_id": f"intent_{intent_count:03d}",
                    "intent_type": "conditional_activation",
                    "conditions": [{
                        "entity_id": t_name,
                        "operator": "TRUE",
                        "value": None
                    }],
                    "logic_gate": "AND",
                    "negations": [],
                    "action": {
                        "action_type": "RESET",
                        "target_id": target_out
                    }
                })
                intent_count += 1
            else:
                # Standard conditional logic activation
                # If no conditions were found, default to first input
                if not conditions:
                    conditions = [{
                        "entity_id": inputs_list[0],
                        "operator": "TRUE",
                        "value": None
                    }]
                    
                intent_objects.append({
                    "intent_id": f"intent_{intent_count:03d}",
                    "intent_type": "conditional_activation",
                    "conditions": conditions,
                    "logic_gate": "AND",
                    "negations": [],
                    "action": {
                        "action_type": action_type,
                        "target_id": target_out
                    }
                })
                intent_count += 1

        return {
            "entities": entities,
            "intent_objects": intent_objects,
            "confidence_score": 0.95,
            "ambiguities": []
        }

    def _generate_dynamic_mock_response_from_json(self, data: dict, user_prompt: str) -> str:
        """
        Creates appropriate output JSON (Validator, Code Generator, Optimizer)
        using the parsed JSON context data.
        """
        # Read from new schema if present
        variables = data.get("variables", data.get("validated_variables", []))
        rungs = data.get("rungs", data.get("validated_rungs", []))
        
        # Fallback to old schema conversion if coming from heuristics
        if not variables and "entities" in data:
            for e in data.get("entities", []):
                t_map = {
                    "input_digital": "BOOL",
                    "input_analog": "REAL",
                    "output_digital": "BOOL",
                    "timer": "BOOL",
                    "counter": "INT"
                }.get(e.get("entity_type", "input_digital"), "BOOL")
                variables.append({
                    "name": e.get("entity_id", "var"),
                    "data_type": t_map,
                    "description": e.get("entity_name", "")
                })

        if not rungs and ("intent_objects" in data or "validated_intents" in data):
            intents = data.get("intent_objects", data.get("validated_intents", []))
            for i, intent in enumerate(intents):
                conditions = []
                for c in intent.get("conditions", []):
                    conditions.append({
                        "variable": c.get("entity_id", "var"),
                        "operator": c.get("operator", "TRUE"),
                        "value": c.get("value")
                    })
                
                action = intent.get("action", {})
                act_type = action.get("action_type", "SET")
                if intent.get("intent_type") == "timer_trigger":
                    act_type = "TIMER_TON"
                
                actions = [{
                    "type": act_type,
                    "target": action.get("target_id", "output"),
                    "parameters": {"PT_ms": action.get("duration_ms")} if action.get("duration_ms") else {}
                }]
                
                rungs.append({
                    "comment": f"Rung {i+1}",
                    "logic_gate": intent.get("logic_gate", "AND"),
                    "conditions": conditions,
                    "actions": actions
                })

        # --- NLP AGENT MOCK RESPONSE ---
        if self.agent_id == "nlp_processor":
            return json.dumps({
                "variables": variables,
                "rungs": rungs,
                "clarifying_questions": []
            })
            
        # --- VALIDATOR AGENT MOCK RESPONSE ---
        elif self.agent_id == "validator":
            warnings = []
            has_pump_or_motor = any(
                any(x in v["name"].lower() for x in ["pump", "pompa", "motor", "motore"])
                for v in variables
            )
            has_estop = any("estop" in v["name"].lower() or "emergenza" in v["name"].lower() for v in variables)
            
            if has_pump_or_motor and not has_estop:
                warnings.append({
                    "level": "WARNING",
                    "code": "SAFETY_ESTOP_MISSING",
                    "message": "Nessun arresto di emergenza (E-Stop) associato alla pompa/motore. Consigliato aggiungere un contatto NC per sicurezza.",
                    "suggestions": ["Aggiungi un contatto NC 'btn_estop' in serie su ciascuna bobina."]
                })
                
            return json.dumps({
                "valid": True,
                "validated_variables": variables,
                "validated_rungs": rungs,
                "warnings": warnings,
                "errors": []
            })

        # --- CODE GENERATOR MOCK RESPONSE ---
        elif self.agent_id == "code_generator":
            var_lines = []
            timer_fb_declarations = []
            
            for v in variables:
                v_name = v["name"]
                v_type = v["data_type"]
                desc = v.get("description", "")
                var_lines.append(f"    {v_name} : {v_type}; (* {desc} *)")
                
                # Check rungs to see if it's used as a timer
                for r in rungs:
                    for act in r.get("actions", []):
                        if act.get("target") == v_name and act.get("type") in ["TIMER_TON", "TIMER_TOF"]:
                            if f"    TON_{v_name} : TON; (* Blocco funzionale Timer *)" not in timer_fb_declarations:
                                timer_fb_declarations.append(f"    TON_{v_name} : TON; (* Blocco funzionale Timer *)")

            var_decls = "VAR\n" + "\n".join(var_lines)
            if timer_fb_declarations:
                var_decls += "\n\n    (* Blocchi Funzionali Timer *)\n" + "\n".join(timer_fb_declarations)
            var_decls += "\nEND_VAR"
            
            st_rungs = []
            for idx, rung in enumerate(rungs):
                conditions = rung.get("conditions", [])
                actions = rung.get("actions", [])
                logic_gate = f" {rung.get('logic_gate', 'AND')} "
                
                cond_clauses = []
                for cond in conditions:
                    c_id = cond["variable"]
                    op = cond.get("operator", "TRUE")
                    val = cond.get("value")
                    
                    if op == "GT":
                        cond_clauses.append(f"({c_id} > {val})")
                    elif op == "LT":
                        cond_clauses.append(f"({c_id} < {val})")
                    elif op in ["RELEASED", "FALSE"]:
                        cond_clauses.append(f"NOT {c_id}")
                    else:
                        cond_clauses.append(c_id)
                        
                full_condition = logic_gate.join(cond_clauses)
                if not full_condition:
                    full_condition = "TRUE"
                    
                rung_code = []
                for act in actions:
                    target = act.get("target", "output")
                    act_type = act.get("type", "SET")
                    params = act.get("parameters", {})
                    duration = params.get("PT_ms")
                    
                    rung_code.append(f"(* Rung {idx + 1}: {rung.get('comment', '')} per {target} *)")
                    
                    if act_type in ["TIMER_TON", "TIMER_TOF"] or duration:
                        rung_code.append(f"TON_{target}(IN := {full_condition}, PT := T#{duration/1000 if duration else 10}s);")
                        rung_code.append(f"{target} := TON_{target}.Q;")
                    else:
                        if act_type == "SET":
                            rung_code.append(f"IF {full_condition} THEN")
                            rung_code.append(f"    {target} := TRUE;")
                            rung_code.append("END_IF;")
                        elif act_type == "RESET":
                            rung_code.append(f"IF {full_condition} THEN")
                            rung_code.append(f"    {target} := FALSE;")
                            rung_code.append("END_IF;")
                        else:
                            rung_code.append(f"{target} := {full_condition};")
                            
                st_rungs.append("\n".join(rung_code))

            ladder_code = "\n\n".join(st_rungs)
            
            return json.dumps({
                "ladder_code": ladder_code,
                "variable_declarations": var_decls
            })

        # --- OPTIMIZER MOCK RESPONSE ---
        elif self.agent_id == "optimizer":
            code = ""
            if isinstance(user_prompt, str):
                try:
                    start_idx = user_prompt.find("{")
                    end_idx = user_prompt.rfind("}") + 1
                    data_opt = json.loads(user_prompt[start_idx:end_idx])
                    code = data_opt.get("ladder_code", "")
                except Exception:
                    pass
            
            return json.dumps({
                "optimized_code": code,
                "optimizations_made": []
            })
            
        return "{}"
