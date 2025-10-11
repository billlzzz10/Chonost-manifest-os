import { useCallback, useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'
import { differenceInSeconds, format } from 'date-fns'
import { AlertTriangle, CheckCircle2, Clock, Shield, ShieldAlert, Undo2 } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/shared/ui/collapsible'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/shared/ui/dialog'
import { Textarea } from '@/shared/ui/textarea'
import { ChartContainer, ChartTooltipContent } from '@/shared/ui/chart'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type {
  ActionButton,
  ActionState,
  CardLayout,
  CardState,
  ConfirmationState,
  ExecutionResult,
  MermaidConfig,
} from '../card-system/cardSchemas'
import { cardStateSchema } from '../card-system/cardSchemas'

const SIGNAL_COLORS: Record<CardLayout['header']['signalBadge'], string> = {
  info: 'bg-blue-100 text-blue-800 border-blue-200',
  success: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  warning: 'bg-amber-100 text-amber-800 border-amber-200',
  critical: 'bg-rose-100 text-rose-800 border-rose-200',
  neutral: 'bg-slate-100 text-slate-800 border-slate-200',
}

type ActionStateMap = Record<string, ActionState>

type OperationalInsightCardProps = {
  layout: CardLayout
  onExecuteCli?: (command: string, sandboxed: boolean) => Promise<ExecutionResult | null>
}

const sanitizeSvg = (raw: string) => {
  const allowedTags = new Set(['svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'text', 'tspan', 'defs', 'marker', 'title', 'desc', 'style'])
  const allowedAttrs = new Set([
    'id',
    'class',
    'fill',
    'stroke',
    'stroke-width',
    'stroke-linecap',
    'stroke-linejoin',
    'stroke-dasharray',
    'stroke-dashoffset',
    'd',
    'x',
    'y',
    'width',
    'height',
    'viewBox',
    'transform',
    'cx',
    'cy',
    'r',
    'points',
    'x1',
    'x2',
    'y1',
    'y2',
    'marker-start',
    'marker-mid',
    'marker-end',
    'font-size',
    'font-family',
    'opacity',
  ])

  const parser = new DOMParser()
  const doc = parser.parseFromString(raw, 'image/svg+xml')
  const errorNode = doc.querySelector('parsererror')
  if (errorNode) {
    throw new Error('Mermaid render produced invalid SVG output.')
  }

  const cleanse = (node: Element) => {
    if (!allowedTags.has(node.tagName)) {
      node.remove()
      return
    }
    for (const attr of Array.from(node.attributes)) {
      if (!allowedAttrs.has(attr.name)) {
        node.removeAttribute(attr.name)
      }
    }
    for (const child of Array.from(node.children)) {
      cleanse(child)
    }
  }

  cleanse(doc.documentElement)
  const serializer = new XMLSerializer()
  return serializer.serializeToString(doc.documentElement)
}

const MermaidPreview = ({ config, previewMode }: { config: MermaidConfig; previewMode: boolean }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!previewMode || !containerRef.current) return

    const renderDiagram = async () => {
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: 'strict' })
        const { svg } = await mermaid.render(
          `mermaid-${Math.random().toString(36).slice(2)}`,
          config.syntax,
        )
        const sanitized = sanitizeSvg(svg)
        const parsed = new DOMParser().parseFromString(sanitized, 'image/svg+xml')
        const svgElement = parsed.documentElement

        containerRef.current.innerHTML = ''
        containerRef.current.appendChild(svgElement)
        setError(null)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to render Mermaid diagram.'
        if (config.errorHandling?.showErrors !== false) {
          setError(message)
        }
        if (config.errorHandling?.fallbackToCode !== false && containerRef.current) {
          containerRef.current.innerHTML = ''
        }
      }
    }

    renderDiagram()
  }, [config, previewMode])

  return (
    <div className="space-y-2" data-testid="mermaid-preview">
      <div
        ref={containerRef}
        className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900"
      />
      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
    </div>
  )
}

const formatDate = (date: Date) => format(date, 'yyyy-MM-dd HH:mm')

const getInitialMermaidPreviewState = (layout: CardLayout) => {
  const block = layout.content.mermaidBlock
  if (!block) return false

  switch (block.viewMode) {
    case 'preview':
    case 'split':
      return true
    case 'code':
      return false
    default:
      // Provide explicit fallback for unknown view modes
      return block.autoRender ?? false
  }
}

const buildInitialCardState = (layout: CardLayout): CardState =>
  cardStateSchema.parse({
    isExpanded: true,
    editingCLI: false,
    showingMermaidPreview: getInitialMermaidPreviewState(layout),
    confirmationModal: null,
    sandboxMode: layout.content.cliSnippet.execution.sandboxed,
    undoTimer: null,
  })

const createInitialActionState = (actions: ActionButton[]): ActionStateMap => {
  return actions.reduce<ActionStateMap>((acc, action) => {
    acc[action.id] = {
      type: action.type,
      status: 'idle',
      result: undefined,
      canUndo: false,
      undoDeadline: undefined,
    }
    return acc
  }, {})
}

const mergeActionStates = (layout: CardLayout): ActionStateMap => ({
  ...createInitialActionState(layout.actions.primary),
  ...createInitialActionState(layout.actions.secondary ?? []),
})

const validateCommand = (command: string, validation: CardLayout['content']['cliSnippet']['validation']) => {
  if (validation.allowedCommands?.length) {
    const allowed = validation.allowedCommands.some((allowedCommand) => command.trim().startsWith(allowedCommand))
    if (!allowed) {
      return `Command must start with one of: ${validation.allowedCommands.join(', ')}`
    }
  }
  if (validation.blockedPatterns?.length) {
    const blockedMatch = validation.blockedPatterns.find((pattern) => pattern.test(command))
    if (blockedMatch) {
      return `Command blocked by safety rule: ${blockedMatch}`
    }
  }
  return null
}

export function OperationalInsightCard({ layout, onExecuteCli }: OperationalInsightCardProps) {
  const [cardState, setCardState] = useState<CardState>(() => buildInitialCardState(layout))
  const [cliCommand, setCliCommand] = useState(layout.content.cliSnippet.command)
  const [cliError, setCliError] = useState<string | null>(null)
  const [actionStates, setActionStates] = useState<ActionStateMap>(() => mergeActionStates(layout))
  const [metrics, setMetrics] = useState(() => layout.metrics)
  const [showUndoAction, setShowUndoAction] = useState<string | null>(null)

  useEffect(() => {
    setCardState(buildInitialCardState(layout))
    setCliCommand(layout.content.cliSnippet.command)
    setActionStates(mergeActionStates(layout))
    setMetrics(layout.metrics)
  }, [layout])

  useEffect(() => {
    if (!showUndoAction) return

    const action = actionStates[showUndoAction]
    if (!action?.undoDeadline) return

    const interval = setInterval(() => {
      setActionStates((prev) => {
        const current = prev[showUndoAction]
        if (!current?.undoDeadline) return prev
        if (differenceInSeconds(current.undoDeadline, new Date()) <= 0) {
          return {
            ...prev,
            [showUndoAction]: { ...current, canUndo: false, undoDeadline: undefined },
          }
        }
        return prev
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [showUndoAction, actionStates])

  const handleToggleExpand = () => {
    setCardState((state) => ({ ...state, isExpanded: !state.isExpanded }))
  }

  const runAction = useCallback(
    async (action: ActionButton) => {
      setActionStates((prev) => ({
        ...prev,
        [action.id]: { ...prev[action.id], status: 'running', result: undefined },
      }))

      const startedAt = new Date()
      try {
        if (action.safety?.requiresSandbox && !cardState.sandboxMode) {
          throw new Error('Sandbox mode is required for this action.')
        }

        let executionResult: ExecutionResult | null = null
        if (action.id === 'execute-sandbox' && onExecuteCli) {
          executionResult = await onExecuteCli(cliCommand, cardState.sandboxMode)
        }

        await new Promise((resolve) => setTimeout(resolve, 650))

        const result: ExecutionResult =
          executionResult ?? {
            message: `${action.label} completed successfully`,
            output: [`Action ${action.id} executed with sandbox=${cardState.sandboxMode}`],
            startedAt,
            completedAt: new Date(),
          }

        const undoDeadline = action.undoWindowSeconds
          ? new Date(Date.now() + action.undoWindowSeconds * 1000)
          : undefined

        setActionStates((prev) => ({
          ...prev,
          [action.id]: {
            ...prev[action.id],
            status: 'success',
            result,
            canUndo: Boolean(action.undoWindowSeconds),
            undoDeadline,
          },
        }))
        if (undoDeadline) {
          setShowUndoAction(action.id)
        }
        setMetrics((prev) =>
          prev
            ? {
                ...prev,
                usage: {
                  ...prev.usage,
                  executions: action.type === 'execute' ? prev.usage.executions + 1 : prev.usage.executions,
                  rollbacks: action.type === 'rollback' ? prev.usage.rollbacks + 1 : prev.usage.rollbacks,
                },
              }
            : prev,
        )
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Action failed to complete.'
        setActionStates((prev) => ({
          ...prev,
          [action.id]: {
            ...prev[action.id],
            status: 'error',
            result: {
              message,
              errors: [message],
              startedAt,
              completedAt: new Date(),
            },
            canUndo: false,
            undoDeadline: undefined,
          },
        }))
      }
    },
    [cardState.sandboxMode, cliCommand, onExecuteCli],
  )

  const triggerAction = useCallback(
    (action: ActionButton) => {
      if (action.confirmation?.required) {
        const confirmation: ConfirmationState = {
          actionId: action.id,
          config: action.confirmation,
          open: true,
        }
        setCardState((state) => ({ ...state, confirmationModal: confirmation }))
      } else {
        runAction(action)
      }
    },
    [runAction],
  )

  const confirmAction = useCallback(() => {
    if (!cardState.confirmationModal) return
    const actionId = cardState.confirmationModal.actionId
    const allActions = [...layout.actions.primary, ...(layout.actions.secondary ?? [])]
    const action = allActions.find((item) => item.id === actionId)
    if (!action) {
      setCardState((state) => ({ ...state, confirmationModal: null }))
      return
    }
    setCardState((state) => ({ ...state, confirmationModal: null }))
    runAction(action)
  }, [cardState.confirmationModal, layout.actions.primary, layout.actions.secondary, runAction])

  const cancelAction = () => {
    setCardState((state) => ({ ...state, confirmationModal: null }))
  }

  const handleUndo = useCallback(
    (actionId: string) => {
      setActionStates((prev) => ({
        ...prev,
        [actionId]: {
          ...prev[actionId],
          status: 'idle',
          result: {
            message: 'Action rolled back safely.',
            startedAt: new Date(),
            completedAt: new Date(),
          },
          canUndo: false,
          undoDeadline: undefined,
        },
      }))
      setMetrics((prev) =>
        prev
          ? {
              ...prev,
              usage: { ...prev.usage, rollbacks: prev.usage.rollbacks + 1 },
            }
          : prev,
      )
      setShowUndoAction(null)
    },
    [],
  )

  const updateCliCommand = (value: string) => {
    setCliCommand(value)
    setCliError(null)
    const errorMessage = validateCommand(value, layout.content.cliSnippet.validation)
    if (errorMessage) {
      setCliError(errorMessage)
    }
  }

  const toggleSandbox = () => {
    setCardState((state) => ({ ...state, sandboxMode: !state.sandboxMode }))
  }

  const signalColor = SIGNAL_COLORS[layout.header.signalBadge]
  const mermaidBlock = layout.content.mermaidBlock
  const mermaidViewMode = mermaidBlock?.viewMode ?? 'code'
  const mermaidEditable = mermaidBlock?.editable ?? false
  const showMermaidToggle = Boolean(mermaidBlock) && mermaidEditable && (mermaidViewMode === 'code' || mermaidViewMode === 'preview')

  // Determine visibility based on view mode
  const getMermaidVisibility = () => {
    if (!mermaidBlock) return { preview: false, code: false }
    
    switch (mermaidViewMode) {
      case 'split':
        return { preview: true, code: true }
      case 'preview':
        return { preview: true, code: false }
      case 'code':
        return { preview: false, code: true }
      default:
        // For editable blocks with toggle, use state
        if (showMermaidToggle) {
          return {
            preview: cardState.showingMermaidPreview,
            code: !cardState.showingMermaidPreview,
          }
        }
        return { preview: false, code: true }
    }
  }

  const { preview: mermaidPreviewVisible, code: mermaidCodeVisible } = getMermaidVisibility()

  const renderChart = () => {
    if (!layout.content.mainChart) return null
    const { type, data } = layout.content.mainChart
    const chartData = data.map((point) => ({ ...point, timestamp: point.timestamp.getTime() }))

    return (
      <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <ChartContainer
          id={`${layout.id}-chart`}
          config={Object.fromEntries(
            data.map((point) => [point.label ?? 'value', { label: point.label ?? 'Value', color: 'var(--primary)' }]),
          )}
        >
          <ResponsiveContainer width="100%" height="100%">
            {(() => {
              switch (type) {
                case 'line':
                  return (
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                        type="number"
                        domain={['dataMin', 'dataMax']}
                      />
                      <YAxis />
                      <Tooltip content={<ChartTooltipContent />} />
                      <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} dot={false} />
                    </LineChart>
                  )
                case 'bar':
                  return (
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                        type="number"
                        domain={['dataMin', 'dataMax']}
                      />
                      <YAxis />
                      <Tooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="value" fill="rgba(37, 99, 235, 0.7)" />
                    </BarChart>
                  )
                case 'scatter':
                  return (
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                        type="number"
                        domain={['dataMin', 'dataMax']}
                      />
                      <YAxis dataKey="value" />
                      <Tooltip content={<ChartTooltipContent />} />
                      <Scatter data={chartData} fill="rgba(37, 99, 235, 0.8)" />
                    </ScatterChart>
                  )
                case 'area':
                default:
                  return (
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timestamp"
                        tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                        type="number"
                        domain={['dataMin', 'dataMax']}
                      />
                      <YAxis />
                      <Tooltip content={<ChartTooltipContent />} />
                      <Area type="monotone" dataKey="value" stroke="#2563eb" fill="rgba(37, 99, 235, 0.2)" />
                    </AreaChart>
                  )
              }
            })()}
          </ResponsiveContainer>
        </ChartContainer>
      </div>
    )
  }

  const renderSafetyChecks = () => {
    if (!layout.safety) return null
    return (
      <div className="mt-4 grid gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Safety & Guardrails</h4>
        <div className="grid gap-2 text-sm">
          <div className="flex items-center justify-between">
            <span>Policy Compliance</span>
            <Badge variant={layout.safety.policyCompliance ? 'default' : 'destructive'}>
              {layout.safety.policyCompliance ? 'Pass' : 'Fail'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span>Data Privacy</span>
            <Badge variant={layout.safety.dataPrivacy ? 'default' : 'destructive'}>
              {layout.safety.dataPrivacy ? 'Pass' : 'Fail'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span>Security Risk</span>
            <Badge>{layout.safety.securityRisk}</Badge>
          </div>
          <div className="flex items-center justify-between">
            <span>Destructive Potential</span>
            <Badge variant={layout.safety.destructivePotential ? 'destructive' : 'default'}>
              {layout.safety.destructivePotential ? 'High' : 'Controlled'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span>Sandbox Required</span>
            <Badge variant={layout.safety.requiresSandbox ? 'default' : 'destructive'}>
              {layout.safety.requiresSandbox ? 'Required' : 'Optional'}
            </Badge>
          </div>
        </div>
      </div>
    )
  }

  const renderAssessment = () => (
    <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Risk Rating</p>
          <p className="text-lg font-semibold text-slate-900 dark:text-slate-100">{layout.assessment.riskRating}</p>
        </div>
        <Shield className="h-6 w-6 text-slate-500" />
      </div>
      <div>
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Impact Projection</h4>
        <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
          <li><strong>Best:</strong> {layout.assessment.impactEstimate.bestCase}</li>
          <li><strong>Expected:</strong> {layout.assessment.impactEstimate.expectedCase}</li>
          <li><strong>Worst:</strong> {layout.assessment.impactEstimate.worstCase}</li>
        </ul>
      </div>
      <div>
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Cost Estimate</h4>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          ${layout.assessment.costEstimate.estimated.usd.toFixed(2)} (latency {layout.assessment.costEstimate.estimated.latency}
          ms)
        </p>
      </div>
      <div>
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Confidence Breakdown</h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <span>Data: {layout.assessment.confidenceBreakdown.dataQuality}%</span>
          <span>Methodology: {layout.assessment.confidenceBreakdown.methodology}%</span>
          <span>Review: {layout.assessment.confidenceBreakdown.humanReview}%</span>
          <span>History: {layout.assessment.confidenceBreakdown.historicalSuccess}%</span>
        </div>
      </div>
    </div>
  )

  const renderActions = (actions: ActionButton[], variant: 'primary' | 'secondary') => (
    <div className="flex flex-wrap gap-2">
      {actions.map((action) => {
        const state = actionStates[action.id]
        const isRunning = state?.status === 'running'
        const isSuccess = state?.status === 'success'
        const isError = state?.status === 'error'
        const undoActive = state?.canUndo && state.undoDeadline && differenceInSeconds(state.undoDeadline, new Date()) > 0

        return (
          <div key={action.id} className="flex items-center gap-2">
            <Button
              variant={action.intent === 'danger' ? 'destructive' : action.intent === 'primary' ? 'default' : 'outline'}
              disabled={action.disabled || isRunning}
              onClick={() => triggerAction(action)}
              title={action.tooltip}
            >
              {isRunning ? 'Running…' : action.label}
            </Button>
            {variant === 'primary' && isSuccess && state?.result ? (
              <Badge variant="default" className="flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Success
              </Badge>
            ) : null}
            {isError && state?.result ? (
              <Badge variant="destructive" className="flex items-center gap-1">
                <ShieldAlert className="h-3.5 w-3.5" />
                Failed
              </Badge>
            ) : null}
            {undoActive ? (
              <Button variant="ghost" size="sm" onClick={() => handleUndo(action.id)} className="flex items-center gap-1">
                <Undo2 className="h-4 w-4" /> Undo
              </Button>
            ) : null}
          </div>
        )
      })}
    </div>
  )

  return (
    <Card className="mx-auto w-full max-w-4xl border border-slate-200 shadow-xl transition-all hover:shadow-2xl dark:border-slate-700 dark:bg-slate-900">
      <CardHeader className="border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <CardTitle className="text-xl font-semibold text-slate-900 dark:text-slate-100">{layout.header.title}</CardTitle>
              <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${signalColor}`}>
                {layout.header.signalBadge.toUpperCase()}
              </span>
            </div>
            <p className="mt-1 text-sm text-slate-500">
              Updated {formatDate(layout.header.timestamp)} • Confidence {layout.header.confidenceScore}%
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleToggleExpand}>
              {cardState.isExpanded ? 'Collapse' : 'Expand'}
            </Button>
            <Button variant="outline" size="sm" onClick={toggleSandbox}>
              Sandbox: {cardState.sandboxMode ? 'On' : 'Off'}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6 p-6">
        <Collapsible open={cardState.isExpanded}>
          <div className="space-y-4">
            <div>
              <CollapsibleTrigger asChild>
                <button className="flex w-full items-center justify-between rounded-lg bg-slate-50 px-4 py-3 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">
                  <span>{layout.content.intentSummary}</span>
                  <span className="text-xs uppercase text-slate-500">TL;DR</span>
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <p className="mt-2 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
                  {layout.content.tldr}
                </p>
              </CollapsibleContent>
            </div>

            {renderChart()}

            {mermaidBlock ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Process Flow</h4>
                  {showMermaidToggle ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        setCardState((state) => ({ ...state, showingMermaidPreview: !state.showingMermaidPreview }))
                      }
                    >
                      {cardState.showingMermaidPreview ? 'Show Code' : 'Preview Diagram'}
                    </Button>
                  ) : null}
                </div>
                {mermaidViewMode === 'split' ? (
                  <div className="grid gap-4 lg:grid-cols-2">
                    <MermaidPreview config={mermaidBlock} previewMode={true} />
                    <Textarea
                      value={mermaidBlock.syntax}
                      readOnly={!mermaidEditable}
                      className="min-h-[160px]"
                      data-testid="mermaid-code"
                    />
                  </div>
                ) : mermaidPreviewVisible ? (
                  <MermaidPreview config={mermaidBlock} previewMode={mermaidPreviewVisible} />
                ) : mermaidCodeVisible ? (
                  <Textarea
                    value={mermaidBlock.syntax}
                    readOnly={!mermaidEditable}
                    className="min-h-[160px]"
                    data-testid="mermaid-code"
                  />
                ) : null}
              </div>
            ) : null}

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">CLI Plan</h4>
                <Button size="sm" variant="ghost" onClick={() => setCardState((state) => ({ ...state, editingCLI: !state.editingCLI }))}>
                  {cardState.editingCLI ? 'Lock Command' : 'Edit Command'}
                </Button>
              </div>
              {cardState.editingCLI ? (
                <Textarea value={cliCommand} onChange={(event) => updateCliCommand(event.target.value)} className="min-h-[120px]" />
              ) : (
                <pre className="rounded-lg border border-slate-200 bg-slate-900 p-4 text-xs text-slate-100 shadow-inner dark:border-slate-700">
                  <code>{cliCommand}</code>
                </pre>
              )}
              {cliError ? <p className="text-sm text-rose-600">{cliError}</p> : null}
              <p className="text-xs text-slate-500">
                Timeout {layout.content.cliSnippet.execution.timeout / 1000}s • Confirmation{' '}
                {layout.content.cliSnippet.execution.requiresConfirmation ? 'Required' : 'Optional'}
              </p>
            </div>

            {renderAssessment()}

            {renderSafetyChecks()}
          </div>
        </Collapsible>

        <div className="space-y-4">
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Primary Actions</h4>
            {renderActions(layout.actions.primary, 'primary')}
          </div>
          {layout.actions.secondary?.length ? (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Secondary Actions</h4>
              {renderActions(layout.actions.secondary, 'secondary')}
            </div>
          ) : null}
        </div>

        <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Audit Metadata</h4>
          <div className="grid gap-2 text-sm text-slate-600 dark:text-slate-300">
            <p>
              Created by <strong>{layout.actions.audit.createdBy}</strong> at {formatDate(layout.actions.audit.createdAt)}
            </p>
            <p>
              Last updated by <strong>{layout.actions.audit.lastModifiedBy}</strong> at {formatDate(layout.actions.audit.lastModifiedAt)}
            </p>
            <div className="space-y-1">
              <p className="text-xs uppercase text-slate-500">Approvals</p>
              {layout.actions.audit.approvals.map((approval) => (
                <div key={`${approval.userId}-${approval.timestamp.toISOString()}`} className="flex items-center justify-between text-sm">
                  <span>{approval.userId}</span>
                  <Badge variant={approval.status === 'approved' ? 'default' : approval.status === 'pending' ? 'secondary' : 'destructive'}>
                    {approval.status}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Confirmation Flow</h4>
          <ol className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
            {layout.confirmationFlow?.steps.map((step, index) => (
              <li key={`${step.type}-${index}`} className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{step.title}</span>
                  <Badge variant={index === layout.confirmationFlow?.currentStep ? 'default' : 'outline'}>
                    Step {index + 1}: {step.type}
                  </Badge>
                </div>
                <p className="mt-1 text-xs text-slate-500">{step.description}</p>
                <ul className="mt-2 space-y-1 text-xs">
                  {step.checks.map((check) => (
                    <li key={check.name} className="flex items-center gap-2">
                      {check.status === 'passed' ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> : check.status === 'failed' ? <ShieldAlert className="h-3.5 w-3.5 text-rose-500" /> : <Clock className="h-3.5 w-3.5 text-amber-500" />}
                      <span>{check.name}</span>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
        </div>

        {layout.undo ? (
          <div className="grid gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm dark:border-amber-500/50 dark:bg-amber-950/40">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              <h4 className="text-sm font-semibold text-amber-700">Undo & Rollback Plan</h4>
            </div>
            <p className="text-xs text-amber-700">
              Undo available until {formatDate(layout.undo.undoDeadline)} • Auto rollback {layout.undo.autoRollback ? 'enabled' : 'disabled'}
            </p>
            <ul className="space-y-1 text-sm text-amber-800">
              {layout.undo.undoSteps.map((step, index) => (
                <li key={`${step.description}-${index}`}>
                  <strong>{step.description}</strong>
                  <span className="ml-2 text-xs">({step.command})</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Provenance & Related Items</h4>
          <p className="text-xs text-slate-500">Audit ID: {layout.footer.auditId}</p>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Source: {layout.footer.provenance.dataSource} ({layout.footer.provenance.modelVersion}) • Confidence{' '}
            {layout.footer.provenance.confidence}% • Freshness {formatDate(layout.footer.provenance.freshness)}
          </p>
          <ul className="space-y-1 text-sm text-blue-600 dark:text-blue-400">
            {layout.footer.relatedItems.map((item) => (
              <li key={item.url}>
                <a href={item.url} target="_blank" rel="noreferrer" className="underline-offset-2 hover:underline">
                  {item.label}
                </a>
                <span className="ml-2 text-xs uppercase text-slate-400">{item.type}</span>
              </li>
            ))}
          </ul>
        </div>

        {metrics ? (
          <div className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-100">Usage Analytics</h4>
            <div className="grid grid-cols-2 gap-3 text-sm text-slate-600 dark:text-slate-300">
              <span>Views: {metrics.usage.views}</span>
              <span>Executions: {metrics.usage.executions}</span>
              <span>Rollbacks: {metrics.usage.rollbacks}</span>
              <span>Shares: {metrics.usage.shares}</span>
              <span>Render Time: {metrics.renderTime}ms</span>
              <span>Interaction Time: {metrics.interactionTime}ms</span>
            </div>
          </div>
        ) : null}
      </CardContent>

      <Dialog open={Boolean(cardState.confirmationModal)} onOpenChange={(open) => !open && setCardState((state) => ({ ...state, confirmationModal: null }))}>
        {cardState.confirmationModal ? (
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirm Action</DialogTitle>
              <DialogDescription>
                Risk Level: {cardState.confirmationModal.config.riskLevel} • Estimated cost {cardState.confirmationModal.config.estimatedCost}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 text-sm text-slate-600">
              <p>This action will perform the following:</p>
              <ul className="list-disc space-y-1 pl-5">
                {cardState.confirmationModal.config.impactPreview.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <p>Undo plan: {cardState.confirmationModal.config.undoPlan}</p>
              {cardState.confirmationModal.config.requiredApprovals?.length ? (
                <p>Required approvals: {cardState.confirmationModal.config.requiredApprovals.join(', ')}</p>
              ) : null}
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={cancelAction}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={confirmAction}>
                Confirm
              </Button>
            </DialogFooter>
          </DialogContent>
        ) : null}
      </Dialog>
    </Card>
  )
}

