// useChat — manages chat state, session, and API calls
import { useState, useCallback, useRef } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { sendChat } from '../api/client'
import type { ChatMessage, ChatResponse, Filters } from '../types'

export interface UseChatReturn {
  messages: ChatMessage[]
  lastResponse: ChatResponse | null
  isLoading: boolean
  error: string | null
  sessionId: string
  sendMessage: (query: string, filters: Filters) => Promise<void>
  clearHistory: () => void
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sessionIdRef = useRef<string>(uuidv4())

  const sendMessage = useCallback(async (query: string, filters: Filters) => {
    if (!query.trim()) return
    setError(null)
    setIsLoading(true)

    const userMsg: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])

    const historyForApi = messages.map(m => ({ role: m.role, content: m.content }))

    try {
      const response = await sendChat({
        query,
        sessionId: sessionIdRef.current,
        history: historyForApi,
        filters,
      })

      const assistantMsg: ChatMessage = {
        role: 'assistant',
        content: response.answerMd,
        timestamp: new Date().toISOString(),
      }
      setMessages(prev => [...prev, assistantMsg])
      setLastResponse(response)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Request failed'
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }, [messages])

  const clearHistory = useCallback(() => {
    setMessages([])
    setLastResponse(null)
    setError(null)
    sessionIdRef.current = uuidv4()
  }, [])

  return {
    messages,
    lastResponse,
    isLoading,
    error,
    sessionId: sessionIdRef.current,
    sendMessage,
    clearHistory,
  }
}
