import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.xml_generator import generate_plcopen_xml

def test_xml_generation():
    var_decls = """VAR
    btn_start : BOOL; (* Pulsante di start *)
    sensor_pressure : REAL; (* Pressione in bar *)
    TON_pump : TON;
END_VAR"""
    
    st_code = """IF btn_start THEN
    TON_pump(IN := TRUE, PT := T#5s);
END_IF;"""

    xml = generate_plcopen_xml(st_code, var_decls)
    
    # Assertions
    assert '<?xml version="1.0" encoding="utf-8"?>' in xml
    assert '<variable name="btn_start">' in xml
    assert '<BOOL/>' in xml
    assert '<derived name="TON"/>' in xml
    assert 'Pulsante di start' in xml
    assert 'TON_pump' in xml
    assert 'CDATA[' in xml
    assert 'TON_pump(IN := TRUE, PT := T#5s);' in xml
