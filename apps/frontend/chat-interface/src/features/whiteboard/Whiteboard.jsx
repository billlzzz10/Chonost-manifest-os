import { useEffect, useRef, useState } from 'react'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Eraser, Pen, RotateCcw } from 'lucide-react'

export function Whiteboard() {
  const canvasRef = useRef(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [tool, setTool] = useState('pen')
  const [color, setColor] = useState('#10B981')
  const [lineWidth, setLineWidth] = useState(3)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const resize = () => {
      const rect = canvas.getBoundingClientRect()
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      canvas.width = rect.width
      canvas.height = rect.height
      ctx.putImageData(imageData, 0, 0)
    }
    resize()
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')

    const getPos = (e) => {
      const rect = canvas.getBoundingClientRect()
      return { x: e.clientX - rect.left, y: e.clientY - rect.top }
    }

    const onDown = (e) => {
      setIsDrawing(true)
      const { x, y } = getPos(e)
      ctx.beginPath()
      ctx.moveTo(x, y)
    }

    const onMove = (e) => {
      if (!isDrawing) return
      const { x, y } = getPos(e)
      ctx.globalCompositeOperation = tool === 'eraser' ? 'destination-out' : 'source-over'
      ctx.strokeStyle = color
      ctx.lineWidth = lineWidth
      ctx.lineTo(x, y)
      ctx.stroke()
    }

    const onUp = () => setIsDrawing(false)

    canvas.addEventListener('mousedown', onDown)
    canvas.addEventListener('mousemove', onMove)
    canvas.addEventListener('mouseup', onUp)
    canvas.addEventListener('mouseleave', onUp)
    return () => {
      canvas.removeEventListener('mousedown', onDown)
      canvas.removeEventListener('mousemove', onMove)
      canvas.removeEventListener('mouseup', onUp)
      canvas.removeEventListener('mouseleave', onUp)
    }
  }, [isDrawing, tool, color, lineWidth])

  const clearCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-6">
        <Card>
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <CardTitle>Whiteboard</CardTitle>
              <div className="flex items-center space-x-2">
                <Button variant={tool === 'pen' ? 'default' : 'outline'} size="sm" onClick={() => setTool('pen')}>
                  <Pen className="w-4 h-4 mr-2" /> Pen
                </Button>
                <Button variant={tool === 'eraser' ? 'default' : 'outline'} size="sm" onClick={() => setTool('eraser')}>
                  <Eraser className="w-4 h-4 mr-2" /> Eraser
                </Button>
                <input type="color" value={color} onChange={(e) => setColor(e.target.value)} title="Color" />
                <input type="range" min={1} max={20} value={lineWidth} onChange={(e) => setLineWidth(parseInt(e.target.value))} title="Line width" />
                <Button variant="outline" size="sm" onClick={clearCanvas}>
                  <RotateCcw className="w-4 h-4 mr-2" /> Clear
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div style={{ height: '70vh' }}>
              <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block', cursor: tool === 'eraser' ? 'grab' : 'crosshair' }} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Whiteboard

