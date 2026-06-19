import re
import datetime
from xml.sax.saxutils import escape

def generate_plcopen_xml(st_code: str, var_declarations: str) -> str:
    """
    Generates a standard PLCopen XML schema containing variables and Structured Text logic
    suitable for importing into CODESYS and other IEC 61131-3 compatible editors.
    """
    # Parse variables from declarations
    variables_xml = []
    
    # Simple regex parsing for variables: "name : TYPE; (* comment *)"
    # Find lines inside VAR ... END_VAR
    var_lines = []
    in_var_block = False
    
    for line in var_declarations.splitlines():
        line_strip = line.strip()
        if not line_strip:
            continue
        if line_strip.upper().startswith("VAR"):
            in_var_block = True
            continue
        if line_strip.upper().startswith("END_VAR"):
            in_var_block = False
            continue
        if in_var_block:
            var_lines.append(line_strip)
            
    for line in var_lines:
        # Match "var_name : var_type; (* comment *)"
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:;\s*(?:\(\*(.*?)\*\))?)?", line)
        if match:
            v_name = match.group(1)
            v_type = match.group(2).upper()
            v_comment = match.group(3).strip() if match.group(3) else ""
            
            # Map standard types or functional blocks
            type_element = f"<{v_type}/>"
            if v_type not in ["BOOL", "INT", "REAL", "DINT", "LREAL", "TIME", "STRING", "WORD", "DWORD"]:
                # Functional blocks (like TON, TOF) require derived types
                type_element = f"<derived name=\"{v_type}\"/>"
                
            comment_xml = ""
            if v_comment:
                comment_xml = f"\n            <documentation>\n              <xhtml xmlns=\"http://www.w3.org/1999/xhtml\"><![CDATA[{escape(v_comment)}]]></xhtml>\n            </documentation>"
                
            variables_xml.append(
                f'          <variable name="{v_name}">\n'
                f'            <type>\n'
                f'              {type_element}\n'
                f'            </type>{comment_xml}\n'
                f'          </variable>'
            )
            
    variables_block = "\n".join(variables_xml)
    current_time = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Escape special characters from the main ST code
    escaped_st_code = st_code
    
    xml_str = f"""<?xml version="1.0" encoding="utf-8"?>
<project xmlns="http://www.plcopen.org/xml/tc6_0201">
  <fileHeader companyName="PLC Code Generator" productName="NL to Ladder" productVersion="1.0" creationDateTime="{current_time}"/>
  <contentHeader name="PLC_Code_Generator" version="1.0">
    <coordinateInfo>
      <fbd><size x="0" y="0"/></fbd>
      <ld><size x="0" y="0"/></ld>
      <sfc><size x="0" y="0"/></sfc>
    </coordinateInfo>
  </contentHeader>
  <types>
    <dataTypes/>
    <pous>
      <pou name="PLC_PRG" pouType="program">
        <interface>
          <localVars>
{variables_block}
          </localVars>
        </interface>
        <body>
          <ST>
            <xhtml xmlns="http://www.w3.org/1999/xhtml">
              <![CDATA[
{escaped_st_code}
              ]]>
            </xhtml>
          </ST>
        </body>
      </pou>
    </pous>
  </types>
  <instances>
    <configurations>
      <configuration name="Config">
        <resource name="Resource">
          <task name="Task" interval="T#50ms" priority="1">
            <pouInstance name="PRG_Instance" typeName="PLC_PRG"/>
          </task>
        </resource>
      </configuration>
    </configurations>
  </instances>
</project>
"""
    return xml_str
