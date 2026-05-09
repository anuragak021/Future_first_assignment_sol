// apiClient — typed wrappers for the backend API
import axios from 'axios'
import type { ChatRequest, ChatResponse, ToolTraceEntry } from '../types'

const http = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
})

export const sendChat = async (request: ChatRequest): Promise<ChatResponse> => {
  const { data } = await http.post<ChatResponse>('/chat', request)
  return data
}

export const fetchTrace = async (sessionId: string): Promise<ToolTraceEntry[]> => {
  const { data } = await http.get<ToolTraceEntry[]>(`/trace/${sessionId}`)
  return data
}

export const checkHealth = async (): Promise<boolean> => {
  try {
    await http.get('/health')
    return true
  } catch {
    return false
  }
}
