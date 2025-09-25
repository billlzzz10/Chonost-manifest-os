import { z } from 'zod'

export const signalTypeSchema = z.enum(['info', 'success', 'warning', 'critical', 'neutral'])
export type SignalType = z.infer<typeof signalTypeSchema>

export const dateRangeSchema = z.object({
  start: z.coerce.date(),
  end: z.coerce.date(),
})
export type DateRange = z.infer<typeof dateRangeSchema>

export const chartDataPointSchema = z.object({
  timestamp: z.coerce.date(),
  value: z.number(),
  label: z.string().optional(),
})
export type ChartDataPoint = z.infer<typeof chartDataPointSchema>

export const chartAnnotationSchema = z.object({
  id: z.string(),
  label: z.string(),
  color: z.string().optional(),
  description: z.string().optional(),
  position: z.union([z.coerce.date(), z.number(), z.string()]),
})
export type ChartAnnotation = z.infer<typeof chartAnnotationSchema>

export const chartConfigSchema = z.object({
  type: z.enum(['line', 'bar', 'area', 'scatter']),
  data: z.array(chartDataPointSchema).min(1),
  timeRange: dateRangeSchema,
  interactive: z.object({
    tooltip: z.boolean().default(true),
    zoom: z.boolean().default(false),
    crosshair: z.boolean().default(false),
  }),
  annotations: z.array(chartAnnotationSchema).optional(),
})
export type ChartConfig = z.infer<typeof chartConfigSchema>

export const mermaidConfigSchema = z.object({
  syntax: z.string(),
  viewMode: z.enum(['code', 'preview', 'split']).default('code'),
  editable: z.boolean().default(false),
  autoRender: z.boolean().default(false),
  errorHandling: z.object({
    showErrors: z.boolean().default(true),
    fallbackToCode: z.boolean().default(true),
  }).default({ showErrors: true, fallbackToCode: true }),
})
export type MermaidConfig = z.infer<typeof mermaidConfigSchema>

export const cliValidationSchema = z.object({
  schema: z.any().optional(),
  allowedCommands: z.array(z.string()).optional(),
  blockedPatterns: z.array(z.instanceof(RegExp)).optional(),
})

export const cliExecutionSchema = z.object({
  sandboxed: z.boolean().default(true),
  timeout: z.number().min(100).max(600000).default(60000),
  requiresConfirmation: z.boolean().default(false),
})

export const cliConfigSchema = z.object({
  command: z.string(),
  editable: z.boolean().default(false),
  syntax: z.enum(['bash', 'powershell', 'python', 'javascript']).default('bash'),
  validation: cliValidationSchema.default({}),
  execution: cliExecutionSchema.default({ sandboxed: true, timeout: 60000, requiresConfirmation: false }),
})
export type CLIConfig = z.infer<typeof cliConfigSchema>

export const scenarioOutcomesSchema = z.object({
  bestCase: z.string(),
  expectedCase: z.string(),
  worstCase: z.string(),
  probability: z
    .object({
      best: z.number().min(0).max(1).optional(),
      expected: z.number().min(0).max(1).optional(),
      worst: z.number().min(0).max(1).optional(),
    })
    .optional(),
})
export type ScenarioOutcomes = z.infer<typeof scenarioOutcomesSchema>

export const resourceEstimateSchema = z.object({
  time: z.string(),
  people: z.number().min(0).default(0),
  budget: z.string(),
  complexity: z.enum(['Low', 'Medium', 'High']).default('Medium'),
  environments: z.array(z.string()).default([]),
})
export type ResourceEstimate = z.infer<typeof resourceEstimateSchema>

export const confidenceMetricsSchema = z.object({
  dataQuality: z.number().min(0).max(100),
  methodology: z.number().min(0).max(100),
  humanReview: z.number().min(0).max(100),
  historicalSuccess: z.number().min(0).max(100),
})
export type ConfidenceMetrics = z.infer<typeof confidenceMetricsSchema>

export const confirmationConfigSchema = z.object({
  required: z.boolean(),
  riskLevel: z.enum(['Low', 'Medium', 'High']),
  impactPreview: z.array(z.string()),
  undoPlan: z.string(),
  estimatedCost: z.string(),
  requiredApprovals: z.array(z.string()).optional(),
})
export type ConfirmationConfig = z.infer<typeof confirmationConfigSchema>

export const safetyChecksSchema = z.object({
  policyCompliance: z.boolean(),
  dataPrivacy: z.boolean(),
  securityRisk: z.enum(['Low', 'Medium', 'High']),
  destructivePotential: z.boolean(),
  requiresSandbox: z.boolean(),
})
export type SafetyChecks = z.infer<typeof safetyChecksSchema>

export const auditMetadataSchema = z.object({
  createdBy: z.string(),
  createdAt: z.coerce.date(),
  lastModifiedBy: z.string(),
  lastModifiedAt: z.coerce.date(),
  approvals: z.array(z.object({
    userId: z.string(),
    status: z.enum(['approved', 'pending', 'rejected']),
    timestamp: z.coerce.date(),
  })),
})
export type AuditMetadata = z.infer<typeof auditMetadataSchema>

export const actionButtonSchema = z.object({
  id: z.string(),
  label: z.string(),
  type: z.enum(['preview', 'execute', 'rollback']),
  intent: z.enum(['default', 'primary', 'danger']).default('default'),
  disabled: z.boolean().optional(),
  confirmation: confirmationConfigSchema.optional(),
  safety: safetyChecksSchema.optional(),
  tooltip: z.string().optional(),
  undoWindowSeconds: z.number().int().positive().optional(),
})
export type ActionButton = z.infer<typeof actionButtonSchema>

export const provenanceDataSchema = z.object({
  dataSource: z.string(),
  modelVersion: z.string(),
  confidence: z.number().min(0).max(100),
  freshness: z.coerce.date(),
  parentEvents: z.array(z.string()).default([]),
  signature: z.string().optional(),
})
export type ProvenanceData = z.infer<typeof provenanceDataSchema>

export const relatedLinkSchema = z.object({
  label: z.string(),
  url: z.string().url(),
  type: z.enum(['doc', 'runbook', 'dashboard', 'ticket', 'other']).default('other'),
})
export type RelatedLink = z.infer<typeof relatedLinkSchema>

export const confirmationStateSchema = z.object({
  actionId: z.string(),
  config: confirmationConfigSchema,
  open: z.boolean().default(true),
})
export type ConfirmationState = z.infer<typeof confirmationStateSchema>

export const executionResultSchema = z.object({
  message: z.string(),
  output: z.array(z.string()).optional(),
  errors: z.array(z.string()).optional(),
  startedAt: z.coerce.date(),
  completedAt: z.coerce.date(),
  cost: z.object({
    usd: z.number().nonnegative().optional(),
    credits: z.number().nonnegative().optional(),
  }).optional(),
})
export type ExecutionResult = z.infer<typeof executionResultSchema>

export const actionStateSchema = z.object({
  type: z.enum(['preview', 'execute', 'rollback']),
  status: z.enum(['idle', 'running', 'success', 'error']).default('idle'),
  result: executionResultSchema.optional(),
  canUndo: z.boolean().default(false),
  undoDeadline: z.coerce.date().optional(),
})
export type ActionState = z.infer<typeof actionStateSchema>

export const cardStateSchema = z.object({
  isExpanded: z.boolean().default(true),
  editingCLI: z.boolean().default(false),
  showingMermaidPreview: z.boolean().default(false),
  confirmationModal: confirmationStateSchema.nullable().default(null),
  sandboxMode: z.boolean().default(true),
  undoTimer: z.number().int().nonnegative().nullable().default(null),
})
export type CardState = z.infer<typeof cardStateSchema>

export const permissionConfigSchema = z.object({
  canView: z.boolean().default(true),
  canEdit: z.boolean().default(false),
  canExecute: z.boolean().default(false),
  canApprove: z.boolean().default(false),
  requiresApproval: z.boolean().default(false),
  approvers: z.array(z.string()).optional(),
  restrictions: z
    .object({
      timeWindow: dateRangeSchema.optional(),
      ipWhitelist: z.array(z.string()).optional(),
      mfaRequired: z.boolean().optional(),
    })
    .default({}),
})
export type PermissionConfig = z.infer<typeof permissionConfigSchema>

export const confirmationStepSchema = z.object({
  type: z.enum(['preview', 'validate', 'approve', 'execute']),
  title: z.string(),
  description: z.string(),
  checks: z.array(z.object({
    name: z.string(),
    status: z.enum(['pending', 'passed', 'failed']),
    detail: z.string().optional(),
  })),
  canSkip: z.boolean().default(false),
  timeout: z.number().int().positive().optional(),
})

export const confirmationFlowSchema = z.object({
  steps: z.array(confirmationStepSchema),
  currentStep: z.number().int().nonnegative().default(0),
})
export type ConfirmationFlow = z.infer<typeof confirmationFlowSchema>

export const undoStepSchema = z.object({
  description: z.string(),
  command: z.string(),
  estimated_time: z.number().positive(),
  risk: z.enum(['Low', 'Medium', 'High']).default('Low'),
})

export const undoSystemSchema = z.object({
  isUndoable: z.boolean(),
  undoDeadline: z.coerce.date(),
  undoSteps: z.array(undoStepSchema),
  autoRollback: z.boolean().default(false),
})
export type UndoSystem = z.infer<typeof undoSystemSchema>

export const auditEventSchema = z.object({
  eventId: z.string(),
  causalId: z.string(),
  userId: z.string(),
  timestamp: z.coerce.date(),
  action: z.enum(['create', 'edit', 'execute', 'rollback']),
  before: z.unknown().optional(),
  after: z.unknown().optional(),
  metadata: z.object({
    cardId: z.string(),
    sessionId: z.string(),
    ipAddress: z.string(),
    userAgent: z.string(),
  }),
})
export type AuditEvent = z.infer<typeof auditEventSchema>

export const provenanceChainSchema = z.object({
  dataSource: z.string(),
  modelVersion: z.string(),
  confidence: z.number().min(0).max(100),
  freshness: z.coerce.date(),
  parentEvents: z.array(z.string()).default([]),
  signature: z.string().optional(),
})
export type ProvenanceChain = z.infer<typeof provenanceChainSchema>

export const costBreakdownSchema = z.object({
  llm_inference: z.number().nonnegative(),
  data_processing: z.number().nonnegative(),
  storage: z.number().nonnegative(),
  network: z.number().nonnegative(),
})

export const costEstimateSchema = z.object({
  apiCalls: z.number().nonnegative(),
  tokenUsage: z.number().nonnegative(),
  computeTime: z.number().nonnegative(),
  storageUsed: z.number().nonnegative(),
  estimated: z.object({
    usd: z.number().nonnegative(),
    credits: z.number().nonnegative(),
    latency: z.number().nonnegative(),
  }),
  breakdown: costBreakdownSchema,
})
export type CostEstimate = z.infer<typeof costEstimateSchema>

export const cardMetricsSchema = z.object({
  renderTime: z.number().nonnegative(),
  interactionTime: z.number().nonnegative(),
  executionTime: z.number().nonnegative().optional(),
  errorRate: z.number().min(0).max(100),
  userSatisfaction: z.number().min(1).max(5).optional(),
  usage: z.object({
    views: z.number().nonnegative(),
    executions: z.number().nonnegative(),
    rollbacks: z.number().nonnegative(),
    shares: z.number().nonnegative(),
  }),
})
export type CardMetrics = z.infer<typeof cardMetricsSchema>

export const permissionAwareActionSchema = actionButtonSchema.extend({
  permissions: permissionConfigSchema.optional(),
})

export const cardLayoutSchema = z.object({
  id: z.string(),
  header: z.object({
    title: z.string(),
    signalBadge: signalTypeSchema,
    timestamp: z.coerce.date(),
    confidenceScore: z.number().min(0).max(100),
  }),
  content: z.object({
    intentSummary: z.string(),
    tldr: z.string(),
    mainChart: chartConfigSchema.optional(),
    mermaidBlock: mermaidConfigSchema.optional(),
    cliSnippet: cliConfigSchema,
  }),
  assessment: z.object({
    riskRating: z.enum(['Low', 'Medium', 'High']),
    impactEstimate: scenarioOutcomesSchema,
    costEstimate: costEstimateSchema,
    confidenceBreakdown: confidenceMetricsSchema,
  }),
  actions: z.object({
    primary: z.array(permissionAwareActionSchema),
    secondary: z.array(permissionAwareActionSchema).default([]),
    audit: auditMetadataSchema,
  }),
  footer: z.object({
    provenance: provenanceDataSchema,
    auditId: z.string(),
    relatedItems: z.array(relatedLinkSchema),
  }),
  permissions: permissionConfigSchema.optional(),
  confirmationFlow: confirmationFlowSchema.optional(),
  undo: undoSystemSchema.optional(),
  safety: safetyChecksSchema.optional(),
  metrics: cardMetricsSchema.optional(),
})
export type CardLayout = z.infer<typeof cardLayoutSchema>

export function validateCardLayout(layout: CardLayout): CardLayout
export function validateCardLayout(layout: unknown): CardLayout
export function validateCardLayout(layout: unknown): CardLayout {
  return cardLayoutSchema.parse(layout)
}

