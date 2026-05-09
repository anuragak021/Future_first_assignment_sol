import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight, oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import clsx from 'clsx'
import type { Components } from 'react-markdown'
import type { ChatMessage } from '../../types'
import { useThemeContext } from '../../context/ThemeContext'

interface Props {
  message: ChatMessage
}

function buildComponents(isDark: boolean): Components {
  return {
    table: ({ children }) => (
      <div className="my-3 overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-gray-50 dark:bg-gray-800/80">{children}</thead>
    ),
    tbody: ({ children }) => (
      <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60 bg-white dark:bg-gray-900">{children}</tbody>
    ),
    tr: ({ children }) => (
      <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">{children}</tr>
    ),
    th: ({ children }) => (
      <th className="px-4 py-2.5 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-4 py-2.5 text-gray-700 dark:text-gray-300 align-top">{children}</td>
    ),

    code: ({ className, children }) => {
      const match = /language-(\w+)/.exec(className || '')
      const isInline = !match && !String(children).includes('\n')

      if (isInline) {
        return (
          <code className="rounded bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 font-mono text-[0.8em] text-rose-600 dark:text-rose-400">
            {children}
          </code>
        )
      }

      const language = match ? match[1] : 'text'
      return (
        <div className="my-3 overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
          <div className="flex items-center bg-gray-800 dark:bg-gray-950 px-4 py-1.5">
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">{language}</span>
          </div>
          <SyntaxHighlighter
            style={isDark ? oneDark : oneLight}
            language={language}
            PreTag="div"
            customStyle={{ margin: 0, borderRadius: 0, fontSize: '0.8rem', lineHeight: '1.6' }}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      )
    },

    h1: ({ children }) => (
      <h1 className="mt-4 mb-2 text-lg font-bold text-gray-900 dark:text-gray-50 border-b border-gray-200 dark:border-gray-700 pb-1">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="mt-3 mb-1.5 text-base font-semibold text-gray-900 dark:text-gray-100">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="mt-2 mb-1 text-sm font-semibold text-gray-800 dark:text-gray-200">{children}</h3>
    ),

    ul: ({ children }) => (
      <ul className="my-2 space-y-1 pl-5 list-disc marker:text-gray-400 dark:marker:text-gray-600">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="my-2 space-y-1 pl-5 list-decimal marker:text-gray-400 dark:marker:text-gray-600">{children}</ol>
    ),
    li: ({ children }) => (
      <li className="text-gray-700 dark:text-gray-300 leading-relaxed">{children}</li>
    ),

    p: ({ children }) => (
      <p className="my-1.5 text-gray-700 dark:text-gray-300 leading-relaxed">{children}</p>
    ),

    blockquote: ({ children }) => (
      <blockquote className="my-3 border-l-4 border-indigo-300 dark:border-indigo-600 bg-indigo-50 dark:bg-indigo-900/20 pl-4 pr-3 py-2 rounded-r-lg text-gray-700 dark:text-gray-300 italic">
        {children}
      </blockquote>
    ),

    hr: () => <hr className="my-4 border-gray-200 dark:border-gray-700" />,

    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-indigo-600 dark:text-indigo-400 underline underline-offset-2 hover:text-indigo-800 dark:hover:text-indigo-300 transition-colors"
      >
        {children}
      </a>
    ),

    strong: ({ children }) => (
      <strong className="font-semibold text-gray-900 dark:text-gray-100">{children}</strong>
    ),
    em: ({ children }) => (
      <em className="italic text-gray-700 dark:text-gray-300">{children}</em>
    ),
  }
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'
  const { isDark } = useThemeContext()

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm',
          isUser
            ? 'max-w-[78%] bg-indigo-600 dark:bg-indigo-500 text-white rounded-br-sm'
            : 'max-w-[92%] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-sm'
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="min-w-0">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={buildComponents(isDark)}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        <p className={clsx('text-xs mt-1.5', isUser ? 'text-indigo-200' : 'text-gray-400 dark:text-gray-500')}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}
