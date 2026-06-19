from typing import List, Dict

def generate_ladder_svg(rungs: List[Dict]) -> str:
    """
    Generates a premium, scalable SVG string representing the Ladder Logic diagram.
    Uses modern design aesthetics (sleek dark mode colors, glow effects, clean typography).
    """
    if not rungs:
        # Return empty placeholder
        return (
            '<svg viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg" style="background:#1e1e2e; border-radius:12px;">'
            '<text x="400" y="100" fill="#a6adc8" font-family="system-ui, sans-serif" font-size="16" text-anchor="middle">'
            'Nessuna logica da visualizzare. Inserisci una specifica.'
            '</text>'
            '</svg>'
        )

    # SVG geometry configurations
    width = 900
    rung_height = 140
    start_y = 60
    left_rail_x = 80
    right_rail_x = 820
    # Expand rungs with multiple actions into multiple visual rungs
    expanded_rungs = []
    for r in rungs:
        actions = r.get("actions", [])
        if not actions:
            expanded_rungs.append(r)
        else:
            for act in actions:
                new_r = r.copy()
                new_r["actions"] = [act]
                expanded_rungs.append(new_r)
    
    rungs = expanded_rungs

    total_height = start_y + (len(rungs) * rung_height) + 40
    
    # SVG Header
    svg = [
        f'<svg viewBox="0 0 {width} {total_height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background: #11111b; font-family: \'Outfit\', \'Inter\', sans-serif; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.4);">'
        '<defs>'
        '  <linearGradient id="railGrad" x1="0%" y1="0%" x2="0%" y2="100%">'
        '    <stop offset="0%" stop-color="#89b4fa"/>'
        '    <stop offset="100%" stop-color="#b4befe"/>'
        '  </linearGradient>'
        '  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">'
        '    <stop offset="0%" stop-color="#89b4fa"/>'
        '    <feGaussianBlur stdDeviation="3" result="blur"/>'
        '    <feComposite in="SourceGraphic" in2="blur" operator="over"/>'
        '  </filter>'
        '</defs>'
    ]
    
    # Draw Background Grid (Subtle lines)
    for x in range(0, width, 40):
        svg.append(f'  <line x1="{x}" y1="0" x2="{x}" y2="{total_height}" stroke="#181825" stroke-width="1"/>')
    for y in range(0, total_height, 40):
        svg.append(f'  <line x1="0" y1="{y}" x2="{width}" y2="{y}" stroke="#181825" stroke-width="1"/>')

    # Draw Power Rails (Left & Right vertical bars)
    svg.append(f'  <!-- Left Rail -->')
    svg.append(f'  <rect x="{left_rail_x - 4}" y="30" width="8" height="{total_height - 60}" rx="3" fill="url(#railGrad)"/>')
    svg.append(f'  <text x="{left_rail_x - 15}" y="25" fill="#89b4fa" font-size="12" font-weight="bold" text-anchor="end">24V DC</text>')
    
    svg.append(f'  <!-- Right Rail -->')
    svg.append(f'  <rect x="{right_rail_x - 4}" y="30" width="8" height="{total_height - 60}" rx="3" fill="url(#railGrad)"/>')
    svg.append(f'  <text x="{right_rail_x + 15}" y="25" fill="#f5e0dc" font-size="12" font-weight="bold" text-anchor="start">0V DC</text>')

    # Draw each Rung
    for rung_idx, rung in enumerate(rungs):
        curr_y = start_y + (rung_idx * rung_height)
        
        # Rung label/header
        actions = rung.get("actions", [])
        action_name = actions[0].get("target", "OUTPUT") if actions else "OUTPUT"
        svg.append(f'  <!-- Rung {rung_idx + 1} -->')
        svg.append(f'  <text x="{left_rail_x}" y="{curr_y - 30}" fill="#cdd6f4" font-size="14" font-weight="600">Rung {rung_idx + 1}: Controllo {action_name}</text>')
        
        # Conditions (Contacts in series)
        conditions = rung.get("conditions", [])
        num_conds = len(conditions)
        
        # We divide the path between left_rail and coil
        # Coil position:
        coil_x = right_rail_x - 100
        
        # Draw the main line of the rung
        svg.append(f'  <line x1="{left_rail_x}" y1="{curr_y}" x2="{right_rail_x}" y2="{curr_y}" stroke="#45475a" stroke-width="3"/>')
        
        # Space out contacts
        if num_conds > 0:
            section_width = (coil_x - left_rail_x) / (num_conds + 1)
            
            for i, cond in enumerate(conditions):
                contact_center_x = left_rail_x + (i + 1) * section_width
                c_name = cond.get("variable", f"IN_{i}")
                op = cond.get("operator", "TRUE")
                val = cond.get("value")
                
                # Check normal open / closed
                is_no = True
                if op == "FALSE":
                    is_no = False
                
                # Draw contact graphic (Clear background to mask the main line)
                svg.append(f'  <!-- Contact: {c_name} -->')
                svg.append(f'  <rect x="{contact_center_x - 18}" y="{curr_y - 20}" width="36" height="40" fill="#11111b"/>')
                
                # Contact vertical bars
                svg.append(f'  <line x1="{contact_center_x - 10}" y1="{curr_y - 15}" x2="{contact_center_x - 10}" y2="{curr_y + 15}" stroke="#89b4fa" stroke-width="4" stroke-linecap="round"/>')
                svg.append(f'  <line x1="{contact_center_x + 10}" y1="{curr_y - 15}" x2="{contact_center_x + 10}" y2="{curr_y + 15}" stroke="#89b4fa" stroke-width="4" stroke-linecap="round"/>')
                
                # Connect contact inside
                svg.append(f'  <line x1="{contact_center_x - 18}" y1="{curr_y}" x2="{contact_center_x - 10}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
                svg.append(f'  <line x1="{contact_center_x + 10}" y1="{curr_y}" x2="{contact_center_x + 18}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
                
                if not is_no:
                    # Normally closed: diagonal line
                    svg.append(f'  <line x1="{contact_center_x - 12}" y1="{curr_y + 12}" x2="{contact_center_x + 12}" y2="{curr_y - 12}" stroke="#f38ba8" stroke-width="3" stroke-linecap="round"/>')
                
                # Label text above contact
                svg.append(f'  <text x="{contact_center_x}" y="{curr_y - 22}" fill="#a6adc8" font-size="11" text-anchor="middle">{c_name}</text>')
                
                # Operator/value helper text below contact
                op_text = ""
                if op in ["GT", "LT", "GE", "LE", "EQ"]:
                    op_text = f"{op} {val}"
                elif not is_no:
                    op_text = "NC"
                else:
                    op_text = "NO"
                if op_text:
                    svg.append(f'  <text x="{contact_center_x}" y="{curr_y + 26}" fill="#585b70" font-size="10" text-anchor="middle">{op_text}</text>')
        else:
            # Direct connection to coil
            pass
            
        # Draw Output Coil / Functional Block at right end
        act = actions[0] if actions else {}
        act_type = act.get("type", "COIL")
        target_name = act.get("target", "OUTPUT")
        params = act.get("parameters", {})
        
        # Check if target is a timer block
        is_timer = act_type in ["TIMER_TON", "TIMER_TOF"]
        
        if is_timer:
            # Draw a box representing Timer block
            t_box_w = 120
            t_box_h = 60
            t_box_x = coil_x - 20
            t_box_y = curr_y - 30
            
            svg.append(f'  <!-- Timer Block: {target_name} -->')
            svg.append(f'  <rect x="{t_box_x}" y="{t_box_y}" width="{t_box_w}" height="{t_box_h}" rx="6" fill="#1e1e2e" stroke="#fab387" stroke-width="3" filter="url(#glow)"/>')
            svg.append(f'  <text x="{t_box_x + t_box_w/2}" y="{t_box_y + 20}" fill="#fab387" font-size="12" font-weight="bold" text-anchor="middle">{act_type.replace("TIMER_", "")} (Timer)</text>')
            svg.append(f'  <text x="{t_box_x + 10}" y="{t_box_y + 40}" fill="#a6adc8" font-size="10" text-anchor="start">IN: {conditions[0].get("variable") if conditions else "ON"}</text>')
            
            duration = params.get("PT_ms")
            dur_str = f"PT: {duration/1000}s" if duration else "PT: 10s"
            svg.append(f'  <text x="{t_box_x + t_box_w - 10}" y="{t_box_y + 40}" fill="#a6adc8" font-size="10" text-anchor="end">{dur_str}</text>')
            svg.append(f'  <text x="{t_box_x + t_box_w/2}" y="{t_box_y + 54}" fill="#fab387" font-size="9" font-weight="bold" text-anchor="middle">{target_name}</text>')
            
            # Connect box to left and right rails
            svg.append(f'  <line x1="{left_rail_x}" y1="{curr_y}" x2="{t_box_x}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
            svg.append(f'  <line x1="{t_box_x + t_box_w}" y1="{curr_y}" x2="{right_rail_x}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
        else:
            # Draw standard Coil (circle / curves)
            svg.append(f'  <!-- Coil: {target_name} -->')
            svg.append(f'  <rect x="{coil_x - 20}" y="{curr_y - 25}" width="40" height="50" fill="#11111b"/>')
            
            # Draw parenthesis curves: ( )
            svg.append(f'  <path d="M {coil_x - 12} {curr_y - 18} A 20 20 0 0 0 {coil_x - 12} {curr_y + 18}" fill="none" stroke="#a6e3a1" stroke-width="4" stroke-linecap="round"/>')
            svg.append(f'  <path d="M {coil_x + 12} {curr_y - 18} A 20 20 0 0 1 {coil_x + 12} {curr_y + 18}" fill="none" stroke="#a6e3a1" stroke-width="4" stroke-linecap="round"/>')
            
            # Connect coil internals
            svg.append(f'  <line x1="{coil_x - 20}" y1="{curr_y}" x2="{coil_x - 12}" y2="{curr_y}" stroke="#a6e3a1" stroke-width="3"/>')
            svg.append(f'  <line x1="{coil_x + 12}" y1="{curr_y}" x2="{coil_x + 20}" y2="{curr_y}" stroke="#a6e3a1" stroke-width="3"/>')
            
            # Set / Reset indicators inside the coil
            if act_type == "SET":
                svg.append(f'  <text x="{coil_x}" y="{curr_y + 5}" fill="#a6e3a1" font-size="12" font-weight="bold" text-anchor="middle">S</text>')
            elif act_type == "RESET":
                svg.append(f'  <text x="{coil_x}" y="{curr_y + 5}" fill="#f38ba8" font-size="12" font-weight="bold" text-anchor="middle">R</text>')
            
            # Coil label text above it
            svg.append(f'  <text x="{coil_x}" y="{curr_y - 22}" fill="#a6e3a1" font-size="11" text-anchor="middle" font-weight="bold">{target_name}</text>')
            
            # Connect last contact to coil, and coil to right rail
            last_contact_x = left_rail_x + num_conds * (section_width if num_conds > 0 else 0)
            if num_conds > 0:
                svg.append(f'  <line x1="{last_contact_x + 18}" y1="{curr_y}" x2="{coil_x - 20}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
            else:
                svg.append(f'  <line x1="{left_rail_x}" y1="{curr_y}" x2="{coil_x - 20}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')
                
            svg.append(f'  <line x1="{coil_x + 20}" y1="{curr_y}" x2="{right_rail_x}" y2="{curr_y}" stroke="#89b4fa" stroke-width="3"/>')

    svg.append('</svg>')
    return '\n'.join(svg)

