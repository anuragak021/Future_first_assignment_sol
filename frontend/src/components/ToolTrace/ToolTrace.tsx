import { useState } from 'react'
import { ChevronDown, ChevronRight, Wrench } from 'lucide-react'
import type { ToolTraceEntry } from '../../types'

interface Props {
  trace: ToolTraceEntry[]
}

function TraceRow({ entry, index }: { entry: ToolTraceEntry; index: number }) {
  const [open, setOpen] = useState(false)
  const agent = entry.agent ?? `step-${index}`

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 px-3 py-2.5 bg-gray-50 dark:bg-gray-800/60 hover:bg-gray-100 dark:hover:bg-gray-800 text-left text-sm transition-colors"
      >
        {open
          ? <ChevronDown size={13} className="text-gray-400 shrink-0" />
          : <ChevronRight size={13} className="text-gray-400 shrink-0" />
        }
        <span className="font-medium text-gray-700 dark:text-gray-300 capitalize truncate">
          {String(agent).replace(/_/g, ' ')}
        </span>
        <span className="ml-auto text-xs text-gray-400 dark:text-gray-500 shrink-0">#{index + 1}</span>
      </button>
      {open && (
        <div className="px-3 py-2.5 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-700">
          <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-x-auto whitespace-pre-wrap leading-relaxed scrollbar-thin">
            {JSON.stringify(entry, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export function ToolTrace({ trace }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (!trace || trace.length === 0) return null

  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(o => !o)}
        className="w-full flex items-center gap-2 px-4 py-3 bg-gray-50 dark:bg-gray-800/60 hover:bg-gray-100 dark:hover:bg-gray-800 text-sm font-semibold text-gray-700 dark:text-gray-300 transition-colors"
      >
        <Wrench size={14} className="text-gray-400 shrink-0" />
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        Tool Trace
        <span className="ml-auto text-xs font-normal text-gray-400 dark:text-gray-500">
          {trace.length} {trace.length === 1 ? 'step' : 'steps'}
        </span>
      </button>
      {expanded && (
        <div className="p-3 space-y-2 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-700">
          {trace.map((entry, i) => (
            <TraceRow key={i} entry={entry} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
