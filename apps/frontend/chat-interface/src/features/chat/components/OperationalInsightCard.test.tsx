import { jest } from '@jest/globals'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'

import { createDemoCardLayout } from '../card-system/defaultCardFactory'
import { OperationalInsightCard } from './OperationalInsightCard'

describe('OperationalInsightCard', () => {
  test('blocks execute actions until CLI validation passes', async () => {
    const layout = createDemoCardLayout('validation-test')
    const executeMock = jest.fn().mockResolvedValue({
      message: 'ok',
      startedAt: new Date(),
      completedAt: new Date(),
    })

    render(<OperationalInsightCard layout={layout} onExecuteCli={executeMock} />)

    fireEvent.click(screen.getByRole('button', { name: /edit command/i }))
    const cliTextarea = screen.getByDisplayValue(layout.content.cliSnippet.command)

    fireEvent.change(cliTextarea, { target: { value: 'rm -rf /' } })

    expect(await screen.findByText(/Command blocked by safety rule/i)).toBeInTheDocument()

    const executeButton = screen.getByRole('button', { name: /execute in sandbox/i })
    expect(executeButton).toBeDisabled()

    fireEvent.click(executeButton)
    expect(executeMock).not.toHaveBeenCalled()

    fireEvent.change(cliTextarea, {
      target: { value: 'ansible-playbook playbooks/failover.yml --limit=staging' },
    })

    await waitFor(() => expect(screen.queryByText(/Command blocked by safety rule/i)).not.toBeInTheDocument())
    await waitFor(() => expect(screen.getByRole('button', { name: /execute in sandbox/i })).not.toBeDisabled())

    fireEvent.click(screen.getByRole('button', { name: /execute in sandbox/i }))
    const confirmButton = await screen.findByRole('button', { name: /confirm/i })
    fireEvent.click(confirmButton)

    await waitFor(() => expect(executeMock).toHaveBeenCalled())
  })
})
