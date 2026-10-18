import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Send, Bot, User, Loader, Sparkles, FileText } from 'lucide-react'

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your PrivacyAudit AI assistant. I can answer questions about your uploaded documents, compliance status, risks, and remediation recommendations. What would you like to know?'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await axios.post('/api/chat', { message: userMsg })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: res.data.content,
        sources: res.data.sources
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I encountered an error processing your question. Please try again, or note that the AI assistant requires Ollama to be running for enhanced responses.'
      }])
    } finally {
      setLoading(false)
    }
  }

  const quickQuestions = [
    'What personal data do we collect?',
    'What are our highest risks?',
    'Which controls are failing?',
    'What remediation is recommended?',
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-accent-100 dark:bg-accent-900/30 rounded-xl flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-accent-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI Compliance Assistant</h2>
          <p className="text-sm text-gray-500">Ask questions about your privacy documents and compliance posture</p>
        </div>
      </div>

      <div className="flex-1 card overflow-y-auto mb-4">
        <div className="space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-accent-100 dark:bg-accent-900/30 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-accent-600" />
                </div>
              )}
              <div className={`max-w-[80%] p-4 rounded-xl ${
                msg.role === 'user'
                  ? 'bg-primary-700 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
              }`}>
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                    <p className="text-xs font-medium text-gray-500 mb-1">Sources:</p>
                    {msg.sources.map((src, j) => (
                      <div key={j} className="flex items-start gap-1.5 text-xs text-gray-500">
                        <FileText className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span className="truncate">{src.snippet}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-primary-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-primary-700" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-accent-100 flex items-center justify-center">
                <Loader className="w-4 h-4 text-accent-600 animate-spin" />
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-xl">
                <p className="text-sm text-gray-500">Analyzing your documents...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Questions */}
      {messages.length <= 2 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {quickQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => { setInput(q) }}
              className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your privacy documents..."
          className="flex-1 input-field"
        />
        <button type="submit" disabled={loading} className="px-5 py-2.5 bg-primary-700 text-white rounded-lg hover:bg-primary-800 disabled:opacity-50 transition-colors">
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  )
}
