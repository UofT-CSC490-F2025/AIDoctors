/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockReplace = jest.fn();
const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
};

// Mock dependencies BEFORE any imports
jest.mock('next/link', () => {
  const Link = ({ children, href, className, ...props }: any) => (
    <a href={href} className={className} {...props}>{children}</a>
  );
  return {
    __esModule: true,
    default: Link,
  };
});

jest.mock('next/dist/client/components/navigation', () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

jest.mock('@/hooks/useUser');

jest.mock('lucide-react', () => ({
  Brain: ({ className, ...props }: any) => (
    <span data-testid="brain-icon" className={className} {...props} />
  ),
}));

jest.mock('@/components/ui/loading-screen', () => ({
  LoadingScreen: () => <div data-testid="loading-screen">Loading...</div>,
}));

jest.mock('@/components/forms/signup-form', () => ({
  SignupForm: () => <div data-testid="signup-form">Signup Form</div>,
}));

describe('SignUpPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render signup page when user is not authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(
      screen.getByText('Create your AI Doctors account')
    ).toBeInTheDocument();
    expect(screen.getByTestId('signup-form')).toBeInTheDocument();
  });

  it('should show loading screen when user is loading', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: true,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();
    expect(screen.queryByTestId('signup-form')).not.toBeInTheDocument();
  });

  it('should show loading screen when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(screen.getByTestId('loading-screen')).toBeInTheDocument();
    expect(screen.queryByTestId('signup-form')).not.toBeInTheDocument();
  });

  it('should redirect to dashboard when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    await waitFor(() => {
      expect(mockReplace).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should render Brain icon', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(screen.getByTestId('brain-icon')).toBeInTheDocument();
  });

  it('should render description text', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(
      screen.getByText('Securely access patient-specific DDI insights.')
    ).toBeInTheDocument();
  });

  it('should render link to home page', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    const homeLink = screen.getByTestId('brain-icon').closest('a');
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('should render login link', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    const loginLink = screen
      .getByText('Sign in to existing account')
      .closest('a');
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  it('should render "Already have an account?" text', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    expect(screen.getByText('Already have an account?')).toBeInTheDocument();
  });

  it('should not redirect when user is null and not loading', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    const { default: SignUpPage } = await import('@/app/(login)/signup/page');
    render(<SignUpPage />);

    await waitFor(() => {
      expect(mockReplace).not.toHaveBeenCalled();
    });
  });
});
