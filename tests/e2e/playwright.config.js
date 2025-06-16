import { defineConfig, devices } from '@playwright/test';

/**
 * Configuración de Playwright para tests E2E de Sumy v2
 */
export default defineConfig({
  testDir: './tests',
  
  /* Timeout para cada test */
  timeout: 60000,
  
  /* Expect timeout */
  expect: {
    timeout: 10000,
  },
  
  /* Configuración de ejecución */
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter */
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['list']
  ],
  
  /* Configuración global */
  use: {
    /* URL base para los tests */
    baseURL: process.env.UI_URL || 'https://maitre-ia.web.app',
    
    /* Timeout para acciones */
    actionTimeout: 10000,
    
    /* Screenshots y videos */
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    /* Tracing */
    trace: 'on-first-retry',
  },

  /* Configuración de proyectos */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    /* Tests móviles */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    /* Tests con diferentes viewports */
    {
      name: 'Desktop Large',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1920, height: 1080 },
      },
    },
  ],

  /* Servidor web local para desarrollo */
  webServer: process.env.NODE_ENV === 'development' ? {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  } : undefined,
}); 