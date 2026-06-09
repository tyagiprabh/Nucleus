import { useEffect, useRef } from 'react'

const AGENTS = [
  { id: 'search_candidates',             label: 'Candidate\nResearch',  color: '#4a9eff', angle: 315 },
  { id: 'generate_onboarding_checklist', label: 'Onboarding',           color: '#4aff9e', angle: 45  },
  { id: 'generate_offboarding_checklist',label: 'Offboarding',          color: '#ff6b4a', angle: 135 },
  { id: 'get_country_compliance_info',   label: 'Compliance',           color: '#b44aff', angle: 225 },
]

const ORBIT_R = 170
const NUCLEUS_R = 38
const PLANET_R = 22

function toXY(angle, r, cx, cy) {
  const rad = (angle * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

export default function SpaceNetwork({ activeTool, width = 480, height = 480 }) {
  const canvasRef = useRef(null)
  const animRef   = useRef(null)
  const pulseRef  = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    const cx = width / 2
    const cy = height / 2

    function drawStars() {
      // deterministic star field
      const rng = (seed) => { let s = seed; return () => { s = (s * 16807 + 0) % 2147483647; return (s - 1) / 2147483646 } }
      const rand = rng(42)
      for (let i = 0; i < 120; i++) {
        const x = rand() * width
        const y = rand() * height
        const r = rand() * 1.2
        const a = 0.2 + rand() * 0.6
        ctx.beginPath()
        ctx.arc(x, y, r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,255,255,${a})`
        ctx.fill()
      }
    }

    function drawOrbitRing(x, y, r, color) {
      ctx.beginPath()
      ctx.arc(x, y, r, 0, Math.PI * 2)
      ctx.strokeStyle = `${color}22`
      ctx.lineWidth = 1
      ctx.setLineDash([4, 6])
      ctx.stroke()
      ctx.setLineDash([])
    }

    function drawGlow(x, y, r, color, alpha = 0.35) {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.5)
      g.addColorStop(0, color.replace(')', `,${alpha})`).replace('rgb', 'rgba'))
      g.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(x, y, r * 2.5, 0, Math.PI * 2)
      ctx.fillStyle = g
      ctx.fill()
    }

    function drawConnection(x1, y1, x2, y2, color, pulse) {
      const grad = ctx.createLinearGradient(x1, y1, x2, y2)
      grad.addColorStop(0, `${color}99`)
      grad.addColorStop(pulse, `${color}ff`)
      grad.addColorStop(Math.min(pulse + 0.15, 1), `${color}ff`)
      grad.addColorStop(1, `${color}33`)
      ctx.beginPath()
      ctx.moveTo(x1, y1)
      ctx.lineTo(x2, y2)
      ctx.strokeStyle = grad
      ctx.lineWidth = 2
      ctx.stroke()
    }

    function drawPlanet(x, y, r, color, label, isActive) {
      // glow
      if (isActive) drawGlow(x, y, r, color, 0.5)

      // body
      const g = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, 0, x, y, r)
      g.addColorStop(0, color + 'ff')
      g.addColorStop(0.6, color + 'cc')
      g.addColorStop(1, color + '66')
      ctx.beginPath()
      ctx.arc(x, y, r, 0, Math.PI * 2)
      ctx.fillStyle = g
      ctx.fill()

      // ring for active
      if (isActive) {
        ctx.beginPath()
        ctx.arc(x, y, r + 6, 0, Math.PI * 2)
        ctx.strokeStyle = color + 'aa'
        ctx.lineWidth = 2
        ctx.stroke()
      }

      // label
      ctx.font = '500 11px Inter'
      ctx.fillStyle = '#ffffff'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      label.split('\n').forEach((line, i) => {
        ctx.fillText(line, x, y + r + 8 + i * 14)
      })
    }

    function frame(ts) {
      pulseRef.current = (ts / 1200) % 1

      ctx.clearRect(0, 0, width, height)

      // background
      ctx.fillStyle = '#04040f'
      ctx.fillRect(0, 0, width, height)

      drawStars()

      // orbit circles
      AGENTS.forEach(a => {
        const pos = toXY(a.angle, ORBIT_R, cx, cy)
        drawOrbitRing(cx, cy, ORBIT_R, a.color)
      })

      // connections + planets
      AGENTS.forEach(a => {
        const pos = toXY(a.angle, ORBIT_R, cx, cy)
        const isActive = activeTool === a.id
        if (isActive) {
          drawConnection(cx, cy, pos.x, pos.y, a.color, pulseRef.current)
        } else {
          ctx.beginPath()
          ctx.moveTo(cx, cy)
          ctx.lineTo(pos.x, pos.y)
          ctx.strokeStyle = `${a.color}18`
          ctx.lineWidth = 1
          ctx.stroke()
        }
        drawPlanet(pos.x, pos.y, PLANET_R, a.color, a.label, isActive)
      })

      // nucleus glow
      drawGlow(cx, cy, NUCLEUS_R, '#f5c842', 0.3)

      // nucleus body
      const ng = ctx.createRadialGradient(cx - 10, cy - 10, 0, cx, cy, NUCLEUS_R)
      ng.addColorStop(0, '#fff8d6')
      ng.addColorStop(0.4, '#f5c842')
      ng.addColorStop(1, '#c8920a')
      ctx.beginPath()
      ctx.arc(cx, cy, NUCLEUS_R, 0, Math.PI * 2)
      ctx.fillStyle = ng
      ctx.fill()

      // nucleus label
      ctx.font = '700 12px "Space Grotesk"'
      ctx.fillStyle = '#04040f'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('NUCLEUS', cx, cy)

      animRef.current = requestAnimationFrame(frame)
    }

    animRef.current = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(animRef.current)
  }, [activeTool, width, height])

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ display: 'block' }}
    />
  )
}
