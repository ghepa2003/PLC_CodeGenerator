from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    total_rungs: int = 0
    total_contacts: int = 0
    total_coils: int = 0
    complexity_score: float = 0.0
    execution_time_ms: int = 0
    model_used: str = ""
    timestamp: str = ""

class LogMessage(BaseModel):
    level: str = "WARNING"  # INFO, WARNING, ERROR
    code: str
    message: str
    suggestions: List[str] = Field(default_factory=list)

class IRVariable(BaseModel):
    name: str
    data_type: str = Field(description="BOOL, INT, REAL, TIME")
    description: Optional[str] = ""

class IRCondition(BaseModel):
    variable: str
    operator: str = Field(description="TRUE, FALSE, GT, LT, EQ, GE, LE")
    value: Optional[Any] = None

class IRAction(BaseModel):
    type: str = Field(description="COIL, SET, RESET, TIMER_TON, TIMER_TOF, COUNTER_CTU")
    target: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class IRRung(BaseModel):
    comment: str
    conditions: List[IRCondition]
    logic_gate: str = Field(default="AND", description="AND or OR for combining conditions")
    actions: List[IRAction]

class IntermediateRepresentation(BaseModel):
    variables: List[IRVariable]
    rungs: List[IRRung]
    clarifying_questions: List[str] = Field(default_factory=list)


class LadderOutputSchema(BaseModel):
    success: bool
    ladder_code: str
    ladder_format: str = "iec_61131_3_st"
    visualization: str = ""  # SVG string
    metadata: Metadata = Field(default_factory=Metadata)
    warnings: List[LogMessage] = Field(default_factory=list)
    errors: List[LogMessage] = Field(default_factory=list)
    clarifying_questions: List[str] = Field(default_factory=list)
    xml_codesys: Optional[str] = ""
