import pytest
import sys
import os

# Adjust path to find backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layers.orchestration import Orchestrator

@pytest.mark.asyncio
async def test_end_to_end_mock_workflow():
    orchestrator = Orchestrator()
    
    # We use a simple input that matches our mock logic
    input_nl = "Se pulsante START premuto E sensore pressione > 5 bar, accendi pompa. Se pompa accesa > 10 sec, ferma pompa."
    
    result = await orchestrator.execute_workflow(
        input_nl=input_nl,
        plc_type="allen_bradley",
        safety_level="medium"
    )
    
    # Assertions
    assert result["success"] is True
    assert "pump_output" in result["ladder_code"] or "pompa" in result["ladder_code"]
    assert "<svg" in result["visualization"]
    assert result["metadata"]["total_rungs"] > 0
    assert len(result["warnings"]) > 0  # Should have safety warning in mock mode
    assert len(result["errors"]) == 0
