import { getCurrentInstance, onBeforeUnmount, ref } from 'vue'

/**
 * Poll a task fetch function until terminal status or cancel.
 * Domain pages should pass their own adapter function.
 */
export function usePollingTask(fetchTask, { intervalMs = 1500, terminal = ['passed', 'failed', 'error', 'cancelled'] } = {}) {
  const task = ref(null)
  const error = ref('')
  const polling = ref(false)
  let timer = null

  async function pollOnce(taskId) {
    task.value = await fetchTask(taskId)
    return task.value
  }

  async function start(taskId) {
    stop()
    polling.value = true
    error.value = ''
    try {
      const current = await pollOnce(taskId)
      if (terminal.includes(current?.status)) {
        stop()
        return
      }
      timer = setInterval(async () => {
        try {
          const next = await pollOnce(taskId)
          if (terminal.includes(next?.status)) stop()
        } catch (err) {
          error.value = err.message || String(err)
          stop()
        }
      }, intervalMs)
    } catch (err) {
      error.value = err.message || String(err)
      stop()
    }
  }

  function stop() {
    polling.value = false
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  if (getCurrentInstance()) {
    onBeforeUnmount(stop)
  }

  return { task, error, polling, start, stop }
}
