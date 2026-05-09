import { useState } from 'react'
import { Moon, Sun, MessageSquare, BarChart2 } from 'lucide-react'
import clsx from 'clsx'
import { ChatPanel } from './components/Chat/ChatPanel'
import { FilterPanel } from './components/Filters/FilterPanel'
import { InsightsPanel } from './components/Insights/InsightsPanel'
import { ChartPanel } from './components/Charts/ChartPanel'
import { ToolTrace } from './components/ToolTrace/ToolTrace'
import { useChat } from './hooks/useChat'
import { useThemeContext } from './context/ThemeContext'
import type { Filters } from './types'

export default function App() {
  const [filters, setFilters] = useState<Filters>({})
  const [mobileTab, setMobileTab] = useState<'chat' | 'insights'>('chat')
  const { messages, lastResponse, isLoading, error, sendMessage, clearHistory } = useChat()
  const { isDark, toggle } = useThemeContext()

  return (
    <div className="h-[100dvh] flex flex-col bg-gray-50 dark:bg-gray-950 font-sans">
      {/* Header */}
      <header className="bg-indigo-600 dark:bg-indigo-700 text-white px-4 sm:px-6 py-3 flex items-center gap-3 shadow-lg shrink-0">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center shrink-0">
            <BarChart2 size={16} className="text-white" />
          </div>
          <div className="min-w-0">
            <p className="font-bold text-sm sm:text-base leading-tight truncate">AI Insights Assistant</p>
            <p className="text-indigo-200 text-xs hidden sm:block">Internal Analytics · FictStream</p>
          </div>
        </div>

        <button
          onClick={toggle}
          aria-label="Toggle theme"
          className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors shrink-0"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      {/* Filters */}
      <FilterPanel filters={filters} onChange={setFilters} />

      {/* Main panels */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Chat — always visible on desktop, conditionally on mobile */}
        <div
          className={clsx(
            'flex-1 min-w-0 overflow-hidden',
            mobileTab !== 'chat' ? 'hidden md:flex md:flex-col' : 'flex flex-col'
          )}
        >
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            error={error}
            onSend={sendMessage}
            filters={filters}
            onClear={clearHistory}
          />
        </div>

        {/* Right: Insights / Charts / Trace */}
        <div
          className={clsx(
            'md:w-96 md:shrink-0 md:border-l md:border-gray-200 md:dark:border-gray-700/60',
            'overflow-y-auto bg-gray-100 dark:bg-gray-900 p-4 space-y-4 scrollbar-thin',
            mobileTab !== 'insights' ? 'hidden md:block' : 'flex-1'
          )}
        >
          <InsightsPanel response={lastResponse} />

          {lastResponse?.chartSpecs && lastResponse.chartSpecs.length > 0 && (
            <ChartPanel chartSpecs={lastResponse.chartSpecs} isDark={isDark} />
          )}

          {lastResponse?.toolTrace && lastResponse.toolTrace.length > 0 && (
            <ToolTrace trace={lastResponse.toolTrace} />
          )}
        </div>
      </div>

      {/* Mobile bottom tab bar */}
      <nav className="md:hidden shrink-0 flex border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <button
          onClick={() => setMobileTab('chat')}
          className={clsx(
            'flex-1 flex flex-col items-center gap-0.5 py-2.5 text-xs font-medium transition-colors',
            mobileTab === 'chat'
              ? 'text-indigo-600 dark:text-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
          )}
        >
          <MessageSquare size={20} />
          Chat
          {messages.length > 0 && (
            <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-indigo-500" />
          )}
        </button>

        <button
          onClick={() => setMobileTab('insights')}
          className={clsx(
            'flex-1 flex flex-col items-center gap-0.5 py-2.5 text-xs font-medium transition-colors',
            mobileTab === 'insights'
              ? 'text-indigo-600 dark:text-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
          )}
        >
          <BarChart2 size={20} />
          Insights
        </button>
      </nav>
    </div>
  )
}
