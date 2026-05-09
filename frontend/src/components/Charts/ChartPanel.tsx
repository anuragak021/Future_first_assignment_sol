import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer,
} from 'recharts'
import type { ChartSpec } from '../../types'

interface Props {
  chartSpecs: ChartSpec[]
  isDark?: boolean
}

function chartColors(isDark: boolean) {
  return {
    grid: isDark ? '#374151' : '#f0f0f0',
    tick: isDark ? '#9ca3af' : '#6b7280',
    bar: isDark ? '#818cf8' : '#6366f1',
    line: isDark ? '#818cf8' : '#6366f1',
    tooltipBg: isDark ? '#1f2937' : '#ffffff',
    tooltipBorder: isDark ? '#374151' : '#e5e7eb',
    tooltipText: isDark ? '#f9fafb' : '#111827',
  }
}

function renderChart(spec: ChartSpec, index: number, isDark: boolean) {
  const data = spec.data?.values ?? []
  const enc = spec.encoding ?? {}
  const xField = (enc.x as { field?: string })?.field ?? 'x'
  const yField = (enc.y as { field?: string })?.field ?? 'y'
  const colorField = (enc.color as { field?: string })?.field
  const c = chartColors(isDark)

  const cardCls =
    'bg-white dark:bg-gray-800/60 rounded-xl border border-gray-200 dark:border-gray-700 p-4'

  const tooltipStyle = {
    backgroundColor: c.tooltipBg,
    border: `1px solid ${c.tooltipBorder}`,
    color: c.tooltipText,
    borderRadius: '0.5rem',
    fontSize: '0.75rem',
  }

  if (spec.mark === 'bar') {
    return (
      <div key={index} className={cardCls}>
        {spec.title && (
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">{spec.title}</h4>
        )}
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={data} margin={{ top: 5, right: 16, left: -10, bottom: 55 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
            <XAxis
              dataKey={xField}
              tick={{ fontSize: 11, fill: c.tick }}
              angle={-35}
              textAnchor="end"
              tickLine={false}
              axisLine={false}
            />
            <YAxis tick={{ fontSize: 11, fill: c.tick }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.03)' }} />
            <Bar dataKey={yField} fill={c.bar} radius={[4, 4, 0, 0]} maxBarSize={48} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (spec.mark === 'line') {
    return (
      <div key={index} className={cardCls}>
        {spec.title && (
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">{spec.title}</h4>
        )}
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data} margin={{ top: 5, right: 16, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
            <XAxis dataKey={xField} tick={{ fontSize: 11, fill: c.tick }} tickLine={false} axisLine={false} />
            <YAxis tick={{ fontSize: 11, fill: c.tick }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            {colorField && <Legend wrapperStyle={{ fontSize: '0.75rem', color: c.tick }} />}
            <Line
              type="monotone"
              dataKey={yField}
              stroke={c.line}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: c.line }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return null
}

export function ChartPanel({ chartSpecs, isDark = false }: Props) {
  if (!chartSpecs || chartSpecs.length === 0) return null

  return (
    <div className="space-y-3">
      <h3 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest">Charts</h3>
      {chartSpecs.map((spec, i) => renderChart(spec, i, isDark))}
    </div>
  )
}
