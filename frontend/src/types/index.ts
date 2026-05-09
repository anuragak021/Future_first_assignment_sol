// Shared TypeScript types mirroring the backend response schemas

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ChartSpec {
  $schema: string
  title: string
  mark: string
  data: { values: Record<string, unknown>[] }
  encoding: Record<string, unknown>
  width?: number
  height?: number
}

export interface ToolTraceEntry {
  agent: string
  [key: string]: unknown
}

export interface ChatResponse {
  sessionId: string
  answerMd: string
  chartSpecs: ChartSpec[]
  toolTrace: ToolTraceEntry[]
  verdict: 'PASS' | 'SOFT_FAIL' | 'HARD_FAIL' | 'UNKNOWN'
  faithfulnessScore: number
  uncertaintyNotes?: string
}

export interface ChatRequest {
  query: string
  sessionId: string
  history: { role: string; content: string }[]
  filters: Filters
}

export interface Filters {
  year?: number
  region?: string
  genre?: string
}
