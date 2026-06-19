from typing import List, Optional, Any
from pydantic import BaseModel, Field

class Entity(BaseModel):
    entity_id: str
    entity_name: str
    entity_type: str  # input_digital, input_analog, output_digital, output_analog, timer, counter, internal_relay
    normally_open: Optional[bool] = True

class Condition(BaseModel):
    entity_id: str
    operator: str  # PRESSED, RELEASED, TRUE, FALSE, GT, LT, EQ, GE, LE
    value: Optional[Any] = None
    normally_open: Optional[bool] = True

class Action(BaseModel):
    action_type: str  # SET, RESET, OUT
    target_id: str
    target_name: Optional[str] = None
    target_type: Optional[str] = None
    duration_ms: Optional[int] = None
    priority: Optional[str] = "normal"

class IntentObject(BaseModel):
    intent_id: str
    intent_type: str  # conditional_activation, logic_gate, timer_trigger, etc.
    conditions: List[Condition]
    logic_gate: str = "AND"  # AND, OR, XOR
    negations: List[str] = Field(default_factory=list)  # list of entity_ids negated
    action: Action
    confidence_score: float = 1.0
    ambiguities: List[str] = Field(default_factory=list)
