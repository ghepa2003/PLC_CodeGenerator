# PLC Ladder Logic Generator 🚀

Un'applicazione full-stack (React/Vite + Python/FastAPI) per generare diagrammi Ladder (Logica Programmabile per PLC) partendo da specifiche in linguaggio naturale.

L'utente inserisce una descrizione (es: "se il pulsante A è premuto, attiva il motore M1") e il sistema analizza il testo estraendo le variabili, per poi tradurle in un diagramma visivo e in formato ST (Structured Text) e XML.

## 🛠 Tecnologie
* **Frontend**: React, Vite, TypeScript, CSS (Vanilla)
* **Backend**: Python, FastAPI
* **Intelligenza Artificiale**: OpenRouter (Claude 3.5 / Llama 3) via agenti autonomi.

## 📦 Installazione Locale

Se vuoi eseguire il progetto sul tuo computer, hai bisogno di Node.js e Python 3.9+.

### 1. Clona il Repository
```bash
git clone <URL_DEL_REPO>
cd PLC_CodeGenerator
```

### 2. Configura il Backend
Nella cartella principale, spostati in `api/` (che funge da backend) o esegui tutto dalla root:
```bash
# Crea l'ambiente virtuale
python -m venv .venv
# Attivalo (Windows)
.\.venv\Scripts\activate
# (Mac/Linux: source .venv/bin/activate)

# Installa le dipendenze
pip install -r requirements.txt
```

Crea un file `.env` dentro la cartella `api/` con la tua API Key di OpenRouter:
```
OPENROUTER_API_KEY=sk-or-v1-tuachiave...
```

Per lanciare il server:
```bash
uvicorn api.index:app --reload
```
*(Il backend girerà su http://localhost:8000)*

### 3. Configura il Frontend
In un altro terminale, nella cartella principale (root):
```bash
npm install
npm run dev
```
*(Il frontend girerà su http://localhost:5173)*

## 🌐 Deployment su Vercel (All-in-One)

Questo repository è già ottimizzato per essere distribuito su Vercel in un solo passaggio, combinando **Vite** e **Vercel Serverless Functions** (Python).

1. Crea un account su [Vercel](https://vercel.com/) e collega il tuo GitHub.
2. Clicca su **"Add New Project"** e seleziona questo repository.
3. Nei "Environment Variables" inserisci:
   * `OPENROUTER_API_KEY`: la tua chiave segreta.
4. Clicca su **Deploy**. 

Vercel leggerà automaticamente il file `vercel.json`, installerà il frontend tramite `package.json` e configurerà le API Python in `/api/index.py`.

---
*Progetto creato e supportato con intelligenza artificiale per l'ottimizzazione del codice industriale.*
