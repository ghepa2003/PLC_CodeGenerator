# ORCHESTRATION: Error Handling Strategy

## Error Categories

1. **INPUT_AMBIGUOUS**
   - *Causa*: Il testo inserito contiene nomi generici o relazioni booleane non chiare.
   - *Gestione*: L'agente Validator interrompe il flusso ed evidenzia le parti ambigue nel campo `errors` dell'output API, indicando domande precise (es. "Ci sono più pompe descritte, a quale ti riferisci?").

2. **LOGIC_CONFLICT**
   - *Causa*: Due condizioni provano a forzare lo stesso output digitale a stati diversi contemporaneamente (es. "Se A attiva pompa, se B disattiva pompa" senza mutua esclusione definita).
   - *Gestione*: Viene sollevato un errore di validazione logica con l'invito a rivedere le condizioni di marcia ed arresto.

3. **SAFETY_VIOLATION**
   - *Causa*: Mancanza di un pulsante di stop o di un interblocco di emergenza in logiche ad alto rischio (es. motori o presse) quando il `safety_level` è impostato su `high`.
   - *Gestione*: Blocco della generazione o aggiunta automatica (con relativo warning) di una condizione di E-Stop (`btn_estop`) in serie su tutti i rung.

4. **API_FAILURE**
   - *Causa*: Servizio OpenRouter non raggiungibile o credenziali non valide.
   - *Gestione*: Rilevamento dell'eccezione HTTP, log di errore sul server e restituzione di un messaggio amichevole all'utente ("Errore di connessione con il servizio AI. Riprova più tardi.").
