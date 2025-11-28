/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
};

// Mock dependencies BEFORE any imports
jest.mock('@/hooks/useUser');

jest.mock('next/link', () => {
  const Link = ({ children, href, className, ...props }: any) => (
    <a href={href} className={className} {...props}>
      {children}
    </a>
  );
  return {
    __esModule: true,
    default: Link,
  };
});

jest.mock('lucide-react', () => ({
  Brain: ({ className, ...props }: any) => (
    <span data-testid="brain-icon" className={className} {...props} />
  ),
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, asChild, variant, className, ...props }: any) => (
    <button data-variant={variant} className={className} {...props}>
      {children}
    </button>
  ),
}));

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the logo and brand name', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.getByTestId('brain-icon')).toBeInTheDocument();
    expect(screen.getByText('AI Doctors')).toBeInTheDocument();
  });

  it('should render login and signup buttons when user is not authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.getByText('Log in')).toBeInTheDocument();
    expect(screen.getByText('Sign up')).toBeInTheDocument();
  });

  it('should render login link with correct href', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const loginLink = screen.getByText('Log in').closest('a');
    expect(loginLink).not.toBeNull();
    if (loginLink) {
      expect(loginLink.getAttribute('href')).toBe('/login');
    }
  });

  it('should render signup link with correct href', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const signupLink = screen.getByText('Sign up').closest('a');
    expect(signupLink).not.toBeNull();
    if (signupLink) {
      expect(signupLink.getAttribute('href')).toBe('/signup');
    }
  });

  it('should render dashboard link when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.getByText('Go to dashboard')).toBeInTheDocument();
  });

  it('should render dashboard link with correct href', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const dashboardLink = screen.getByText('Go to dashboard').closest('a');
    expect(dashboardLink).not.toBeNull();
    if (dashboardLink) {
      expect(dashboardLink.getAttribute('href')).toBe('/dashboard');
    }
  });

  it('should render username when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('should render "Account" when user has no username', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: { ...mockUser, username: null },
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.getByText('Account')).toBeInTheDocument();
  });

  it('should not render login/signup buttons when user is authenticated', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: mockUser,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    expect(screen.queryByText('Log in')).not.toBeInTheDocument();
    expect(screen.queryByText('Sign up')).not.toBeInTheDocument();
  });

  it('should render home link with correct href', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const brainIcon = screen.getByTestId('brain-icon');
    const homeLink = brainIcon.closest('a');
    expect(homeLink).not.toBeNull();
    if (homeLink) {
      expect(homeLink.getAttribute('href')).toBe('/');
    }
  });

  it('should apply ghost variant to login button', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const loginButton = screen.getByText('Log in').closest('button');
    expect(loginButton).not.toBeNull();
    if (loginButton) {
      expect(loginButton.getAttribute('data-variant')).toBe('ghost');
    }
  });

  it('should apply rounded-full class to buttons', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const loginButton = screen.getByText('Log in').closest('button');
    const signupButton = screen.getByText('Sign up').closest('button');
    
    expect(loginButton).not.toBeNull();
    expect(signupButton).not.toBeNull();
    
    if (loginButton) {
      expect(loginButton.className).toContain('rounded-full');
    }
    if (signupButton) {
      expect(signupButton.className).toContain('rounded-full');
    }
  });

  it('should render brain icon with correct styling', async () => {
    const { useUser } = require('@/hooks/useUser');
    (useUser as jest.Mock).mockReturnValue({
      user: null,
    });

    const { Header } = await import('@/components/layout/header');
    render(<Header />);

    const brainIcon = screen.getByTestId('brain-icon');
    expect(brainIcon.className).toContain('h-9');
    expect(brainIcon.className).toContain('w-9');
    expect(brainIcon.className).toContain('text-orange-500');
  });
});
