/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React, { useContext } from 'react';

const mockFetch = jest.fn();
const mockGetApiBaseUrl = jest.fn(() => 'http://localhost:8000');

// Setup global fetch mock
global.fetch = mockFetch as any;

// Mock the API utility
jest.mock('@/utils/api', () => ({
  getApiBaseUrl: mockGetApiBaseUrl,
}));

describe('UserProvider Component', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockGetApiBaseUrl.mockClear();
  });

  it('should provide user context with initial loading state', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      return (
        <div>
          <div data-testid="user">{context?.user ? 'User exists' : 'No user'}</div>
          <div data-testid="loading">{context?.isLoading ? 'Loading' : 'Not loading'}</div>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('Loading');
  });

  it('should fetch user on mount and set user on success', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      return (
        <div>
          <div data-testid="user">{context?.user?.username || 'No user'}</div>
          <div data-testid="loading">{context?.isLoading ? 'Loading' : 'Not loading'}</div>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('testuser');
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/users/me',
      expect.objectContaining({
        method: 'GET',
        credentials: 'include',
      })
    );
  });

  it('should set user to null when fetch fails', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      return (
        <div>
          <div data-testid="user">{context?.user ? 'User exists' : 'No user'}</div>
          <div data-testid="loading">{context?.isLoading ? 'Loading' : 'Not loading'}</div>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
  });

  it('should set user to null when network error occurs', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      return (
        <div>
          <div data-testid="user">{context?.user ? 'User exists' : 'No user'}</div>
          <div data-testid="loading">{context?.isLoading ? 'Loading' : 'Not loading'}</div>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('Not loading');
    });

    expect(screen.getByTestId('user')).toHaveTextContent('No user');
  });

  it('should allow setUser to update user state', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      
      return (
        <div>
          <div data-testid="user">{context?.user?.username || 'No user'}</div>
          <button onClick={() => context?.setUser(mockUser)}>Set User</button>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
    });

    const button = screen.getByText('Set User');
    button.click();

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser');
    });
  });

  it('should allow setUser to clear user state', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      
      return (
        <div>
          <div data-testid="user">{context?.user?.username || 'No user'}</div>
          <button onClick={() => context?.setUser(null)}>Clear User</button>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('testuser');
    });

    const button = screen.getByText('Clear User');
    button.click();

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('No user');
    });
  });

  it('should render children correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { UserProvider } = await import('@/components/features/auth/user-context');

    render(
      <UserProvider>
        <div>Child 1</div>
        <div>Child 2</div>
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Child 1')).toBeInTheDocument();
      expect(screen.getByText('Child 2')).toBeInTheDocument();
    });
  });

  it('should provide context value with all required properties', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const TestComponent = () => {
      const context = useContext(UserCtx);
      
      return (
        <div>
          <div data-testid="has-user">{context?.user !== undefined ? 'true' : 'false'}</div>
          <div data-testid="has-setUser">{typeof context?.setUser === 'function' ? 'true' : 'false'}</div>
          <div data-testid="has-isLoading">{context?.isLoading !== undefined ? 'true' : 'false'}</div>
        </div>
      );
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('has-user')).toHaveTextContent('true');
      expect(screen.getByTestId('has-setUser')).toHaveTextContent('true');
      expect(screen.getByTestId('has-isLoading')).toHaveTextContent('true');
    });
  });

  it('should fetch user data with correct API endpoint', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, username: 'test' }),
    });

    const { UserProvider } = await import('@/components/features/auth/user-context');

    render(
      <UserProvider>
        <div>Test</div>
      </UserProvider>
    );

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    expect(mockGetApiBaseUrl).toHaveBeenCalled();
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/users/me',
      expect.objectContaining({
        method: 'GET',
        credentials: 'include',
      })
    );
  });

  it('should set loading to false after successful fetch', async () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    const { UserProvider, UserCtx } = await import('@/components/features/auth/user-context');

    const loadingStates: boolean[] = [];

    const TestComponent = () => {
      const context = useContext(UserCtx);
      if (context) {
        loadingStates.push(context.isLoading);
      }
      return <div>{context?.isLoading ? 'Loading' : 'Done'}</div>;
    };

    render(
      <UserProvider>
        <TestComponent />
      </UserProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Done')).toBeInTheDocument();
    });

    // Should have been loading initially, then not loading
    expect(loadingStates).toContain(true);
    expect(loadingStates[loadingStates.length - 1]).toBe(false);
  });
});
