import { useState, useCallback } from 'react'
import ChatPanel from './components/ChatPanel'
import SpaceNetwork from './components/SpaceNetwork'

export default function App() {
  const [activeTool, setActiveTool] = useState(null)

  const handleToolActive = useCallback((tool) => {
    setActiveTool(tool)
  }, [])

  return (
    <div style={styles.root}>
      <div style={styles.chat}>
        <ChatPanel onToolActive={handleToolActive} />
      </div>
      <div style={styles.space}>
        <SpaceNetwork activeTool={activeTool} width={520} height={520} />
        <p style={styles.hint}>
          {activeTool
            ? `Routing to ${activeTool.replace(/_/g, ' ')}…`
            : 'Agents standing by'}
        </p>
      </div>
    </div>
  )
}

const styles = {
  root: {
    display: 'grid',
    gridTemplateColumns: '420px 1fr',
    height: '100vh',
    overflow: 'hidden',
  },
  chat: { overflow: 'hidden' },
  space: {
    display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    gap: 16, background: '#04040f',
  },
  hint: {
    fontSize: 12, color: '#3a3a5a',
    fontFamily: '"Space Grotesk", sans-serif',
    letterSpacing: '0.05em',
  },
}
