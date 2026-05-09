import { useEffect, useRef } from 'react'
import { Loader2, Trash2 } from 'lucide-react'
import { MessageBubble } from './MessageBubble'
import { InputBar } from './InputBar'
import type { ChatMessage, Filters } from '../../types'

interface Props {
  messages: ChatMessage[]
  isLoading: boolean
  error: string | null
  onSend: (query: string, filters: Filters) => void
  filters: Filters
  onClear: () => void
}

export function ChatPanel({ messages, isLoading, error, onSend, filters, onClear }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-950">
      {/* Chat header */}
      <div className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700/60 shrink-0">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold text-gray-800 dark:text-gray-100 text-sm">Chat</h2>
          {messages.length > 0 && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 font-medium">
              {Math.ceil(messages.length / 2)}
            </span>
          )}
        </div>
        {messages.length > 0 && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors"
          >
            <Trash2 size={13} />
            Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 sm:px-4 py-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-6 text-gray-400 dark:text-gray-600 select-none">
            <div className="w-14 h-14 rounded-2xl bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center mb-4">
              <span className="text-2xl">💬</span>
            </div>
            <p className="font-medium text-gray-600 dark:text-gray-400 mb-1">Ask anything about your data</p>
            <p className="text-sm">Try one of the quick questions below or type your own.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 shadow-sm">
              <Loader2 size={15} className="animate-spin text-indigo-500" />
              Analyzing data…
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3 text-sm text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <InputBar onSend={q => onSend(q, filters)} isLoading={isLoading} />
    </div>
  )
}
