/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

const mockSetUser = jest.fn();
const mockPush = jest.fn();
const mockGetApiBaseUrl = jest.fn(() => 'http://localhost:8000');
const mockFetch = jest.fn();

// Setup global fetch mock
global.fetch = mockFetch as any;
// Mock the hooks and dependencies
jest.mock('@/hooks/useUser', () => ({
  useUser: () => ({
    setUser: mockSetUser,
  }),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    prefetch: jest.fn(),
  }),
}));

jest.mock('@/utils/api', () => ({
  getApiBaseUrl: mockGetApiBaseUrl,
}));

describe('LoginForm Component', () => {
  beforeEach(() => {
    mockSetUser.mockClear();
    mockPush.mockClear();
    mockGetApiBaseUrl.mockClear();
    mockFetch.mockClear();
  });

  it('should render login form with username and password fields', async () => {
    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    expect(screen.getByPlaceholderText(/enter your username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('should display error message on invalid credentials', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 401,
      ok: false,
    });

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'wrongpassword');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
    });
  });

  it('should successfully login and redirect to dashboard', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
      })
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
        json: async () => mockUser,
      });

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'correctpassword');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith(mockUser);
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should display error when token request fails with non-401 error', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 500,
      ok: false,
    });

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/request failed/i)).toBeInTheDocument();
    });
  });

  it('should display error when user data fetch fails', async () => {
    mockFetch
      .mockResolvedValueOnce({
        status: 200,
        ok: true,
      })
      .mockResolvedValueOnce({
        status: 500,
        ok: false,
      });

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'correctpassword');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to fetch user data/i)).toBeInTheDocument();
      expect(mockSetUser).toHaveBeenCalledWith(null);
    });
  });

  it('should display error when network error occurs', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
    });
  });

  it('should show loading state when form is submitting', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    const { LoginForm } = await import('@/components/forms/login-form');
    render(<LoginForm />);
    
    const usernameInput = screen.getByPlaceholderText(/enter your username/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/loading/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });
});
