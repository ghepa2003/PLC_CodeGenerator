import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.svg_generator import generate_ladder_svg

def test_empty_svg_generation():
    svg = generate_ladder_svg([])
    assert "<svg" in svg
    assert "Nessuna logica" in svg

def test_single_rung_svg_generation():
    # Mock intent objects
    intents = [
        {
            "intent_id": "intent_001",
            "conditions": [
                {
                    "entity_id": "btn_start",
                    "operator": "PRESSED",
                    "normally_open": True
                }
            ],
            "action": {
                "action_type": "SET",
                "target_id": "pump_output"
            }
        }
    ]
    svg = generate_ladder_svg(intents)
    assert "<svg" in svg
    assert "btn_start" in svg
    assert "pump_output" in svg
    assert "Rung 1:" in svg
