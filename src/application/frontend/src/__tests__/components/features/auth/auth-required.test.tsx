/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

const mockReplace = jest.fn();
const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
};

// Mock the hooks and dependencies
jest.mock('@/hooks/useUser');
jest.mock('next/dist/client/components/navigation', () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

jest.mock('@/components/ui/loading-screen', () => ({
  LoadingScreen: () => <div data-testid="loading-screen">Loading...</div>,
}));

describe('AuthRequired Component', () => {
  beforeEach(() => {
    mockReplace.mockClear();
  });

  it('should render loading screen when user is loading', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: true,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should redirect to login when user is not authenticated and not loading', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('/login');
    });

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should render children when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: false,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByTestId('loading-screen')).not.toBeInTheDocument();
    expect(mockReplace).not.toHaveBeenCalled();
  });

  it('should show loading screen when user exists but isLoading is true', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: true,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should redirect only once when user state changes from loading to null', async () => {
    const { useUser } = require('@/hooks/useUser');
    const mockUseUser = useUser as jest.Mock;

    mockUseUser.mockReturnValue({
      user: null,
      isLoading: true,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    const { rerender } = render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(mockReplace).not.toHaveBeenCalled();

    // Update to not loading with no user
    mockUseUser.mockReturnValue({
      user: null,
      isLoading: false,
    });

    rerender(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledTimes(1);
      expect(mockReplace).toHaveBeenCalledWith('/login');
    });
  });

  it('should render children when user becomes authenticated after loading', async () => {
    const { useUser } = require('@/hooks/useUser');
    const mockUseUser = useUser as jest.Mock;

    mockUseUser.mockReturnValue({
      user: null,
      isLoading: true,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    const { rerender } = render(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();

    // Update to authenticated user
    mockUseUser.mockReturnValue({
      user: mockUser,
      isLoading: false,
    });

    rerender(
      <AuthRequired>
        <div>Protected Content</div>
      </AuthRequired>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByTestId('loading-screen')).not.toBeInTheDocument();
    expect(mockReplace).not.toHaveBeenCalled();
  });

  it('should render multiple children correctly', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: false,
    });

    const { AuthRequired } = await import(
      '@/components/features/auth/auth-required'
    );
    render(
      <AuthRequired>
        <div>First Child</div>
        <div>Second Child</div>
        <span>Third Child</span>
      </AuthRequired>
    );

    expect(screen.getByText('First Child')).toBeInTheDocument();
    expect(screen.getByText('Second Child')).toBeInTheDocument();
    expect(screen.getByText('Third Child')).toBeInTheDocument();
  });
});
