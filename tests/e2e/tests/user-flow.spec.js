import { test, expect } from '@playwright/test';

/**
 * Tests End-to-End para flujo completo de usuario en Sumy v2
 */

test.describe('Flujo completo de usuario', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navegar a la aplicación
    await page.goto('/');
    
    // Esperar a que la página cargue completamente
    await page.waitForLoadState('networkidle');
  });

  test('Carga inicial de la aplicación', async ({ page }) => {
    // Verificar que el título sea correcto
    await expect(page).toHaveTitle(/Sumy/);
    
    // Verificar elementos principales de la UI
    await expect(page.locator('.app')).toBeVisible();
    
    // Debería mostrar la pantalla de login inicialmente
    await expect(page.locator('.login-container')).toBeVisible();
  });

  test('Interfaz de login', async ({ page }) => {
    // Verificar elementos de login
    await expect(page.locator('.login-title')).toContainText('Sumy');
    await expect(page.locator('.google-login-btn')).toBeVisible();
    await expect(page.locator('.google-login-btn')).toContainText('Continuar con Google');
    
    // Verificar que el botón sea clickeable
    await expect(page.locator('.google-login-btn')).toBeEnabled();
  });

  test('Navegación responsive', async ({ page }) => {
    // Test en desktop
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.locator('.app')).toBeVisible();
    
    // Test en tablet
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('.app')).toBeVisible();
    
    // Test en móvil
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.app')).toBeVisible();
    
    // La aplicación debería adaptarse a diferentes tamaños
    const appElement = page.locator('.app');
    await expect(appElement).toHaveCSS('width', '375px');
  });
});

test.describe('Flujo de autenticación (Mock)', () => {
  
  test('Simulación de login exitoso', async ({ page }) => {
    // Interceptar llamadas de Firebase Auth
    await page.route('**/identitytoolkit.googleapis.com/**', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          kind: 'identitytoolkit#VerifyAssertionResponse',
          localId: 'test-user-id',
          email: 'test@example.com',
          displayName: 'Test User',
          idToken: 'mock-id-token',
          refreshToken: 'mock-refresh-token'
        })
      });
    });
    
    // Simular usuario autenticado en el localStorage
    await page.addInitScript(() => {
      const mockUser = {
        uid: 'test-user-id',
        email: 'test@example.com',
        displayName: 'Test User'
      };
      window.localStorage.setItem('sumy-user', JSON.stringify(mockUser));
    });
    
    await page.reload();
    
    // Debería mostrar la interfaz de chat
    await expect(page.locator('.chat-container')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
    await expect(page.locator('.send-button')).toBeVisible();
  });
});

test.describe('Interfaz de chat', () => {
  
  test.beforeEach(async ({ page }) => {
    // Simular usuario autenticado
    await page.addInitScript(() => {
      const mockUser = {
        uid: 'test-user-id',
        email: 'test@example.com',
        displayName: 'Test User'
      };
      window.localStorage.setItem('sumy-user', JSON.stringify(mockUser));
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Elementos de la interfaz de chat', async ({ page }) => {
    // Verificar elementos principales
    await expect(page.locator('.chat-container')).toBeVisible();
    await expect(page.locator('.message-input')).toBeVisible();
    await expect(page.locator('.send-button')).toBeVisible();
    
    // Verificar placeholder del input
    await expect(page.locator('.message-input')).toHaveAttribute('placeholder', /pregunta/i);
    
    // Verificar estado inicial
    await expect(page.locator('.message-input')).toHaveValue('');
    await expect(page.locator('.send-button')).toBeEnabled();
  });

  test('Envío de mensaje básico', async ({ page }) => {
    const messageInput = page.locator('.message-input');
    const sendButton = page.locator('.send-button');
    
    // Escribir mensaje
    await messageInput.fill('¿Qué vino me recomiendas?');
    
    // Interceptar llamada a la API
    await page.route('**/query', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Te recomiendo un excelente Rioja Reserva...',
          metadata: {
            classification: 'WINE_SEARCH',
            rag_used: true,
            wine_results: 2,
            knowledge_results: 0
          }
        })
      });
    });
    
    // Enviar mensaje
    await sendButton.click();
    
    // Verificar que el mensaje aparece en el chat
    await expect(page.locator('.message-user')).toContainText('¿Qué vino me recomiendas?');
    
    // Esperar respuesta del sumiller
    await expect(page.locator('.message-assistant')).toBeVisible({ timeout: 30000 });
    await expect(page.locator('.message-assistant')).toContainText('Rioja Reserva');
  });

  test('Envío de mensaje con Enter', async ({ page }) => {
    const messageInput = page.locator('.message-input');
    
    await messageInput.fill('Test message');
    
    // Interceptar API
    await page.route('**/query', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Respuesta de prueba',
          metadata: { classification: 'GENERAL', rag_used: false }
        })
      });
    });
    
    // Presionar Enter
    await messageInput.press('Enter');
    
    // Verificar mensaje enviado
    await expect(page.locator('.message-user')).toContainText('Test message');
  });

  test('Prevención de mensajes vacíos', async ({ page }) => {
    const sendButton = page.locator('.send-button');
    
    // Intentar enviar mensaje vacío
    await sendButton.click();
    
    // No debería aparecer ningún mensaje
    await expect(page.locator('.message-user')).not.toBeVisible();
  });

  test('Estado de carga durante respuesta', async ({ page }) => {
    const messageInput = page.locator('.message-input');
    const sendButton = page.locator('.send-button');
    
    // Interceptar API con delay
    await page.route('**/query', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Respuesta después del delay',
          metadata: { classification: 'GENERAL', rag_used: false }
        })
      });
    });
    
    await messageInput.fill('Mensaje de prueba');
    await sendButton.click();
    
    // Verificar estado de carga
    await expect(messageInput).toBeDisabled();
    await expect(sendButton).toBeDisabled();
    await expect(page.locator('.loading-indicator')).toBeVisible();
    
    // Esperar a que termine la carga
    await expect(page.locator('.message-assistant')).toBeVisible({ timeout: 10000 });
    
    // Verificar que se restaura el estado normal
    await expect(messageInput).toBeEnabled();
    await expect(sendButton).toBeEnabled();
    await expect(page.locator('.loading-indicator')).not.toBeVisible();
  });
});

test.describe('Tipos de consultas', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup usuario autenticado
    await page.addInitScript(() => {
      window.localStorage.setItem('sumy-user', JSON.stringify({
        uid: 'test-user-id',
        email: 'test@example.com'
      }));
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Consulta de recomendación de vino', async ({ page }) => {
    await page.route('**/query', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Te recomiendo un **Tempranillo de Ribera del Duero**...',
          metadata: {
            classification: 'WINE_SEARCH',
            rag_used: true,
            wine_results: 3,
            knowledge_results: 0
          }
        })
      });
    });
    
    await page.fill('.message-input', 'Recomiéndame un vino tinto español');
    await page.click('.send-button');
    
    // Verificar respuesta con formato markdown
    await expect(page.locator('.message-assistant strong')).toContainText('Tempranillo');
  });

  test('Consulta teórica sobre vinos', async ({ page }) => {
    await page.route('**/query', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Los **taninos** son compuestos polifenólicos...',
          metadata: {
            classification: 'WINE_THEORY',
            rag_used: true,
            wine_results: 0,
            knowledge_results: 2
          }
        })
      });
    });
    
    await page.fill('.message-input', '¿Qué son los taninos?');
    await page.click('.send-button');
    
    await expect(page.locator('.message-assistant')).toContainText('taninos');
  });

  test('Consulta de maridaje', async ({ page }) => {
    await page.route('**/query', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Para el salmón te recomiendo un **Albariño**...',
          metadata: {
            classification: 'WINE_SEARCH',
            rag_used: true,
            wine_results: 2,
            knowledge_results: 1
          }
        })
      });
    });
    
    await page.fill('.message-input', '¿Qué vino va bien con salmón?');
    await page.click('.send-button');
    
    await expect(page.locator('.message-assistant')).toContainText('salmón');
    await expect(page.locator('.message-assistant')).toContainText('Albariño');
  });
});

test.describe('Manejo de errores', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('sumy-user', JSON.stringify({
        uid: 'test-user-id',
        email: 'test@example.com'
      }));
    });
    
    await page.goto('/');
  });

  test('Error de red', async ({ page }) => {
    // Simular error de red
    await page.route('**/query', route => {
      route.abort('failed');
    });
    
    await page.fill('.message-input', 'Test error message');
    await page.click('.send-button');
    
    // Debería mostrar mensaje de error
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText(/error/i);
  });

  test('Error del servidor', async ({ page }) => {
    await page.route('**/query', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    await page.fill('.message-input', 'Test server error');
    await page.click('.send-button');
    
    await expect(page.locator('.error-message')).toBeVisible();
  });
});

test.describe('Accesibilidad', () => {
  
  test('Navegación con teclado', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('sumy-user', JSON.stringify({
        uid: 'test-user-id'
      }));
    });
    
    await page.goto('/');
    
    // Navegar con Tab
    await page.keyboard.press('Tab');
    await expect(page.locator('.message-input')).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(page.locator('.send-button')).toBeFocused();
  });

  test('Atributos ARIA', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem('sumy-user', JSON.stringify({
        uid: 'test-user-id'
      }));
    });
    
    await page.goto('/');
    
    // Verificar atributos de accesibilidad
    await expect(page.locator('.message-input')).toHaveAttribute('aria-label');
    await expect(page.locator('.send-button')).toHaveAttribute('aria-label');
  });
});

test.describe('Performance', () => {
  
  test('Tiempo de carga inicial', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // La página debería cargar en menos de 5 segundos
    expect(loadTime).toBeLessThan(5000);
  });

  test('Tamaño de recursos', async ({ page }) => {
    const responses = [];
    
    page.on('response', response => {
      if (response.url().includes(page.url())) {
        responses.push(response);
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verificar que los recursos no sean excesivamente grandes
    for (const response of responses) {
      const contentLength = response.headers()['content-length'];
      if (contentLength) {
        expect(parseInt(contentLength)).toBeLessThan(5 * 1024 * 1024); // 5MB max
      }
    }
  });
}); 