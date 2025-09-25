import { addMinutes, subMinutes } from 'date-fns'
import { validateCardLayout, type CardLayout } from './cardSchemas'

const now = () => new Date()

const randomId = (prefix: string, length = 6) => {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
  const bytes = Array.from({ length }, () => alphabet[Math.floor(Math.random() * alphabet.length)])
  return `${prefix}-${bytes.join('')}`
}

export function createDemoCardLayout(sessionId: string | number | null): CardLayout {
  const timestamp = now()
  const id = `card-${sessionId ?? 'preview'}`

  return validateCardLayout({
    id,
    header: {
      title: 'Operational Insight Summary',
      signalBadge: 'info',
      timestamp,
      confidenceScore: 86,
    },
    content: {
      intentSummary:
        'Summarizes the current chat intent, proposed remediation steps, and execution safeguards for infrastructure-level actions.',
      tldr:
        'Automate failover verification in staging with sandboxed CLI execution and full audit capture prior to production rollout.',
      mainChart: {
        type: 'line',
        data: [
          { timestamp: subMinutes(timestamp, 45), value: 25, label: 'baseline' },
          { timestamp: subMinutes(timestamp, 30), value: 40, label: 'load spike' },
          { timestamp: subMinutes(timestamp, 15), value: 36, label: 'mitigation' },
          { timestamp, value: 48, label: 'current' },
        ],
        timeRange: { start: subMinutes(timestamp, 60), end: timestamp },
        interactive: { tooltip: true, zoom: true, crosshair: true },
        annotations: [
          {
            id: randomId('anno'),
            label: 'Failover triggered',
            position: subMinutes(timestamp, 32),
            color: '#fb923c',
            description: 'Automatic health-check triggered failover sequence',
          },
        ],
      },
      mermaidBlock: {
        syntax: `flowchart TD\n  A[User Request] -->|LLM Intent Parser| B{Signal Triage}\n  B -->|Low Risk| C[Auto Approve]\n  B -->|Medium Risk| D[Sandbox Execution]\n  B -->|High Risk| E[Manual Review]\n  D --> F[Audit Log]\n  E --> G{Approval Needed}\n  G -->|Approved| D\n  G -->|Rejected| H[Abort]\n`,
        viewMode: 'split',
        editable: true,
        autoRender: true,
        errorHandling: { showErrors: true, fallbackToCode: true },
      },
      cliSnippet: {
        command: 'ansible-playbook playbooks/failover.yml --limit=staging --check',
        editable: true,
        syntax: 'bash',
        validation: {
          allowedCommands: ['ansible-playbook', 'kubectl', 'helm'],
          blockedPatterns: [/rm\s+-rf/, /shutdown/, /reboot/],
        },
        execution: {
          sandboxed: true,
          timeout: 120000,
          requiresConfirmation: true,
        },
      },
    },
    assessment: {
      riskRating: 'Medium',
      impactEstimate: {
        bestCase: 'Failover tested safely without impacting users.',
        expectedCase: 'Staging environment validated with automated health checks.',
        worstCase: 'Sandbox isolation breached leading to partial staging outage.',
        probability: { best: 0.2, expected: 0.65, worst: 0.15 },
      },
      costEstimate: {
        apiCalls: 18,
        tokenUsage: 2450,
        computeTime: 36,
        storageUsed: 12,
        estimated: { usd: 3.42, credits: 14, latency: 850 },
        breakdown: {
          llm_inference: 2.1,
          data_processing: 0.5,
          storage: 0.3,
          network: 0.52,
        },
      },
      confidenceBreakdown: {
        dataQuality: 82,
        methodology: 88,
        humanReview: 76,
        historicalSuccess: 91,
      },
    },
    actions: {
      primary: [
        {
          id: 'preview-plan',
          label: 'Preview Impact',
          type: 'preview',
          intent: 'primary',
          tooltip: 'Generate a sandboxed preview of the failover plan.',
        },
        {
          id: 'execute-sandbox',
          label: 'Execute in Sandbox',
          type: 'execute',
          intent: 'primary',
          confirmation: {
            required: true,
            riskLevel: 'Medium',
            impactPreview: [
              'Creates isolated environment snapshot',
              'Runs smoke tests with synthetic traffic',
            ],
            undoPlan: 'Rollback via ansible-playbook playbooks/failover.yml --limit=staging --tags=rollback',
            estimatedCost: '$3.42 estimated spend',
            requiredApprovals: ['ops-lead'],
          },
          safety: {
            policyCompliance: true,
            dataPrivacy: true,
            securityRisk: 'Low',
            destructivePotential: false,
            requiresSandbox: true,
          },
          undoWindowSeconds: 45,
        },
      ],
      secondary: [
        {
          id: 'request-approval',
          label: 'Request Approval',
          type: 'preview',
          intent: 'default',
          confirmation: {
            required: false,
            riskLevel: 'Low',
            impactPreview: ['Sends approval request to ops lead'],
            undoPlan: 'Cancel request before execution.',
            estimatedCost: 'No additional cost',
          },
        },
        {
          id: 'rollback',
          label: 'Schedule Rollback',
          type: 'rollback',
          intent: 'danger',
          confirmation: {
            required: true,
            riskLevel: 'High',
            impactPreview: ['Restores previous deployment state', 'Notifies incident channel'],
            undoPlan: 'Re-run execution step after verifying fix.',
            estimatedCost: '$1.15 estimated spend',
            requiredApprovals: ['ops-lead', 'compliance'],
          },
          safety: {
            policyCompliance: true,
            dataPrivacy: true,
            securityRisk: 'Medium',
            destructivePotential: true,
            requiresSandbox: false,
          },
          undoWindowSeconds: 120,
        },
      ],
      audit: {
        createdBy: 'system',
        createdAt: subMinutes(timestamp, 90),
        lastModifiedBy: 'ops-lead',
        lastModifiedAt: subMinutes(timestamp, 5),
        approvals: [
          { userId: 'ops-lead', status: 'approved', timestamp: subMinutes(timestamp, 4) },
          { userId: 'security', status: 'pending', timestamp: subMinutes(timestamp, 3) },
        ],
      },
    },
    footer: {
      provenance: {
        dataSource: 'observability-stack',
        modelVersion: 'kg-orchestrator@2.3.4',
        confidence: 92,
        freshness: subMinutes(timestamp, 2),
        parentEvents: ['evt-1200', 'evt-1188'],
        signature: '0xacf2ef',
      },
      auditId: randomId('audit'),
      relatedItems: [
        { label: 'Failover Runbook', url: 'https://intranet.example.com/runbooks/failover', type: 'runbook' },
        { label: 'Observability Dashboard', url: 'https://grafana.example.com/d/ops', type: 'dashboard' },
        { label: 'Incident Ticket #3492', url: 'https://tickets.example.com/3492', type: 'ticket' },
      ],
    },
    permissions: {
      canView: true,
      canEdit: true,
      canExecute: true,
      canApprove: false,
      requiresApproval: true,
      approvers: ['ops-lead', 'security'],
      restrictions: {
        mfaRequired: true,
      },
    },
    confirmationFlow: {
      steps: [
        {
          type: 'preview',
          title: 'Review Impact Summary',
          description: 'Confirm the projected outcomes and dependencies.',
          checks: [
            { name: 'Intent aligned with policy', status: 'passed' },
            { name: 'Dependencies satisfied', status: 'passed' },
          ],
          canSkip: false,
        },
        {
          type: 'validate',
          title: 'Validate Sandbox Environment',
          description: 'Ensure sandbox isolation and health-check coverage.',
          checks: [
            { name: 'Sandbox quota available', status: 'passed' },
            { name: 'Health checks configured', status: 'pending' },
          ],
          canSkip: false,
          timeout: 600,
        },
        {
          type: 'approve',
          title: 'Collect Required Approvals',
          description: 'Ops lead and security sign-off required.',
          checks: [
            { name: 'Ops lead approval', status: 'passed' },
            { name: 'Security approval', status: 'pending' },
          ],
          canSkip: false,
        },
        {
          type: 'execute',
          title: 'Execute Sandbox Run',
          description: 'Perform the validated failover in sandbox mode.',
          checks: [
            { name: 'Execution dry-run', status: 'pending' },
            { name: 'Audit log streaming', status: 'pending' },
          ],
          canSkip: false,
        },
      ],
      currentStep: 1,
    },
    undo: {
      isUndoable: true,
      undoDeadline: addMinutes(timestamp, 2),
      undoSteps: [
        {
          description: 'Restore database replication state',
          command: 'ansible-playbook playbooks/failover.yml --tags=rollback',
          estimated_time: 4,
          risk: 'Medium',
        },
        {
          description: 'Notify stakeholders and update incident ticket',
          command: 'python scripts/notify_incident.py --ticket=3492 --status=rollback',
          estimated_time: 2,
          risk: 'Low',
        },
      ],
      autoRollback: true,
    },
    safety: {
      policyCompliance: true,
      dataPrivacy: true,
      securityRisk: 'Medium',
      destructivePotential: false,
      requiresSandbox: true,
    },
    metrics: {
      renderTime: 120,
      interactionTime: 320,
      executionTime: 950,
      errorRate: 1,
      userSatisfaction: 5,
      usage: {
        views: 42,
        executions: 7,
        rollbacks: 1,
        shares: 3,
      },
    },
  })
}

