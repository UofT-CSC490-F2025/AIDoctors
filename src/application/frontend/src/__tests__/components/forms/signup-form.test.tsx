/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

const mockPush = jest.fn();
const mockGetApiBaseUrl = jest.fn(() => 'http://localhost:8000');
const mockFetch = jest.fn();

// Setup global fetch mock
global.fetch = mockFetch as any;

// Mock the hooks and dependencies
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    prefetch: jest.fn(),
  }),
}));

jest.mock('@/utils/api', () => ({
  getApiBaseUrl: mockGetApiBaseUrl,
}));

describe('SignupForm Component', () => {
  beforeEach(() => {
    mockPush.mockClear();
    mockGetApiBaseUrl.mockClear();
    mockFetch.mockClear();
  });

  it('should render signup form with all required fields', async () => {
    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    expect(screen.getByPlaceholderText(/enter your first name/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter your last name/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter a username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter a password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  it('should submit form with valid data and redirect to login', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 201,
      ok: true,
      json: async () => ({ message: 'User created successfully' }),
    });

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'John');
    await userEvent.type(lastNameInput, 'Doe');
    await userEvent.type(usernameInput, 'johndoe');
    await userEvent.type(emailInput, 'john.doe@example.com');
    await userEvent.type(passwordInput, 'SecurePassword123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/users/register',
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.any(String),
        })
      );
    });

    const fetchCall = mockFetch.mock.calls[0];
    const requestBody = JSON.parse(fetchCall[1].body);
    expect(requestBody).toEqual({
      first_name: 'John',
      last_name: 'Doe',
      username: 'johndoe',
      email: 'john.doe@example.com',
      password: 'SecurePassword123',
    });

    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  it('should display error message when API returns client error', async () => {
    const errorMessage = 'Username already exists';
    
    mockFetch.mockResolvedValueOnce({
      status: 400,
      ok: false,
      json: async () => ({ detail: errorMessage }),
    });

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'John');
    await userEvent.type(lastNameInput, 'Doe');
    await userEvent.type(usernameInput, 'existinguser');
    await userEvent.type(emailInput, 'john.doe@example.com');
    await userEvent.type(passwordInput, 'SecurePassword123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should display error message when email is already registered', async () => {
    const errorMessage = 'Email already registered';
    
    mockFetch.mockResolvedValueOnce({
      status: 409,
      ok: false,
      json: async () => ({ detail: errorMessage }),
    });

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'John');
    await userEvent.type(lastNameInput, 'Doe');
    await userEvent.type(usernameInput, 'johndoe');
    await userEvent.type(emailInput, 'existing@example.com');
    await userEvent.type(passwordInput, 'SecurePassword123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should display generic error message when API request fails', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 500,
      ok: false,
      json: async () => ({}),
    });

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'John');
    await userEvent.type(lastNameInput, 'Doe');
    await userEvent.type(usernameInput, 'johndoe');
    await userEvent.type(emailInput, 'john.doe@example.com');
    await userEvent.type(passwordInput, 'SecurePassword123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/request failed/i)).toBeInTheDocument();
    });

    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should display error message when network error occurs', async () => {
    // Suppress console.error
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'John');
    await userEvent.type(lastNameInput, 'Doe');
    await userEvent.type(usernameInput, 'johndoe');
    await userEvent.type(emailInput, 'john.doe@example.com');
    await userEvent.type(passwordInput, 'SecurePassword123');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
    });

    // Assert the error was handled/logged internally
    expect(consoleSpy).toHaveBeenCalled();
    // Restore console.error to avoid hiding real errors in other tests
    consoleSpy.mockRestore();
  });

  it('should format request body correctly with snake_case keys', async () => {
    mockFetch.mockResolvedValueOnce({
      status: 201,
      ok: true,
      json: async () => ({ message: 'User created successfully' }),
    });

    const { SignupForm } = await import('@/components/forms/signup-form');
    render(<SignupForm />);
    
    const firstNameInput = screen.getByPlaceholderText(/enter your first name/i) as HTMLInputElement;
    const lastNameInput = screen.getByPlaceholderText(/enter your last name/i) as HTMLInputElement;
    const usernameInput = screen.getByPlaceholderText(/enter a username/i) as HTMLInputElement;
    const emailInput = screen.getByPlaceholderText(/enter your email/i) as HTMLInputElement;
    const passwordInput = screen.getByPlaceholderText(/enter a password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /sign up/i });

    await userEvent.type(firstNameInput, 'Jane');
    await userEvent.type(lastNameInput, 'Smith');
    await userEvent.type(usernameInput, 'janesmith');
    await userEvent.type(emailInput, 'jane.smith@example.com');
    await userEvent.type(passwordInput, 'AnotherPassword456');
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });

    const fetchCall = mockFetch.mock.calls[0];
    const requestBody = JSON.parse(fetchCall[1].body);
    
    // Verify snake_case formatting
    expect(requestBody).toHaveProperty('first_name', 'Jane');
    expect(requestBody).toHaveProperty('last_name', 'Smith');
    expect(requestBody).toHaveProperty('username', 'janesmith');
    expect(requestBody).toHaveProperty('email', 'jane.smith@example.com');
    expect(requestBody).toHaveProperty('password', 'AnotherPassword456');
  });
});
