import { render, screen } from '@testing-library/react'
import type { CardLayout } from '../../card-system/cardSchemas'
import { OperationalInsightCard } from '../OperationalInsightCard'

jest.mock('mermaid', () => ({
  initialize: jest.fn(),
  render: jest.fn().mockResolvedValue({ svg: '<svg><g></g></svg>' }),
}))

const createLayout = (
  mermaidOverrides: Partial<NonNullable<CardLayout['content']['mermaidBlock']>> = {},
): CardLayout => {
  const timestamp = new Date('2024-01-01T00:00:00Z')

  return {
    id: 'test-card',
    header: {
      title: 'Test Card',
      signalBadge: 'info',
      timestamp,
      confidenceScore: 85,
    },
    content: {
      intentSummary: 'Summarised intent',
      tldr: 'A concise TLDR of the operational insight.',
      mainChart: undefined,
      mermaidBlock: {
        syntax: 'graph TD; A-->B;',
        viewMode: 'code',
        editable: true,
        autoRender: false,
        errorHandling: { showErrors: true, fallbackToCode: true },
        ...mermaidOverrides,
      },
      cliSnippet: {
        command: 'echo "hello"',
        editable: false,
        syntax: 'bash',
        validation: {},
        execution: { sandboxed: true, timeout: 60000, requiresConfirmation: false },
      },
    },
    assessment: {
      riskRating: 'Low',
      impactEstimate: {
        bestCase: 'Best case outcome',
        expectedCase: 'Expected outcome',
        worstCase: 'Worst case outcome',
        probability: undefined,
      },
      costEstimate: {
        apiCalls: 1,
        tokenUsage: 1,
        computeTime: 1,
        storageUsed: 1,
        estimated: { usd: 100, credits: 10, latency: 500 },
        breakdown: {
          llm_inference: 10,
          data_processing: 5,
          storage: 2,
          network: 3,
        },
      },
      confidenceBreakdown: {
        dataQuality: 80,
        methodology: 75,
        humanReview: 90,
        historicalSuccess: 70,
      },
    },
    actions: {
      primary: [
        {
          id: 'action-1',
          label: 'Run Action',
          type: 'execute',
          intent: 'default',
        },
      ],
      secondary: [],
      audit: {
        createdBy: 'tester',
        createdAt: timestamp,
        lastModifiedBy: 'tester',
        lastModifiedAt: timestamp,
        approvals: [],
      },
    },
    footer: {
      provenance: {
        dataSource: 'synthetic',
        modelVersion: 'v1',
        confidence: 80,
        freshness: timestamp,
        parentEvents: [],
        signature: undefined,
      },
      auditId: 'audit-123',
      relatedItems: [],
    },
    permissions: undefined,
    confirmationFlow: undefined,
    undo: undefined,
    safety: {
      policyCompliance: true,
      dataPrivacy: true,
      securityRisk: 'Low',
      destructivePotential: false,
      requiresSandbox: false,
    },
    metrics: {
      renderTime: 10,
      interactionTime: 5,
      executionTime: undefined,
      errorRate: 0,
      usage: {
        views: 1,
        executions: 0,
        rollbacks: 0,
        shares: 0,
      },
    },
  }
}

describe('OperationalInsightCard mermaid view modes', () => {
  it('renders the preview pane by default when viewMode is preview', () => {
    render(<OperationalInsightCard layout={createLayout({ viewMode: 'preview' })} />)

    expect(screen.getByTestId('mermaid-preview')).toBeInTheDocument()
    expect(screen.queryByTestId('mermaid-code')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /show code/i })).toBeInTheDocument()
  })

  it('renders the code editor by default when viewMode is code', () => {
    render(<OperationalInsightCard layout={createLayout({ viewMode: 'code' })} />)

    expect(screen.getByTestId('mermaid-code')).toBeInTheDocument()
    expect(screen.queryByTestId('mermaid-preview')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /preview diagram/i })).toBeInTheDocument()
  })

  it('renders both panes without a toggle when viewMode is split', () => {
    render(<OperationalInsightCard layout={createLayout({ viewMode: 'split' })} />)

    expect(screen.getByTestId('mermaid-preview')).toBeInTheDocument()
    expect(screen.getByTestId('mermaid-code')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /preview diagram/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /show code/i })).not.toBeInTheDocument()
  })
})
