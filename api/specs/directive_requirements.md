# DIRECTIVE: Requirements & Scope

## Functional Requirements
- Convertire free-text NL (Natural Language) in Ladder Logic IEC 61131-3 (Structured Text representation and SVG).
- Supportare logica booleana (AND, OR, NOT, XOR).
- Gestire timer (TON, TOF, TP) e counter (CTU, CTD).
- Gestire sensori e attuatori con stati discreti/analogici.
- Validare l'input prima di generare il codice per evitare incongruenze e situazioni di pericolo.

## Non-Functional Requirements
- Response time: < 5 secondi per input semplice.
- Supportare PLC types: Allen Bradley, Siemens, Mitsubishi, Beckhoff.
- Tasso errore: < 2% per intenti semplici.
- Robustezza: Gestione accurata delle eccezioni e dei messaggi di errore restituiti all'utente.

## Success Metrics
- Percentuale di conversioni sintatticamente corrette (target: 95%).
- Comprensione immediata dell'output grafico da parte dell'utente.
