import { useState, useRef, KeyboardEvent } from 'react'
import { Send } from 'lucide-react'

const QUICK_QUESTIONS = [
  'Which titles performed best in 2025?',
  'Why is Stellar Run trending recently?',
  'Compare Dark Orbit vs Last Kingdom',
  'Which city had the strongest engagement last month?',
  'What explains weak comedy performance?',
  'What recommendations for leadership?',
]

interface Props {
  onSend: (query: string) => void
  isLoading: boolean
}

export function InputBar({ onSend, isLoading }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (!value.trim() || isLoading) return
    onSend(value.trim())
    setValue('')
    textareaRef.current?.focus()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="shrink-0 border-t border-gray-200 dark:border-gray-700/60 bg-white dark:bg-gray-900 px-3 sm:px-4 pt-3 pb-3 sm:pb-4 space-y-2.5">
      {/* Quick questions — horizontal scroll on mobile */}
      <div className="flex gap-2 overflow-x-auto pb-0.5 scrollbar-thin">
        {QUICK_QUESTIONS.map(q => (
          <button
            key={q}
            onClick={() => { setValue(q); textareaRef.current?.focus() }}
            className="shrink-0 text-xs px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-colors whitespace-nowrap"
          >
            {q.length > 36 ? q.slice(0, 36) + '…' : q}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="flex gap-2 items-end">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a business question… (Enter to send)"
          rows={2}
          className={[
            'flex-1 resize-none rounded-xl border px-3.5 py-2.5 text-sm leading-relaxed',
            'bg-white dark:bg-gray-800',
            'text-gray-900 dark:text-gray-100',
            'placeholder-gray-400 dark:placeholder-gray-500',
            'border-gray-300 dark:border-gray-600',
            'focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-transparent',
            'disabled:opacity-50',
            'scrollbar-thin',
          ].join(' ')}
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !value.trim()}
          className={[
            'p-3 rounded-xl transition-all shrink-0',
            'bg-indigo-600 dark:bg-indigo-500 text-white',
            'hover:bg-indigo-700 dark:hover:bg-indigo-600',
            'disabled:opacity-40 disabled:cursor-not-allowed',
            'active:scale-95',
          ].join(' ')}
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
