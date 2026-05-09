import type { Filters } from '../../types'

interface Props {
  filters: Filters
  onChange: (filters: Filters) => void
}

const YEARS = [2023, 2024, 2025]
const REGIONS = ['All', 'North', 'South', 'East', 'West', 'Central']
const GENRES = ['All', 'Sci-Fi', 'Thriller', 'Drama', 'Romance', 'Comedy', 'Action', 'Mystery']

const selectCls =
  'text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 ' +
  'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 ' +
  'focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400'

export function FilterPanel({ filters, onChange }: Props) {
  const hasFilters = !!(filters.year || filters.region || filters.genre)

  return (
    <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700/60 px-4 py-2.5 flex items-center gap-3 overflow-x-auto shrink-0 scrollbar-thin">
      <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest shrink-0">
        Filters
      </span>

      <div className="flex items-center gap-1.5 shrink-0">
        <label className="text-xs text-gray-500 dark:text-gray-400">Year</label>
        <select
          value={filters.year ?? ''}
          onChange={e => onChange({ ...filters, year: e.target.value ? Number(e.target.value) : undefined })}
          className={selectCls}
        >
          <option value="">All</option>
          {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        <label className="text-xs text-gray-500 dark:text-gray-400">Region</label>
        <select
          value={filters.region ?? ''}
          onChange={e => onChange({ ...filters, region: e.target.value || undefined })}
          className={selectCls}
        >
          {REGIONS.map(r => <option key={r} value={r === 'All' ? '' : r}>{r}</option>)}
        </select>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        <label className="text-xs text-gray-500 dark:text-gray-400">Genre</label>
        <select
          value={filters.genre ?? ''}
          onChange={e => onChange({ ...filters, genre: e.target.value || undefined })}
          className={selectCls}
        >
          {GENRES.map(g => <option key={g} value={g === 'All' ? '' : g}>{g}</option>)}
        </select>
      </div>

      {hasFilters && (
        <button
          onClick={() => onChange({})}
          className="shrink-0 text-xs px-2.5 py-1 rounded-full bg-red-50 dark:bg-red-900/30 text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/50 transition-colors"
        >
          Clear
        </button>
      )}
    </div>
  )
}
