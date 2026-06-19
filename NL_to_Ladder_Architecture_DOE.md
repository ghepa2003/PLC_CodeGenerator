# 🤖 NL → Ladder Logic PLC Generator
## Architettura Completa DOE (Directive-Orchestration-Executive)

**Progetto:** Conversione Natural Language → Codice Ladder IEC 61131-3  
**Stack:** OpenRouter (multi-model AI) + Python Backend + React Frontend (Vercel) + Antigravity (Development)  
**Pattern:** DOE 3-Layer Architecture  
**Data Provider:** OpenRouter API  
**Deployment:** Vercel (Frontend) + Python Server (Backend)  

---

## 📊 ARCHITETTURA GLOBALE

```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React/Vercel)                     │
│                  ↓ User Interface ↓ Natural Language Input        │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP REST API
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│              DIRECTIVE LAYER (Strategia & Governance)            │
│  - Requirements, Glossario PLC, Vincoli tecnici, Specs utente   │
│  Agenti: UX Designer, Product Manager                            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────────────────┐
│           ORCHESTRATION LAYER (Coordinamento & Routing)          │
│  - State Machine Workflow, Protocol comunicazione, Error handling│
│  Agente: Orchestrator (Direttore)                                │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────────────────────────┐
│              EXECUTIVE LAYER (Esecuzione Concreta)               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ NLP Processor: Parse NL → Structured Intent                │ │
│  │ Validator: Check consistency & ambiguity resolution         │ │
│  │ Code Generator: Intent → Ladder Logic                       │ │
│  │ Optimizer: Merge rungs, minimize complexity                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  Agenti: NLP Agent, Validator Agent, Code Generator Agent        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ↓ REST API
                 ┌────────────────────┐
                 │  RESPONSE: Ladder  │
                 │  + Metadata        │
                 │  + Visualization   │
                 └────────────────────┘
```

---

## 🔄 WORKFLOW COMPLETO (End-to-End)

### **Input → Processing → Output**

```
1. USER WRITES NATURAL LANGUAGE
   Example: "Se pulsante START premuto E sensore pressione > 5 bar, accendi pompa.
             Se pompa accesa > 10 sec, ferma pompa."

                            ↓

2. FRONTEND SENDS TO BACKEND (HTTP POST)
   POST /api/generate-ladder
   {
     "input_nl": "...",
     "plc_type": "allen_bradley",
     "safety_level": "medium",
     "user_preferences": { ... }
   }

                            ↓

3. DIRECTIVE LAYER LOADS CONTEXT
   [Carica specs, glossario PLC, vincoli)
   Output: Context Object con tutti i requirements

                            ↓

4. ORCHESTRATION LAYER ROUTES REQUEST
   [Determina workflow: Parse → Validate → Plan → Generate → Test]
   Output: Execution Plan

                            ↓

5. EXECUTIVE LAYER EXECUTES
   a) NLP AGENT: Estrae entità, intenzioni, logica booleana
      Output: Structured Intent Object
      
   b) VALIDATOR AGENT: Verifica coerenza, risolve ambiguità
      Output: Validated Intent + Warnings/Errors
      
   c) CODE GENERATOR AGENT: Converte in Ladder Logic
      Output: Ladder Rungs (IEC 61131-3)
      
   d) OPTIMIZER AGENT: Minimizza complessità
      Output: Optimized Ladder Code + Comments

                            ↓

6. BACKEND RETURNS RESPONSE
   {
     "success": true,
     "ladder_code": "...",
     "visualization": "<svg>...",
     "metadata": {
       "rungs_count": 5,
       "execution_time": 1.23,
       "warnings": []
     }
   }

                            ↓

7. FRONTEND DISPLAYS RESULT
   [Visualizzazione ladder, export options, edit UI]
```

---

## 📋 FILE MARKDOWN DA CREARE

Ogni file è una specifica che definirai una volta, e che gli agenti consulteranno.

### **LAYER 1: DIRECTIVE**

#### **1.1 `directive_requirements.md`**
```markdown
# DIRECTIVE: Requirements & Scope

## Functional Requirements
- Convertire free-text NL in Ladder Logic IEC 61131-3
- Supportare logica booleana (AND, OR, NOT, XOR)
- Gestire timer e counter
- Gestire sensori e attuatori con stati discreti/analogici
- Validare prima di generare codice

## Non-Functional Requirements
- Response time: < 5 secondi per input semplice
- Supportare PLC types: Allen Bradley, Siemens, Mitsubishi, Beckhoff
- Scalabilità: 100+ concurrent requests
- Tasso errore: < 2% per intenti semplici

## Success Metrics
- % di conversioni corrette (target: 95%)
- % di utenti che capiscono output
- Tempo medio generazione
- Engagement (save, export, share)
```

#### **1.2 `directive_glossary.md`**
```markdown
# DIRECTIVE: PLC Glossary & Domain Knowledge

## PLC Concepts
- **Rung**: Una riga di logica in ladder
- **Contact**: Elemento di input (Normally Open, Normally Closed)
- **Coil**: Elemento di output (elemento di set/reset)
- **Timer**: ON_DELAY, OFF_DELAY, PULSE_TIMER
- **Counter**: UP_COUNTER, DOWN_COUNTER, UP_DOWN_COUNTER

## IEC 61131-3 Standard
- Ladder Diagram (LD) is one of 5 languages
- Rungs execute sequentially
- Power rail on left and right
- Contacts can be in series (AND) or parallel (OR)

## Common Patterns
- Motor control: Start/Stop pushbuttons + timer + thermal protection
- Pump control: Flow sensor + pressure sensor + duty cycle
- Safety interlock: E-stop + two-hand control

## Terminology Mapping
- "accendi" → SET coil
- "spegni" → RESET coil / OFF coil
- "se" → IF logic (in series)
- "oppure" → OR logic (in parallel)
```

#### **1.3 `directive_constraints.md`**
```markdown
# DIRECTIVE: Technical Constraints & Preferences

## PLC Constraints
- Max contacts per rung: 7 (readability)
- Nesting depth: max 3 levels
- Scan cycle time: 50ms
- Memory: typical 2MB for ladder

## Code Generation Rules
- Always include comments
- Use standardized naming: btn_*, sensor_*, output_*, timer_*, counter_*
- Format: Rung number, description, then contacts
- Safety-critical logic MUST use double-check

## Validation Rules
- No floating coils (every output must have logic)
- No isolated branches (dead code detection)
- Timer/Counter names MUST be unique
- Sensori input MUST be debounced if freq < 1Hz
```

#### **1.4 `directive_ux_specs.md`**
```markdown
# DIRECTIVE: UX/Frontend Specifications

## User Input Interface
- Text area for free-form natural language
- PLC type selector dropdown
- Safety level selector (low/medium/high)
- Optional: Logic diagram preview while typing

## Output Display
- Left panel: Ladder logic visualization (SVG)
- Right panel: Code in text format (IEC 61131-3)
- Bottom: Execution metadata, warnings, errors

## Interaction Features
- Export to file (PDF, PNG, ST code)
- Edit mode: Modify ladder directly or regenerate
- History: Save previous generations
- Share: Generate shareable link
```

---

### **LAYER 2: ORCHESTRATION**

#### **2.1 `orchestration_workflow.md`**
```markdown
# ORCHESTRATION: Workflow State Machine

## Main States
1. **PARSE**: Ricevi input NL da utente
2. **VALIDATE_SYNTAX**: Controlla sintassi/ambiguità
3. **PLAN**: Determina struttura ladder (order delle rungs)
4. **GENERATE**: Scrivi rungs in IEC 61131-3
5. **OPTIMIZE**: Merge rungs, riduci complessità
6. **TEST**: Valida logica finale
7. **RETURN**: Invia a frontend

## State Transitions
- PARSE → VALIDATE_SYNTAX (sempre)
- VALIDATE_SYNTAX → [ERROR] oppure PLAN
- PLAN → GENERATE (sempre)
- GENERATE → OPTIMIZE (se complexity > threshold)
- OPTIMIZE → TEST (sempre)
- TEST → [WARNING/ERROR] oppure RETURN

## Error Handling
- Se VALIDATE fallisce: ritorna lista di clarifying questions
- Se GENERATE fallisce: riprova con simplified structure
- Se TEST fallisce: log error + fallback to manual review mode
```

#### **2.2 `orchestration_protocol.md`**
```markdown
# ORCHESTRATION: Inter-Agent Communication Protocol

## Agent Communication Format
All messages are JSON objects with:
- `agent_id`: chi ha mandato il messaggio
- `timestamp`: when
- `state`: current state
- `payload`: actual data
- `version`: schema version

## Message Flow Example
```
orchestrator → nlp_agent:
{
  "agent_id": "orchestrator",
  "state": "PARSE",
  "payload": { "input_nl": "...", "plc_type": "allen_bradley" }
}

nlp_agent → orchestrator:
{
  "agent_id": "nlp_agent",
  "state": "PARSE_COMPLETE",
  "payload": { 
    "intent_objects": [...],
    "confidence": 0.92,
    "ambiguities": []
  }
}
```

## Timeout & Retry
- Timeout per agent: 30 seconds
- Retry logic: max 2 retries con backoff exponential
- If all retries fail: escalate to error handler
```

#### **2.3 `orchestration_error_handling.md`**
```markdown
# ORCHESTRATION: Error Handling Strategy

## Error Categories
1. **INPUT_AMBIGUOUS**: Clarify with user
   - Ask multiple choice questions
   - Request more details about specific components

2. **UNSUPPORTED_LOGIC**: Cannot convert to ladder
   - Example: Fuzzy logic, ML inference
   - Fallback: Suggest alternative approach

3. **COMPLEXITY_EXCEEDED**: Ladder logic too complex
   - Break into multiple sub-problems
   - Suggest subroutine architecture

4. **API_FAILURE**: OpenRouter API down
   - Cache previous responses
   - Use local fallback model (lightweight)

## Escalation
- Level 1: Retry with different model
- Level 2: Ask user for clarification
- Level 3: Manual review queue (for later)
```

---

### **LAYER 3: EXECUTIVE**

#### **3.1 `executive_nlp_processor.md`**
```markdown
# EXECUTIVE: NLP Processor Specifications

## Input
- Natural language text (Italian, English)
- Context from directive layer

## Processing Steps

### Step 1: Tokenization & Entity Extraction
Extract:
- **SENSORS**: button, sensor, input device
  - Pattern: "pulsante", "sensore", "bottone", "contatto", "switch"
  - Attributes: name, type (digital/analog), normally_open/closed
  
- **ACTUATORS**: pump, motor, light, solenoid
  - Pattern: "pompa", "motore", "luce", "solenoide"
  - Attributes: name, type, power_on/off behavior
  
- **TIMERS**: delay, duration, timeout
  - Pattern: "dopo", "entro", "durante", "per X secondi/minuti"
  - Attributes: name, duration, type (on_delay/off_delay)
  
- **COUNTERS**: count, cycle, occurrence
  - Pattern: "ogni N volte", "conta", "occorrenza"
  - Attributes: name, count_value, action_on_reach

### Step 2: Relationship Extraction
Identify logical relationships:
- AND: "e", "inoltre", ",", "anche"
- OR: "oppure", "o", "altrimenti"
- NOT: "non", "tranne", "eccetto"
- IF-THEN: "se...allora", "quando...poi"
- SEQUENCE: "prima", "poi", "successivamente"

### Step 3: Build Intent Tree
Structure:
```
IntentObject {
  id: "intent_001",
  type: "conditional_activation",
  conditions: [
    { entity: "btn_start", operator: "PRESSED" },
    { entity: "sensor_pressure", operator: "GT", value: 5 }
  ],
  logic_gate: "AND",
  action: {
    type: "SET",
    target: "pump_output",
    duration: null
  }
}
```

## Output
- List of IntentObjects (structured)
- Confidence scores
- Ambiguities flagged for validation
```

#### **3.2 `executive_validator_agent.md`**
```markdown
# EXECUTIVE: Validator Agent Specifications

## Input
- IntentObjects from NLP processor
- Domain glossary & constraints

## Validation Checks

### Check 1: Entity Consistency
- All entities exist in glossary
- No conflicting definitions
- Naming follows standards

### Check 2: Logic Consistency
- No contradictions (e.g., "turn ON if input OFF and input ON")
- No deadlocks (logic that can never be satisfied)
- No floating outputs (every output has trigger logic)

### Check 3: Ambiguity Resolution
Ask clarifying questions for:
- Ambiguous entity names
  Example: "Pompa" (è pompa1 o pompa2?)
  
- Ambiguous operators
  Example: "dopo 10 secondi" (on_delay o off_delay?)
  
- Ambiguous scope
  Example: "quando il sensore è attivo" (continuously? triggered once?)

### Check 4: Safety Check
- Critical operations flagged for double-check
- E-stop logic validated
- Interlocks present where needed

## Output
- Validated IntentObjects
- List of warnings
- List of resolved ambiguities
- Questions for user (if needed)
```

#### **3.3 `executive_code_generator.md`**
```markdown
# EXECUTIVE: Code Generator Agent Specifications

## Input
- Validated IntentObjects
- Ladder generation rules from directive

## Generation Algorithm

### Phase 1: Rung Planning
Create execution order:
1. Identify independent logic branches
2. Order by dependency (no forward references)
3. Insert timers/counters before their use
4. Group related rungs

### Phase 2: Rung Generation
For each IntentObject, generate ladder rung(s):

**Example: Simple condition**
```
IntentObject: {
  conditions: [{ entity: "btn_start", operator: "PRESSED" }],
  action: { type: "SET", target: "pump" }
}

Ladder Output:
  Rung 001: Start button pressed → Set pump ON
  ├─ [ btn_start ] ────( pump )─┤
```

**Example: Complex logic**
```
IntentObject: {
  conditions: [
    { entity: "btn_start", operator: "PRESSED" },
    { entity: "sensor_pressure", operator: "GT", value: 5 },
    { entity: "sensor_flow", operator: "GT", value: 10 }
  ],
  logic_gate: "AND",
  action: { type: "SET", target: "pump_output" }
}

Ladder Output:
  Rung 001: Start pump if conditions met
  ├─ [ btn_start ]──[ sensor_pressure > 5 ]──[ sensor_flow > 10 ]────( pump_output )─┤
```

**Example: Timer logic**
```
Rung 002: Timer - pump running
├─ [ pump_output ]────[ TON: timer_pump_running, 10s ]────( timer_pump_running.Q )─┤

Rung 003: Stop pump after 10 seconds
├─ [ timer_pump_running.Q ]────( pump_stop )─┤
```

### Phase 3: Code Formatting
Output in IEC 61131-3 ST (Structured Text):
```
(* Rung 001: Start pump if conditions met *)
pump_output := btn_start AND (sensor_pressure > 5) AND (sensor_flow > 10);

(* Rung 002: Pump running timer *)
TON_pump(IN := pump_output, PT := T#10s);

(* Rung 003: Stop pump after 10 seconds *)
pump_stop := TON_pump.Q;
```

### Phase 4: Add Comments & Metadata
- Each rung: description, author, timestamp
- Variable declarations (type, initial value)
- Function block declarations

## Output
- Ladder code in IEC 61131-3 format
- SVG visualization (rungs diagram)
- Metadata: rung count, complexity score
```

#### **3.4 `executive_optimizer.md`**
```markdown
# EXECUTIVE: Optimizer Agent Specifications

## Input
- Generated Ladder Code
- Optimization threshold

## Optimization Rules

### Rule 1: Merge Similar Rungs
If two rungs have same logic branch, merge:
```
Before:
├─ [ A ]────( X )─┤
├─ [ A ]────( Y )─┤

After:
├─ [ A ]────( X )─┤
       ├─( Y )─┤
```

### Rule 2: Eliminate Redundant Contacts
If condition appears twice, use internal relay:
```
Before:
├─ [ A ]──[ B ]──[ C ]────( X )─┤
├─ [ A ]──[ B ]──[ C ]────( Y )─┤

After:
├─ [ A ]──[ B ]──[ C ]────( internal_relay )─┤
├─ [ internal_relay ]────( X )─┤
├─ [ internal_relay ]────( Y )─┤
```

### Rule 3: Parallel to Series Optimization
Minimize nesting if complexity is high:
```
Before: (A OR B) AND (C OR D)  → 4 contacts + nested logic

After: Create intermediate coils
```

### Rule 4: Timer/Counter Optimization
Combine related timers, reuse reset logic

## Output
- Optimized ladder code
- Optimization report (changes made)
- Complexity metrics (before/after)
```

---

## 🏗️ ARCHITETTURA BACKEND (Python)

### **Directory Structure**
```
backend/
├── main.py                          # FastAPI entry point
├── requirements.txt                 # pip dependencies
├── config.py                        # Configuration (OpenRouter API key, etc)
├── 
├── layers/
│   ├── directive.py                # Loads & manages directive specs
│   ├── orchestration.py             # State machine, routing logic
│   └── executive.py                 # Executor for all agent calls
│
├── agents/
│   ├── base_agent.py               # Base agent class (OpenRouter caller)
│   ├── nlp_processor.py             # NLP Agent implementation
│   ├── validator.py                 # Validator Agent
│   ├── code_generator.py            # Code Generator Agent
│   └── optimizer.py                 # Optimizer Agent
│
├── models/
│   ├── intent_model.py              # Pydantic models for IntentObject
│   ├── ladder_model.py              # Pydantic models for Ladder output
│   └── schemas.py                   # JSON schemas
│
├── utils/
│   ├── openrouter_client.py         # OpenRouter API wrapper
│   ├── ladder_formatter.py          # Ladder code formatting
│   ├── svg_generator.py             # SVG visualization generator
│   └── error_handler.py             # Error handling utilities
│
├── specs/
│   ├── directive_requirements.md
│   ├── directive_glossary.md
│   ├── directive_constraints.md
│   ├── directive_ux_specs.md
│   ├── orchestration_workflow.md
│   ├── orchestration_protocol.md
│   ├── orchestration_error_handling.md
│   ├── executive_nlp_processor.md
│   ├── executive_validator_agent.md
│   ├── executive_code_generator.md
│   └── executive_optimizer.md
│
└── tests/
    ├── test_agents.py
    ├── test_workflow.py
    └── test_ladder_output.py
```

### **Key Backend Components**

#### **main.py (FastAPI)**
```python
from fastapi import FastAPI
from fastapi.cors import CORSMiddleware
from layers import directive, orchestration, executive

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/generate-ladder")
async def generate_ladder(request: GenerateLadderRequest):
    """
    Main endpoint: NL → Ladder
    """
    # Load directive context
    ctx = directive.load_context(request.plc_type)
    
    # Execute orchestration
    result = await orchestration.execute_workflow(
        input_nl=request.input_nl,
        context=ctx
    )
    
    return result

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

#### **orchestration.py (State Machine)**
```python
from enum import Enum
from agents import nlp_processor, validator, code_generator, optimizer

class WorkflowState(Enum):
    PARSE = "parse"
    VALIDATE = "validate"
    PLAN = "plan"
    GENERATE = "generate"
    OPTIMIZE = "optimize"
    TEST = "test"
    RETURN = "return"

async def execute_workflow(input_nl, context):
    state = WorkflowState.PARSE
    
    while state != WorkflowState.RETURN:
        if state == WorkflowState.PARSE:
            intent_objects = await nlp_processor.process(input_nl, context)
            state = WorkflowState.VALIDATE
            
        elif state == WorkflowState.VALIDATE:
            validated = await validator.validate(intent_objects, context)
            if validated.errors:
                return {"error": validated.errors}
            state = WorkflowState.PLAN
            
        elif state == WorkflowState.GENERATE:
            ladder_code = await code_generator.generate(validated, context)
            state = WorkflowState.OPTIMIZE
            
        elif state == WorkflowState.OPTIMIZE:
            optimized = await optimizer.optimize(ladder_code, context)
            state = WorkflowState.TEST
            
        # ... other states
    
    return build_response(optimized, context)
```

#### **agents/base_agent.py**
```python
import openai
from config import OPENROUTER_API_KEY

class BaseAgent:
    def __init__(self, agent_id: str, model: str):
        self.agent_id = agent_id
        self.model = model
        self.client = openai.AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.io/api/v1"
        )
    
    async def call_model(self, system_prompt: str, user_prompt: str):
        """Call OpenRouter with specified model"""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Low temp for deterministic output
            top_p=0.9
        )
        return response.choices[0].message.content

class NLPAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="nlp_processor",
            model="anthropic/claude-3-5-sonnet"  # or your choice from OpenRouter
        )
    
    async def process(self, input_nl: str, context: dict):
        system_prompt = open("specs/executive_nlp_processor.md").read()
        user_prompt = f"""
        Process this natural language input:
        {input_nl}
        
        Using domain glossary:
        {context['glossary']}
        
        Return structured JSON with IntentObjects.
        """
        response = await self.call_model(system_prompt, user_prompt)
        return parse_intent_objects(response)
```

---

## 🎨 ARCHITETTURA FRONTEND (React/Vercel)

### **Directory Structure**
```
frontend/
├── pages/
│   ├── index.tsx                    # Main app
│   ├── api/
│   │   └── generate.ts              # Proxy to backend
│   └── _app.tsx                     # App wrapper
│
├── components/
│   ├── InputPanel.tsx               # NL text input
│   ├── LadderVisualization.tsx       # SVG ladder display
│   ├── CodePanel.tsx                # Code output
│   ├── MetadataPanel.tsx            # Execution stats
│   └── ExportModal.tsx              # Download options
│
├── hooks/
│   └── useGenerateLadder.ts         # API call hook
│
├── utils/
│   ├── api.ts                       # Backend API client
│   └── validators.ts                # Input validation
│
├── styles/
│   └── globals.css                  # Tailwind/CSS
│
├── public/
│   └── logo.svg
│
├── package.json
├── tsconfig.json
└── vercel.json                      # Vercel config
```

### **Key Frontend Components**

#### **pages/index.tsx**
```typescript
import React, { useState } from 'react';
import InputPanel from '@/components/InputPanel';
import LadderVisualization from '@/components/LadderVisualization';
import CodePanel from '@/components/CodePanel';
import MetadataPanel from '@/components/MetadataPanel';
import { useGenerateLadder } from '@/hooks/useGenerateLadder';

export default function Home() {
  const [inputNL, setInputNL] = useState('');
  const [plcType, setPlcType] = useState('allen_bradley');
  const { result, loading, error, generate } = useGenerateLadder();

  const handleGenerate = async () => {
    await generate(inputNL, plcType);
  };

  return (
    <div className="flex h-screen">
      {/* Left: Input */}
      <div className="w-1/3 p-4 border-r">
        <InputPanel
          value={inputNL}
          onChange={setInputNL}
          plcType={plcType}
          onPlcTypeChange={setPlcType}
          onGenerate={handleGenerate}
          loading={loading}
        />
      </div>

      {/* Right: Output */}
      <div className="w-2/3 p-4 flex flex-col">
        {error && <div className="text-red-500 mb-4">{error}</div>}
        {result && (
          <>
            <LadderVisualization svg={result.visualization} />
            <CodePanel code={result.ladder_code} />
            <MetadataPanel metadata={result.metadata} />
          </>
        )}
      </div>
    </div>
  );
}
```

#### **hooks/useGenerateLadder.ts**
```typescript
import { useState } from 'react';
import api from '@/utils/api';

export function useGenerateLadder() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generate = async (inputNL: string, plcType: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.generateLadder({
        input_nl: inputNL,
        plc_type: plcType,
      });
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { result, loading, error, generate };
}
```

---

## 📊 DATA SCHEMAS

### **Intent Object Schema (JSON)**
```json
{
  "intent_id": "intent_001",
  "intent_type": "conditional_activation",
  "conditions": [
    {
      "entity_id": "btn_start",
      "entity_name": "Start Button",
      "entity_type": "input_digital",
      "operator": "PRESSED",
      "value": null,
      "normally_open": true
    },
    {
      "entity_id": "sensor_pressure",
      "entity_name": "Pressure Sensor",
      "entity_type": "input_analog",
      "operator": "GT",
      "value": 5,
      "unit": "bar"
    }
  ],
  "logic_gate": "AND",
  "negations": [],
  "action": {
    "action_type": "SET",
    "target_id": "pump_output",
    "target_name": "Pump Motor",
    "target_type": "output_digital",
    "duration_ms": null,
    "priority": "normal"
  },
  "confidence_score": 0.95,
  "ambiguities": []
}
```

### **Ladder Output Schema (JSON)**
```json
{
  "success": true,
  "ladder_code": "...",
  "ladder_format": "iec_61131_3_st",
  "visualization": "<svg>...</svg>",
  "metadata": {
    "total_rungs": 5,
    "total_contacts": 12,
    "total_coils": 4,
    "complexity_score": 0.62,
    "execution_time_ms": 1234,
    "model_used": "anthropic/claude-3-5-sonnet",
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "warnings": [
    {
      "level": "WARNING",
      "code": "AMBIGUOUS_TIMER",
      "message": "Timer duration assumed 10 seconds, confirm if correct"
    }
  ],
  "errors": [],
  "export_formats": {
    "pdf_url": "...",
    "png_url": "...",
    "st_download_url": "..."
  }
}
```

---

## 🚀 CHECKLIST DI IMPLEMENTAZIONE (In Ordine)

### **FASE 1: Setup Iniziale**
- [ ] Creare repo backend (Python + FastAPI)
- [ ] Creare repo frontend (React + Next.js)
- [ ] Setup OpenRouter account e ottenere API key
- [ ] Configurare environment variables (.env)
- [ ] Setup Vercel project per frontend

### **FASE 2: Directive Layer**
- [ ] Scrivi `directive_requirements.md` con requirements specifici
- [ ] Scrivi `directive_glossary.md` con terminology PLC
- [ ] Scrivi `directive_constraints.md` con vincoli tecnici
- [ ] Scrivi `directive_ux_specs.md` con UI mockups
- [ ] Backend: implementa loader per directive specs

### **FASE 3: Orchestration Layer**
- [ ] Scrivi `orchestration_workflow.md` con state machine
- [ ] Scrivi `orchestration_protocol.md` con formato messaggi
- [ ] Scrivi `orchestration_error_handling.md`
- [ ] Backend: implementa orchestration.py con state machine
- [ ] Backend: test workflow transitions

### **FASE 4: Executive Layer - NLP Agent**
- [ ] Scrivi `executive_nlp_processor.md` completo
- [ ] Backend: implementa `agents/nlp_processor.py`
- [ ] Test: mandale examples dal glossario, verifica IntentObjects
- [ ] Ottimizza prompt per accuracy

### **FASE 5: Executive Layer - Validator Agent**
- [ ] Scrivi `executive_validator_agent.md` completo
- [ ] Backend: implementa `agents/validator.py`
- [ ] Test: verifica risoluzione ambiguità
- [ ] Test: safety checks funzionano

### **FASE 6: Executive Layer - Code Generator Agent**
- [ ] Scrivi `executive_code_generator.md` con examples
- [ ] Backend: implementa `agents/code_generator.py`
- [ ] Backend: implementa `utils/ladder_formatter.py` (IEC 61131-3)
- [ ] Test: simple ladder generation (1 rung)
- [ ] Test: complex ladder (5+ rungs with timers)

### **FASE 7: Executive Layer - Optimizer Agent**
- [ ] Scrivi `executive_optimizer.md` con regole
- [ ] Backend: implementa `agents/optimizer.py`
- [ ] Test: merge similar rungs works
- [ ] Test: complexity reduction measured

### **FASE 8: Visualization & Export**
- [ ] Backend: implementa `utils/svg_generator.py` (ladder to SVG)
- [ ] Backend: setup PDF/PNG export (use reportlab or similar)
- [ ] Frontend: LadderVisualization component
- [ ] Frontend: ExportModal component

### **FASE 9: Frontend Integration**
- [ ] Frontend: InputPanel component
- [ ] Frontend: CodePanel component
- [ ] Frontend: MetadataPanel component
- [ ] Frontend: Connect useGenerateLadder hook
- [ ] Frontend: Error handling UI

### **FASE 10: Testing & Optimization**
- [ ] Backend: test suite (pytest)
- [ ] Frontend: test suite (jest + react-testing-library)
- [ ] End-to-end test: NL input → Ladder output
- [ ] Performance: measure response times
- [ ] Load test: concurrent requests

### **FASE 11: Deployment**
- [ ] Backend: containerize (Docker) + deploy to cloud (Heroku, Railway, or cloud provider)
- [ ] Frontend: deploy to Vercel (git push trigger)
- [ ] Setup monitoring & logging
- [ ] Configure CORS, rate limits, API keys

### **FASE 12: Post-Launch**
- [ ] Collect user feedback
- [ ] Monitor error rates
- [ ] Iterate on agent prompts
- [ ] Expand PLC type support
- [ ] Add more examples to glossary

---

## 🔧 AGENT SELECTION DA OPENROUTER

**Consigliati per questo task:**

| Agent Purpose | OpenRouter Model | Cost | Speed | Quality |
|---|---|---|---|---|
| **NLP Processing** | `anthropic/claude-3-5-sonnet` | $$ | Fast | Excellent |
| **Validation** | `deepseek/deepseek-chat` | $ | Fast | Good |
| **Code Generator** | `openai/gpt-4o` | $$$$ | Medium | Best |
| **Optimizer** | `anthropic/claude-3-haiku` | $ | Very Fast | Good |
| **Fallback** | `meta-llama/llama-2-70b` | $ | Medium | Good |

**Strategia di selezione:**
- NLP: use Claude Sonnet (buon trade-off)
- Code Gen: use GPT-4o if budget allows (best for precise code)
- Validator: use DeepSeek o Llama (cost-effective)
- Optimizer: use Haiku (fast, sufficient)

---

## 📝 NEXT STEPS IN ANTIGRAVITY

1. **Importa questo file** come master spec
2. **Per ogni sezione**, crea un agent in Antigravity:
   - Agent 1: NLP Processor (incaricato: Claude Sonnet)
   - Agent 2: Validator (incaricato: DeepSeek)
   - Agent 3: Code Generator (incaricato: GPT-4o)
   - Agent 4: Optimizer (incaricato: Haiku)
   - Agent 5: Orchestrator (incaricato: Claude Sonnet)

3. **Scrivi le spec markdown** seguendo template qui sopra

4. **Test workflow** con simple example end-to-end

5. **Itera e ottimizza** based on results

---

## 🎯 SUCCESS CRITERIA

✅ **Fase finale:**
- Input: *"Se pulsante acceso e pressione > 5 bar, accendi pompa. Se pompa accesa > 10 sec, spegni."*
- Output: Ladder IEC 61131-3 corretto, visualizzazione SVG, export PDF

- Response time: < 3 secondi
- Accuracy: 90%+ su semplici intenti
- User can edit & regenerate

---

## 📚 RESOURCES

- [IEC 61131-3 Standard](https://en.wikipedia.org/wiki/IEC_61131-3)
- [Ladder Logic Tutorial](https://www.tutorialspoint.com/plc_scada/plc_ladder_logic.htm)
- [OpenRouter Documentation](https://openrouter.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-15  
**Author:** Lorenzo (in collaboration with Claude)  
**Status:** Ready for Antigravity Implementation

