import { useState, useRef, useEffect } from 'react'

const BACKEND = import.meta.env.VITE_BACKEND_URL || ''

const AGENT_LABELS = {
  onboarding:  'Aria · Onboarding',
  offboarding: 'Felix · Offboarding',
  compliance:  'Lex · Compliance',
  candidate:   'Scout · Talent',
  general:     'Nucleus',
}

const TOOL_LABELS = {
  search_candidates:              'Searched candidates',
  generate_onboarding_checklist:  'Built onboarding checklist',
  generate_offboarding_checklist: 'Built offboarding checklist',
  get_country_compliance_info:    'Checked compliance rules',
}

const SUGGESTIONS = [
  'Onboard Sophie Martin, Store Manager, Madrid, starting June 16',
  'Write a job description for a Sales Associate in Amsterdam',
  'What are the sick leave rules in Poland?',
  'Offboard Jean Dupont, Sales Associate, Netherlands, last day June 30',
  'Find candidates for a Store Manager role in Madrid',
  'Generate interview questions for a Store Manager position',
]

export default function ChatPanel({ onToolActive }) {
  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [sessionId]               = useState(() => Math.random().toString(36).slice(2))
  const bottomRef                 = useRef(null)
  const inputRef                  = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(text) {
    const msg = text || input.trim()
    if (!msg || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: msg }])
    setLoading(true)

    setMessages(prev => [...prev, { role: 'agent', text: '', agent: null, tools: [] }])

    const res = await fetch(`${BACKEND}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, session_id: sessionId }),
    })

    const data = await res.json()
    onToolActive(data.agent || null)

    setMessages(prev => {
      const next = [...prev]
      next[next.length - 1] = {
        role: 'agent',
        text: data.text,
        agent: data.agent,
        tools: data.tools_used || [],
      }
      return next
    })

    setTimeout(() => onToolActive(null), 1500)
    setLoading(false)
    inputRef.current?.focus()
  }

  function clear() {
    fetch(`${BACKEND}/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    setMessages([])
    onToolActive(null)
  }

  return (
    <div style={styles.panel}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.dot} />
          <span style={styles.title}>Nucleus</span>
          <span style={styles.sub}>HR Intelligence</span>
        </div>
        <button onClick={clear} style={styles.clearBtn}>clear</button>
      </div>

      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.empty}>
            <p style={styles.emptyTitle}>What do you need?</p>
            <div style={styles.suggestions}>
              {SUGGESTIONS.map((s, i) => (
                <button key={i} style={styles.suggestion} onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={m.role === 'user' ? styles.userMsg : styles.agentMsg}>
            {m.role === 'agent' && (
              <div style={styles.agentLabel}>
                <div style={styles.agentDot} />
                {AGENT_LABELS[m.agent] || 'nucleus'}
              </div>
            )}
            {m.tools && m.tools.length > 0 && (
              <div style={styles.toolBadge}>
                <span style={styles.toolDot} />
                {m.tools.map(t => TOOL_LABELS[t] || t).join(' · ')}
              </div>
            )}
            {m.text ? (
              <div style={styles.msgText}>{m.text}</div>
            ) : (
              <div style={styles.thinking}><span /><span /><span /></div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputRow}>
        <input
          ref={inputRef}
          style={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask about HR, onboarding, compliance…"
          disabled={loading}
        />
        <button
          style={{ ...styles.sendBtn, opacity: loading || !input.trim() ? 0.4 : 1 }}
          onClick={() => send()}
          disabled={loading || !input.trim()}
        >
          ↑
        </button>
      </div>
    </div>
  )
}

const styles = {
  panel: {
    display: 'flex', flexDirection: 'column', height: '100%',
    background: '#0c0c20', borderRight: '1px solid rgba(255,255,255,0.07)',
  },
  header: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '20px 24px', borderBottom: '1px solid rgba(255,255,255,0.07)',
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 10 },
  dot: { width: 10, height: 10, borderRadius: '50%', background: '#f5c842', boxShadow: '0 0 8px #f5c84288' },
  title: { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 700, fontSize: 18, color: '#fff' },
  sub: { fontSize: 12, color: '#6b6b8a', marginLeft: 4 },
  clearBtn: {
    background: 'none', border: '1px solid rgba(255,255,255,0.1)', color: '#6b6b8a',
    borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 12,
  },
  messages: { flex: 1, overflowY: 'auto', padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 16 },
  empty: { margin: 'auto', textAlign: 'center', maxWidth: 340 },
  emptyTitle: { color: '#6b6b8a', marginBottom: 16, fontSize: 13 },
  suggestions: { display: 'flex', flexDirection: 'column', gap: 8 },
  suggestion: {
    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
    color: '#a0a0c0', borderRadius: 8, padding: '8px 12px', cursor: 'pointer',
    fontSize: 12, textAlign: 'left', transition: 'all 0.15s',
  },
  userMsg: {
    alignSelf: 'flex-end', background: 'rgba(245,200,66,0.1)', border: '1px solid rgba(245,200,66,0.2)',
    borderRadius: '12px 12px 2px 12px', padding: '10px 14px', maxWidth: '80%',
  },
  agentMsg: {
    alignSelf: 'flex-start', maxWidth: '90%',
    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
    borderRadius: '2px 12px 12px 12px', padding: '10px 14px',
  },
  agentLabel: { display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#f5c842', marginBottom: 6, fontWeight: 600 },
  agentDot: { width: 6, height: 6, borderRadius: '50%', background: '#f5c842' },
  toolBadge: {
    display: 'flex', alignItems: 'center', gap: 6, fontSize: 11,
    color: '#6b6b8a', marginBottom: 8, fontStyle: 'italic',
  },
  toolDot: { width: 5, height: 5, borderRadius: '50%', background: '#6b6b8a', animation: 'pulse 1s infinite' },
  msgText: { lineHeight: 1.6, color: '#e8e8f0', whiteSpace: 'pre-wrap', wordBreak: 'break-word' },
  thinking: { display: 'flex', gap: 4, alignItems: 'center', padding: '4px 0' },
  inputRow: {
    display: 'flex', gap: 8, padding: '16px 24px',
    borderTop: '1px solid rgba(255,255,255,0.07)',
  },
  input: {
    flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 10, padding: '10px 14px', color: '#fff', fontSize: 14,
    outline: 'none', fontFamily: 'Inter, sans-serif',
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: 10, background: '#f5c842',
    border: 'none', color: '#04040f', fontSize: 18, cursor: 'pointer', fontWeight: 700,
  },
}
