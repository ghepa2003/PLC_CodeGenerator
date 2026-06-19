import { useState, useEffect } from 'react';

interface Metadata {
  total_rungs: number;
  total_contacts: number;
  total_coils: number;
  complexity_score: number;
  execution_time_ms: number;
  model_used: string;
  timestamp: string;
}

interface LogMessage {
  level: string;
  code: string;
  message: string;
  suggestions: string[];
}

interface GenerateResult {
  success: boolean;
  ladder_code: string;
  visualization: string;
  metadata: Metadata;
  warnings: LogMessage[];
  errors: LogMessage[];
  clarifying_questions: string[];
  xml_codesys?: string;
}

export default function App() {
  const [inputNL, setInputNL] = useState<string>('');
  const [plcType, setPlcType] = useState<string>('allen_bradley');
  const [safetyLevel, setSafetyLevel] = useState<string>('medium');
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'ladder' | 'code'>('ladder');
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [alertList, setAlertList] = useState<{ type: 'warning' | 'error'; code: string; message: string; suggestions?: string[] }[]>([]);
  const [aiStatus, setAiStatus] = useState<'checking' | 'connected' | 'error' | 'mock'>('checking');
  const [aiErrorMsg, setAiErrorMsg] = useState<string>('');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch('/api/debug');
        const data = await res.json();
        if (data.is_mock_mode) {
           setAiStatus('mock');
           setAiErrorMsg('Nessuna chiave API inserita o chiave MOCK rilevata.');
        } else if (data.test_call_result === "ERROR") {
           setAiStatus('error');
           setAiErrorMsg(data.error_details || 'Errore di connessione API');
        } else {
           setAiStatus('connected');
        }
      } catch (e) {
        setAiStatus('error');
        setAiErrorMsg('Impossibile contattare il backend locale');
      }
    };
    checkStatus();
  }, []);

  const handleGenerate = async () => {
    if (!inputNL.trim()) {
      alert("Per favore, inserisci delle specifiche in linguaggio naturale.");
      return;
    }

    setLoading(true);
    setAlertList([]);
    setResult(null);

    try {
      const response = await fetch('/api/generate-ladder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input_nl: inputNL,
          plc_type: plcType,
          safety_level: safetyLevel,
        }),
      });

      const data = await response.json();
      
      const newAlerts: typeof alertList = [];
      
      // Handle warnings
      if (data.warnings && data.warnings.length > 0) {
        data.warnings.forEach((warn: LogMessage) => {
          newAlerts.push({
            type: 'warning',
            code: warn.code,
            message: warn.message,
            suggestions: warn.suggestions,
          });
        });
      }

      // Handle logic errors
      if (!data.success) {
        if (data.errors && data.errors.length > 0) {
          data.errors.forEach((err: LogMessage) => {
            newAlerts.push({
              type: 'error',
              code: err.code,
              message: err.message,
              suggestions: err.suggestions,
            });
          });
        }
        if (data.clarifying_questions && data.clarifying_questions.length > 0) {
          data.clarifying_questions.forEach((q: string) => {
            newAlerts.push({
              type: 'warning',
              code: 'AMBIGUITA_LOGICA',
              message: `Clarification needed: ${q}`,
            });
          });
        }
      } else {
        setResult(data);
        setActiveTab('ladder');
      }

      setAlertList(newAlerts);
    } catch (err) {
      console.error(err);
      setAlertList([{
        type: 'error',
        code: 'SERVER_ERROR',
        message: 'Impossibile connettersi al server backend locale. Assicurati che FastAPI sia in esecuzione.',
      }]);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (!result?.ladder_code) return;
    navigator.clipboard.writeText(result.ladder_code);
    alert("Codice Structured Text copiato!");
  };

  const downloadST = () => {
    if (!result?.ladder_code) return;
    const element = document.createElement("a");
    const file = new Blob([result.ladder_code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "plc_program.st";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const downloadXML = () => {
    if (!result?.xml_codesys) {
      alert("Nessun sorgente XML CODESYS generato.");
      return;
    }
    const element = document.createElement("a");
    const file = new Blob([result.xml_codesys], { type: 'text/xml' });
    element.href = URL.createObjectURL(file);
    element.download = "codesys_import.xml";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: 'var(--bg-app)' }}>
      {/* Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        padding: '12px 24px',
        backgroundColor: 'var(--bg-card)',
        borderBottom: '1px solid var(--border-color)',
        boxShadow: 'var(--shadow-sm)',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-success))',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            color: 'white',
            fontSize: '16px'
          }}>L</div>
          <h1 style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-main)' }}>PLC Ladder Logic Generator</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {/* AI Status Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500, padding: '4px 10px', borderRadius: '20px', backgroundColor: 'var(--bg-app)', border: '1px solid var(--border-color)' }}>
            {aiStatus === 'checking' && <span style={{ color: '#6b7280' }}>Verifica connessione AI...</span>}
            {aiStatus === 'connected' && <><div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }}></div><span style={{ color: '#059669' }}>AI Connessa</span></>}
            {aiStatus === 'mock' && <><div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#f59e0b' }}></div><span style={{ color: '#d97706' }} title={aiErrorMsg}>Modalità MOCK (Locale)</span></>}
            {aiStatus === 'error' && <><div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#ef4444' }}></div><span style={{ color: '#dc2626' }} title={aiErrorMsg}>Errore AI: Passa il mouse qui</span></>}
          </div>

          <span style={{
            backgroundColor: 'var(--accent-primary-light)',
            border: '1px solid rgba(79, 70, 229, 0.15)',
            color: 'var(--accent-primary)',
            padding: '4px 10px',
            borderRadius: '99px',
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.5px'
          }}>Vite + React Dashboard</span>
        </div>
      </header>

      {/* Main Layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        
        {/* Left Input Sidebar */}
        <div style={{
          width: '380px',
          backgroundColor: 'var(--bg-card)',
          borderRight: '1px solid var(--border-color)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '20px',
          overflowY: 'auto'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Specifiche in Linguaggio Naturale</label>
            <textarea
              value={inputNL}
              onChange={(e) => setInputNL(e.target.value)}
              placeholder="Esempio:
Se pulsante START premuto E sensore_livello > 80, attiva valvola_scarico.
Se valvola_scarico attiva per 5 secondi, accendi segnale_allarme."
              style={{
                width: '100%',
                height: '180px',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                color: 'var(--text-main)',
                padding: '12px',
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                lineHeight: '1.5',
                resize: 'none',
                outline: 'none',
                transition: 'all 0.2s'
              }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Marca PLC</label>
              <select
                value={plcType}
                onChange={(e) => setPlcType(e.target.value)}
                style={{
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-main)',
                  padding: '8px 10px',
                  fontSize: '13px',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="siemens">Siemens (TIA)</option>
                <option value="allen_bradley">Allen Bradley</option>
                <option value="beckhoff">Beckhoff (TC3)</option>
                <option value="mitsubishi">Mitsubishi</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Sicurezza</label>
              <select
                value={safetyLevel}
                onChange={(e) => setSafetyLevel(e.target.value)}
                style={{
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-main)',
                  padding: '8px 10px',
                  fontSize: '13px',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="low">Bassa</option>
                <option value="medium">Media</option>
                <option value="high">Alta</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading}
            style={{
              background: 'linear-gradient(135deg, var(--accent-primary), #3b82f6)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px',
              fontWeight: 600,
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(79, 70, 229, 0.15)',
              transition: 'all 0.2s'
            }}
          >
            {loading ? (
              <>
                <span className="spinner" style={{
                  display: 'inline-block',
                  width: '14px',
                  height: '14px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderRadius: '50%',
                  borderTopColor: 'white',
                  animation: 'spin 0.8s linear infinite',
                  marginRight: '4px'
                }}></span>
                Elaborazione in corso...
              </>
            ) : "Genera Diagramma"}
          </button>

          <div style={{
            backgroundColor: 'var(--accent-primary-light)',
            border: '1px solid rgba(79, 70, 229, 0.12)',
            borderRadius: '8px',
            padding: '14px',
            fontSize: '12px',
            color: 'var(--text-muted)',
            lineHeight: '1.6'
          }}>
            <h4 style={{ color: 'var(--text-main)', fontWeight: 600, marginBottom: '6px' }}>💡 Suggerimenti</h4>
            <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
              <li style={{ marginBottom: '4px' }}>• Usa verbi d'azione come "attiva", "avvia", "spegni".</li>
              <li style={{ marginBottom: '4px' }}>• Specifica timer con "per X secondi" o "dopo X sec".</li>
              <li>• Per sensori analogici indica soglie numeriche (es. &gt; 50).</li>
            </ul>
          </div>
        </div>

        {/* Right Output Panel */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', backgroundColor: 'var(--bg-app)' }}>
          {/* Tabs */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-color)',
            padding: '0 24px',
            backgroundColor: 'var(--bg-card)'
          }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => setActiveTab('ladder')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: activeTab === 'ladder' ? 'var(--accent-primary)' : 'var(--text-muted)',
                  padding: '16px 20px',
                  fontSize: '13px',
                  fontWeight: activeTab === 'ladder' ? 600 : 500,
                  cursor: 'pointer',
                  borderBottom: activeTab === 'ladder' ? '2px solid var(--accent-primary)' : '2px solid transparent',
                  outline: 'none'
                }}
              >
                Diagramma Ladder
              </button>
              <button
                onClick={() => setActiveTab('code')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: activeTab === 'code' ? 'var(--accent-primary)' : 'var(--text-muted)',
                  padding: '16px 20px',
                  fontSize: '13px',
                  fontWeight: activeTab === 'code' ? 600 : 500,
                  cursor: 'pointer',
                  borderBottom: activeTab === 'code' ? '2px solid var(--accent-primary)' : '2px solid transparent',
                  outline: 'none'
                }}
              >
                Codice Structured Text (ST)
              </button>
            </div>

            {result && (
              <div style={{ display: 'flex', gap: '10px' }}>
                {activeTab === 'code' && (
                  <button
                    onClick={copyCode}
                    style={{
                      backgroundColor: 'white',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-main)',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontWeight: 500
                    }}
                  >
                    Copia ST
                  </button>
                )}
                <button
                  onClick={downloadST}
                  style={{
                    backgroundColor: 'white',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontWeight: 500
                  }}
                >
                  Scarica .ST
                </button>
                {result.xml_codesys && (
                  <button
                    onClick={downloadXML}
                    style={{
                      backgroundColor: 'var(--accent-success-light)',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                      color: '#065f46',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontWeight: 600
                    }}
                  >
                    Scarica XML CODESYS
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Alert messages and panels */}
          <div style={{ flex: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {alertList.map((alert, idx) => (
              <div
                key={idx}
                style={{
                  backgroundColor: alert.type === 'error' ? 'var(--accent-danger-light)' : 'var(--accent-warning-light)',
                  border: `1px solid ${alert.type === 'error' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`,
                  color: alert.type === 'error' ? '#991b1b' : '#92400e',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  lineHeight: '1.5'
                }}
              >
                <strong>[{alert.code}]</strong> {alert.message}
                {alert.suggestions && alert.suggestions.length > 0 && (
                  <ul style={{ paddingLeft: '20px', marginTop: '6px', fontSize: '11px', opacity: 0.9 }}>
                    {alert.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                )}
              </div>
            ))}

            {/* Ladder SVG Rendering Panel */}
            {activeTab === 'ladder' && (
              <div style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'white',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '24px',
                boxShadow: 'var(--shadow-sm)',
                minHeight: '350px'
              }}>
                {result?.visualization ? (
                  <div
                    style={{ width: '100%', maxWidth: '900px' }}
                    dangerouslySetInnerHTML={{ __html: result.visualization }}
                  />
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center' }}>
                    <div style={{ fontSize: '32px', marginBottom: '8px', opacity: 0.4 }}>📊</div>
                    Il diagramma Ladder a contatti verrà renderizzato qui.
                  </div>
                )}
              </div>
            )}

            {/* Code Panel */}
            {activeTab === 'code' && (
              <div style={{
                flex: 1,
                backgroundColor: '#1e293b',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                minHeight: '350px'
              }}>
                {result?.ladder_code ? (
                  <pre style={{ margin: 0, padding: '20px', overflowX: 'auto', height: '100%' }}>
                    <code style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: '#38bdf8', lineHeight: '1.6' }}>
                      {result.ladder_code}
                    </code>
                  </pre>
                ) : (
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#94a3b8', fontSize: '13px' }}>
                    <div style={{ fontSize: '32px', marginBottom: '8px', opacity: 0.4 }}>💻</div>
                    Il codice Structured Text (ST) verrà mostrato qui.
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer Metadata */}
          {result && (
            <div style={{
              borderTop: '1px solid var(--border-color)',
              padding: '12px 24px',
              backgroundColor: 'var(--bg-card)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '11px',
              color: 'var(--text-muted)'
            }}>
              <div style={{ display: 'flex', gap: '20px' }}>
                <div>Rung totali: <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{result.metadata.total_rungs}</span></div>
                <div>Contatti: <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{result.metadata.total_contacts}</span></div>
                <div>Bobine: <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{result.metadata.total_coils}</span></div>
                <div>Complessità: <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{(result.metadata.complexity_score * 100).toFixed(0)}%</span></div>
                <div>Tempo: <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{result.metadata.execution_time_ms}ms</span></div>
              </div>
              <div>Motore AI: {result.metadata.model_used}</div>
            </div>
          )}
        </div>
      </div>
      
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
