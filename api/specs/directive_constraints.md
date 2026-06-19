# DIRECTIVE: Technical Constraints & Preferences

## PLC Constraints
- Max contacts per rung: 7 (per favorire la leggibilità).
- Livello di nidificazione: massimo 3 livelli per rami paralleli.
- Convenzioni sui Nomi:
  - Input digitali: `I_` o `btn_`, `sensor_`
  - Output digitali: `Q_` o `actuator_`, `pump_`, `motor_`, `valve_`
  - Timer: `T_` o `timer_`
  - Counter: `C_` o `counter_`
  - Variabili interne / Memory: `M_` o `relay_`

## Code Generation Rules
- Ogni rung deve includere un commento descrittivo del suo funzionamento.
- Lo Structured Text generato deve essere conforme alla sintassi dello standard IEC 61131-3.
- Utilizzare una formattazione pulita, rientri consistenti e lettere maiuscole per le parole chiave booleane (`AND`, `OR`, `NOT`, `:=`).
- I blocchi di sicurezza (es. arresto d'emergenza o interblocchi hardware) devono avere la precedenza su qualsiasi logica di controllo.

## Validation Rules
- Nessuna bobina fluttuante (ogni output deve essere comandato da almeno una condizione logica).
- Nessun ramo isolato (dead code).
- I nomi dei timer e dei contatori devono essere univoci all'interno dell'intero blocco di programma.
- Rilevamento dei conflitti: non è consentito avere due rung che comandano la stessa bobina in modalità diretta (sovrascrittura dell'output nello stesso ciclo di scansione). Per attivazioni multiple della stessa bobina, usare logiche in parallelo (OR) o bobine di SET/RESET separate e mutualmente esclusive.
