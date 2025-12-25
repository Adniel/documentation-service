/**
 * E2E tests for Learning Module components.
 *
 * Sprint 9: Learning Module Basics
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8000/api/v1';

// Test user credentials
const TEST_USER = {
  email: 'test@example.com',
  password: 'TestPass123',
};

// Helper to login and get auth token
async function login(page: any) {
  const response = await page.request.post(`${API_URL}/auth/login`, {
    form: {
      username: TEST_USER.email,
      password: TEST_USER.password,
    },
  });
  const data = await response.json();
  return data.access_token;
}

test.describe('Learning Module', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    const token = await login(page);

    // Set the token in localStorage before navigating
    await page.addInitScript((token) => {
      localStorage.setItem(
        'auth-storage',
        JSON.stringify({
          state: {
            accessToken: token,
            user: { email: 'test@example.com' },
          },
          version: 0,
        })
      );
    }, token);
  });

  test('should load training progress component', async ({ page }) => {
    // Navigate to training progress page (if exists)
    await page.goto(BASE_URL);

    // Check the page loads without errors
    await expect(page).toHaveTitle(/Documentation/i);
  });

  test('should access learning API endpoints', async ({ page }) => {
    const token = await login(page);

    // Test assignments endpoint
    const assignmentsResponse = await page.request.get(`${API_URL}/learning/assignments/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(assignmentsResponse.ok()).toBeTruthy();

    // Test completion report endpoint
    const completionResponse = await page.request.get(`${API_URL}/learning/reports/completion`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(completionResponse.ok()).toBeTruthy();

    // Test overdue report endpoint
    const overdueResponse = await page.request.get(`${API_URL}/learning/reports/overdue`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(overdueResponse.ok()).toBeTruthy();
    const overdueData = await overdueResponse.json();
    expect(overdueData).toHaveProperty('total_overdue');
    expect(overdueData).toHaveProperty('assignments');

    // Test acknowledgments endpoint
    const ackResponse = await page.request.get(`${API_URL}/learning/acknowledgments/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(ackResponse.ok()).toBeTruthy();
  });

  test('should export report as JSON', async ({ page }) => {
    const token = await login(page);

    const response = await page.request.post(`${API_URL}/learning/reports/export`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      data: {
        report_type: 'completion',
        format: 'json',
      },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('report_type', 'completion');
    expect(data).toHaveProperty('generated_at');
    expect(data).toHaveProperty('data');
  });

  test('should export report as CSV', async ({ page }) => {
    const token = await login(page);

    const response = await page.request.post(`${API_URL}/learning/reports/export`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      data: {
        report_type: 'completion',
        format: 'csv',
      },
    });

    expect(response.ok()).toBeTruthy();
    expect(response.headers()['content-type']).toContain('text/csv');
  });

  test('should get user training history', async ({ page }) => {
    const token = await login(page);

    // First get the user ID from the /me endpoint
    const meResponse = await page.request.get(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const userData = await meResponse.json();
    const userId = userData.id;

    // Get user training history
    const response = await page.request.get(`${API_URL}/learning/reports/user/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('user_id', userId);
    expect(data).toHaveProperty('user_email');
    expect(data).toHaveProperty('total_assignments');
    expect(data).toHaveProperty('acknowledgments');
  });

  test('should return 404 for non-existent user', async ({ page }) => {
    const token = await login(page);

    const response = await page.request.get(
      `${API_URL}/learning/reports/user/00000000-0000-0000-0000-000000000000`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    expect(response.status()).toBe(404);
  });
});
