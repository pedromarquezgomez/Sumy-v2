/**
 * Tests unitarios para Frontend Vue.js
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import axios from 'axios'

// Mock de Firebase Auth
vi.mock('@/config/firebase', () => ({
  auth: {
    currentUser: null,
    onAuthStateChanged: vi.fn(),
    signInWithPopup: vi.fn(),
    signOut: vi.fn()
  },
  googleProvider: {},
  db: {
    collection: vi.fn(() => ({
      doc: vi.fn(() => ({
        get: vi.fn(),
        set: vi.fn(),
        add: vi.fn()
      }))
    }))
  }
}))

// Mock de axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('App.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(App, {
      global: {
        plugins: [createTestingPinia()]
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('renders the main application', () => {
    expect(wrapper.find('.app').exists()).toBe(true)
  })

  it('shows login when user is not authenticated', () => {
    expect(wrapper.find('.login-container').exists()).toBe(true)
  })

  it('shows chat interface when user is authenticated', async () => {
    // Simular usuario autenticado
    await wrapper.setData({ user: { uid: 'test-user', email: 'test@test.com' } })
    expect(wrapper.find('.chat-container').exists()).toBe(true)
  })
})

describe('ChatInterface Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ChatInterface, {
      props: {
        user: { uid: 'test-user', email: 'test@test.com' }
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })
  })

  it('renders chat interface correctly', () => {
    expect(wrapper.find('.chat-interface').exists()).toBe(true)
    expect(wrapper.find('.message-input').exists()).toBe(true)
    expect(wrapper.find('.send-button').exists()).toBe(true)
  })

  it('sends message when send button is clicked', async () => {
    const messageInput = wrapper.find('.message-input')
    const sendButton = wrapper.find('.send-button')

    await messageInput.setValue('¿Qué vino me recomiendas?')
    await sendButton.trigger('click')

    expect(wrapper.vm.messages).toHaveLength(1)
    expect(wrapper.vm.messages[0].content).toBe('¿Qué vino me recomiendas?')
    expect(wrapper.vm.messages[0].type).toBe('user')
  })

  it('sends message when Enter key is pressed', async () => {
    const messageInput = wrapper.find('.message-input')

    await messageInput.setValue('Test message')
    await messageInput.trigger('keydown.enter')

    expect(wrapper.vm.messages).toHaveLength(1)
  })

  it('prevents sending empty messages', async () => {
    const sendButton = wrapper.find('.send-button')
    await sendButton.trigger('click')

    expect(wrapper.vm.messages).toHaveLength(0)
  })

  it('disables input while loading', async () => {
    await wrapper.setData({ isLoading: true })
    
    const messageInput = wrapper.find('.message-input')
    const sendButton = wrapper.find('.send-button')

    expect(messageInput.attributes('disabled')).toBeDefined()
    expect(sendButton.attributes('disabled')).toBeDefined()
  })
})

describe('MessageBubble Component', () => {
  it('renders user message correctly', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: {
          type: 'user',
          content: 'Test user message',
          timestamp: new Date()
        }
      }
    })

    expect(wrapper.find('.message-user').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test user message')
  })

  it('renders assistant message correctly', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: {
          type: 'assistant',
          content: 'Test assistant message',
          timestamp: new Date()
        }
      }
    })

    expect(wrapper.find('.message-assistant').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test assistant message')
  })

  it('renders markdown content', () => {
    const wrapper = mount(MessageBubble, {
      props: {
        message: {
          type: 'assistant',
          content: '**Bold text** and *italic text*',
          timestamp: new Date()
        }
      }
    })

    expect(wrapper.html()).toContain('<strong>Bold text</strong>')
    expect(wrapper.html()).toContain('<em>italic text</em>')
  })

  it('shows timestamp', () => {
    const timestamp = new Date('2024-01-01T12:00:00Z')
    const wrapper = mount(MessageBubble, {
      props: {
        message: {
          type: 'user',
          content: 'Test message',
          timestamp
        }
      }
    })

    expect(wrapper.find('.timestamp').exists()).toBe(true)
  })
})

describe('LoginComponent', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(LoginComponent, {
      global: {
        plugins: [createTestingPinia()]
      }
    })
  })

  it('renders login interface', () => {
    expect(wrapper.find('.login-container').exists()).toBe(true)
    expect(wrapper.find('.google-login-btn').exists()).toBe(true)
  })

  it('calls Google sign in when button is clicked', async () => {
    const googleBtn = wrapper.find('.google-login-btn')
    await googleBtn.trigger('click')

    // Verificar que se llamó a la función de login
    expect(wrapper.emitted('login')).toBeTruthy()
  })

  it('shows loading state during authentication', async () => {
    await wrapper.setData({ isLoading: true })
    
    const googleBtn = wrapper.find('.google-login-btn')
    expect(googleBtn.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Iniciando sesión...')
  })
})

describe('ConversationHistory Component', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(ConversationHistory, {
      props: {
        user: { uid: 'test-user' },
        conversations: [
          {
            id: 'conv1',
            title: 'Consulta sobre Rioja',
            lastMessage: 'Te recomiendo...',
            timestamp: new Date('2024-01-01')
          },
          {
            id: 'conv2',
            title: 'Maridaje con salmón',
            lastMessage: 'Para el salmón...',
            timestamp: new Date('2024-01-02')
          }
        ]
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })
  })

  it('renders conversation list', () => {
    expect(wrapper.findAll('.conversation-item')).toHaveLength(2)
  })

  it('emits conversation selection', async () => {
    const firstConversation = wrapper.find('.conversation-item')
    await firstConversation.trigger('click')

    expect(wrapper.emitted('select-conversation')).toBeTruthy()
    expect(wrapper.emitted('select-conversation')[0]).toEqual(['conv1'])
  })

  it('shows empty state when no conversations', async () => {
    await wrapper.setProps({ conversations: [] })
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })
})

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('sendMessage', () => {
    it('sends message to sumiller API', async () => {
      const mockResponse = {
        data: {
          response: 'Test response',
          metadata: {
            rag_used: true,
            classification: 'WINE_SEARCH'
          }
        }
      }
      mockedAxios.post.mockResolvedValue(mockResponse)

      const { sendMessage } = await import('@/services/api')
      
      const result = await sendMessage({
        query: 'Test query',
        user_id: 'test-user',
        conversation_history: []
      })

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/query'),
        {
          query: 'Test query',
          user_id: 'test-user',
          conversation_history: []
        }
      )
      expect(result.response).toBe('Test response')
    })

    it('handles API errors gracefully', async () => {
      mockedAxios.post.mockRejectedValue(new Error('Network error'))

      const { sendMessage } = await import('@/services/api')

      await expect(sendMessage({
        query: 'Test query',
        user_id: 'test-user',
        conversation_history: []
      })).rejects.toThrow('Network error')
    })
  })

  describe('loadConversationHistory', () => {
    it('loads conversation history from Firestore', async () => {
      const mockConversations = [
        { id: 'conv1', title: 'Test conversation' }
      ]

      const { loadConversationHistory } = await import('@/services/firestore')
      
      // Mock Firestore response
      const mockSnapshot = {
        docs: mockConversations.map(conv => ({
          id: conv.id,
          data: () => conv
        }))
      }

      const result = await loadConversationHistory('test-user')
      expect(Array.isArray(result)).toBe(true)
    })
  })
})

describe('Console Logging', () => {
  let consoleSpy

  beforeEach(() => {
    consoleSpy = vi.spyOn(console, 'group').mockImplementation(() => {})
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'groupEnd').mockImplementation(() => {})
  })

  afterEach(() => {
    consoleSpy.mockRestore()
  })

  it('logs traceability information', async () => {
    const { logTraceability } = await import('@/utils/console')

    const mockData = {
      query: 'Test query',
      response: 'Test response',
      metadata: {
        rag_used: true,
        classification: 'WINE_SEARCH',
        wine_results: 2,
        knowledge_results: 0
      }
    }

    logTraceability(mockData)

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('🍷 Sumy Traceability')
    )
  })
})

describe('Error Handling', () => {
  it('handles network errors', async () => {
    mockedAxios.post.mockRejectedValue(new Error('Network Error'))

    const wrapper = mount(ChatInterface, {
      props: {
        user: { uid: 'test-user' }
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })

    await wrapper.vm.sendMessage('Test message')

    expect(wrapper.vm.messages.some(msg => 
      msg.type === 'error' && msg.content.includes('Error')
    )).toBe(true)
  })

  it('handles authentication errors', async () => {
    const wrapper = mount(LoginComponent, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    // Simular error de autenticación
    await wrapper.vm.handleAuthError(new Error('Auth failed'))

    expect(wrapper.vm.error).toContain('Auth failed')
  })
})

describe('Responsive Design', () => {
  it('adapts to mobile viewport', async () => {
    // Simular viewport móvil
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ChatInterface, {
      props: {
        user: { uid: 'test-user' }
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })

    expect(wrapper.classes()).toContain('mobile-layout')
  })
})

describe('Performance', () => {
  it('debounces rapid message sending', async () => {
    const wrapper = mount(ChatInterface, {
      props: {
        user: { uid: 'test-user' }
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const messageInput = wrapper.find('.message-input')
    
    // Enviar múltiples mensajes rápidamente
    await messageInput.setValue('Message 1')
    await messageInput.trigger('keydown.enter')
    await messageInput.setValue('Message 2')
    await messageInput.trigger('keydown.enter')

    // Solo debería procesarse un mensaje debido al debounce
    expect(wrapper.vm.isLoading).toBe(true)
  })
}) 