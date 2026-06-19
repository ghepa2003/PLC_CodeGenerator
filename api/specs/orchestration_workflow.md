# ORCHESTRATION: Workflow State Machine

## Main States
1. **PARSE**: Ricezione dell'input in linguaggio naturale dall'utente ed estrazione strutturata delle entità e degli intenti logici.
2. **VALIDATE**: Controllo della coerenza logica, verifica dei vincoli tecnici e di sicurezza, rilevamento di ambiguità o conflitti.
3. **PLAN**: Ordinamento logico dei rung e dei blocchi funzionali (ad esempio, posizionamento dei timer prima dei relativi contatti).
4. **GENERATE**: Traduzione del piano in codice Structured Text (ST) IEC 61131-3 ed elementi grafici Ladder.
5. **OPTIMIZE**: Applicazione di regole di ottimizzazione booleana per semplificare i rami e ridurre il numero di contatti/bobine ridondanti.
6. **TEST**: Verifica finale del codice generato rispetto ai requisiti originali.
7. **RETURN**: Formattazione della risposta JSON contenente codice, diagramma SVG, metadati ed eventuali warning.

## State Transitions
- `START` → `PARSE`
- `PARSE` → `VALIDATE`
- `VALIDATE` → `PLAN` (se valido)
- `VALIDATE` → `RETURN` (se vengono rilevati errori critici o ambiguità irrisolte da chiarire con l'utente)
- `PLAN` → `GENERATE`
- `GENERATE` → `OPTIMIZE`
- `OPTIMIZE` → `TEST`
- `TEST` → `RETURN`
