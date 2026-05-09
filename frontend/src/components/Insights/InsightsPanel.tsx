import clsx from 'clsx'
import { CheckCircle, AlertTriangle, XCircle, BarChart2 } from 'lucide-react'
import type { ChatResponse } from '../../types'

interface Props {
  response: ChatResponse | null
}

const VERDICT_CONFIG = {
  PASS: {
    label: 'Verified',
    icon: CheckCircle,
    cls: 'text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800',
    bar: 'bg-emerald-500',
  },
  SOFT_FAIL: {
    label: 'Partial verification',
    icon: AlertTriangle,
    cls: 'text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800',
    bar: 'bg-amber-400',
  },
  HARD_FAIL: {
    label: 'Could not fully verify',
    icon: XCircle,
    cls: 'text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    bar: 'bg-red-500',
  },
  UNKNOWN: {
    label: 'Unverified',
    icon: AlertTriangle,
    cls: 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700',
    bar: 'bg-gray-400',
  },
}

export function InsightsPanel({ response }: Props) {
  if (!response) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center text-gray-400 dark:text-gray-600 select-none">
        <div className="w-12 h-12 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
          <BarChart2 size={22} className="text-gray-300 dark:text-gray-600" />
        </div>
        <p className="text-sm font-medium text-gray-500 dark:text-gray-500">No insights yet</p>
        <p className="text-xs mt-1">Insights appear after your first question.</p>
      </div>
    )
  }

  const cfg = VERDICT_CONFIG[response.verdict] ?? VERDICT_CONFIG.UNKNOWN
  const Icon = cfg.icon
  const pct = Math.round(response.faithfulnessScore * 100)

  return (
    <div className="space-y-3">
      {/* Verdict badge */}
      <div className={clsx('border rounded-xl px-4 py-3 flex items-start gap-3', cfg.cls)}>
        <Icon size={18} className="mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{cfg.label}</p>
          <div className="mt-1.5 flex items-center gap-2">
            <div className="flex-1 h-1.5 rounded-full bg-black/10 dark:bg-white/10 overflow-hidden">
              <div className={clsx('h-full rounded-full transition-all duration-500', cfg.bar)} style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs font-medium shrink-0">Faithfulness: {pct}%</span>
          </div>
        </div>
      </div>

      {/* Uncertainty note */}
      {response.uncertaintyNotes && (
        <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-xl px-4 py-3 text-sm text-orange-700 dark:text-orange-400">
          <strong>Note:</strong> {response.uncertaintyNotes}
        </div>
      )}

      {/* Session ID */}
      <div className="bg-white dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-3">
        <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest mb-1.5">Session</p>
        <p className="text-xs text-gray-500 dark:text-gray-400 break-all font-mono leading-relaxed">{response.sessionId}</p>
      </div>
    </div>
  )
}
