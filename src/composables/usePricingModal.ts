import { ref, readonly } from 'vue'
import { useAuth } from './useAuth'
import { useSubscription } from './useSubscription'

// Singleton state - shared across all instances
const isOpen = ref(false)
const triggerSource = ref('')

export function usePricingModal() {
  const { user } = useAuth()
  const { hasAccess } = useSubscription(user)

  function openModal(source: string) {
    triggerSource.value = source
    isOpen.value = true
  }

  function closeModal() {
    isOpen.value = false
    triggerSource.value = ''
  }

  /**
   * Wrapper function to check subscription access before executing an action.
   * If user has access, executes the action immediately.
   * If not, shows the pricing modal instead.
   *
   * @param action - The function to execute if user has access
   * @param source - Identifier for analytics tracking (e.g., 'feature-name')
   * @returns The result of the action if executed, void if modal is shown
   */
  function withAccess<T>(
    action: () => T | Promise<T>,
    source: string
  ): T | Promise<T> | void {
    if (hasAccess.value) {
      return action()
    } else {
      openModal(source)
    }
  }

  return {
    isOpen: readonly(isOpen),
    triggerSource: readonly(triggerSource),
    openModal,
    closeModal,
    withAccess,
  }
}
