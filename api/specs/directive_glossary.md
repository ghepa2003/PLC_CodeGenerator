# DIRECTIVE: PLC Glossary & Domain Knowledge

## PLC Concepts
- **Rung**: Una singola riga o ramo di logica in un diagramma Ladder.
- **Contact**: Elemento di input (Normalmente Aperto [NO], Normalmente Chiuso [NC]).
- **Coil**: Elemento di output (bobina di attivazione, SET/latch, RESET/unlatch).
- **Timer**: Blocco funzionale per ritardi (TON - On Delay, TOF - Off Delay, TP - Pulse).
- **Counter**: Blocco funzionale per conteggi (CTU - Count Up, CTD - Count Down).

## IEC 61131-3 Standard
- Il Ladder Diagram (LD) è uno dei 5 linguaggi dello standard.
- L'esecuzione dei rung avviene in modo sequenziale (dall'alto verso il basso).
- Flusso di potenza virtuale da sinistra a destra.
- I contatti in serie rappresentano l'operatore logico AND.
- I contatti in parallelo rappresentano l'operatore logico OR.

## Common Patterns
- **Motor control**: Pulsante Start (NO) + Pulsante Stop (NC) + Contatto di autoritenuta + Protezione termica.
- **Pump control**: Pressostato + Flussostato + Feedback di stato + Timer di timeout marcia.
- **Safety interlock**: E-Stop (arresto d'emergenza) cablato in serie a tutti gli output critici.

## Terminology Mapping (Italian to PLC)
- "accendi", "attiva", "avvia" → SET coil / Coil attiva (Normally Open)
- "spegni", "disattiva", "ferma" → RESET coil / Coil disattiva (Normally Closed logic or explicit reset)
- "se", "quando" → Condizione di ingresso (Contact)
- "e", "inoltre", "congiuntamente" → Collegamento in serie (AND)
- "o", "oppure", "altrimenti" → Collegamento in parallelo (OR)
- "non", "in assenza di" → Contatto normalmente chiuso (NOT)
- "ritardo", "dopo" → Timer TON
- "per un tempo di" → Timer TP (Pulse) o TOF
