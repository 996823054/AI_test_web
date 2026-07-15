import { describe, expect, it, vi } from 'vitest'
import { usePollingTask } from './usePollingTask'

describe('usePollingTask', () => {
  it('stops polling on terminal status', async () => {
    vi.useFakeTimers()
    const fetchTask = vi
      .fn()
      .mockResolvedValueOnce({ status: 'running' })
      .mockResolvedValueOnce({ status: 'passed' })

    const { start, polling, task, stop } = usePollingTask(fetchTask, { intervalMs: 100 })
    await start('task-1')
    expect(polling.value).toBe(true)
    await vi.advanceTimersByTimeAsync(100)
    expect(task.value.status).toBe('passed')
    expect(polling.value).toBe(false)
    stop()
    vi.useRealTimers()
  })
})
