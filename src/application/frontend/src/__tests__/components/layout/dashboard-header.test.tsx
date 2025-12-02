/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

const mockSetUser = jest.fn();
const mockPathname = '/dashboard';
const mockFetch = jest.fn();

// Mock dependencies BEFORE any imports
jest.mock('@/hooks/useUser', () => ({
  useUser: () => ({
    setUser: mockSetUser,
  }),
}));

jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname,
}));

jest.mock('@/utils/api', () => ({
  getApiBaseUrl: () => 'http://localhost:3000',
}));

jest.mock('@/utils/general', () => ({
  pathname_equal: (path1: string, path2: string) => path1 === path2,
}));

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
  Button: ({
    children,
    type,
    variant,
    size,
    className,
    onClick,
    ...props
  }: any) => (
    <button
      type={type}
      data-variant={variant}
      data-size={size}
      className={className}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  ),
}));

describe('DashboardHeader Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = mockFetch as any;
  });

  it('should render the logo and brand name', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    expect(screen.getByTestId('brain-icon')).toBeInTheDocument();
    expect(screen.getByText('AI Doctors')).toBeInTheDocument();
  });

  it('should render navigation links', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Predict')).toBeInTheDocument();
  });

  it('should render overview link with correct href', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const overviewLink = screen.getByText('Overview').closest('a');
    expect(overviewLink).not.toBeNull();
    if (overviewLink) {
      expect(overviewLink.getAttribute('href')).toBe('/dashboard');
    }
  });

  it('should render predict link with correct href', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const predictLink = screen.getByText('Predict').closest('a');
    expect(predictLink).not.toBeNull();
    if (predictLink) {
      expect(predictLink.getAttribute('href')).toBe('/dashboard/predict');
    }
  });

  it('should render sign out button', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    expect(screen.getByText('Sign out')).toBeInTheDocument();
  });

  it('should apply active styling to current page', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const overviewLink = screen.getByText('Overview').closest('a');
    expect(overviewLink).not.toBeNull();
    if (overviewLink) {
      expect(overviewLink.className).toContain('bg-orange-50');
      expect(overviewLink.className).toContain('text-orange-700');
    }
  });

  it('should not apply active styling to non-current page', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const predictLink = screen.getByText('Predict').closest('a');
    expect(predictLink).not.toBeNull();
    if (predictLink) {
      expect(predictLink.className).toContain('text-gray-700');
      expect(predictLink.className).toContain('hover:bg-gray-100');
    }
  });

  it('should call logout API when sign out button is clicked', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const signOutButton = screen.getByText('Sign out');
    fireEvent.click(signOutButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:3000/auth/logout',
        {
          method: 'POST',
          credentials: 'include',
        }
      );
    });
  });

  it('should set user to null after successful logout', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const signOutButton = screen.getByText('Sign out');
    fireEvent.click(signOutButton);

    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith(null);
    });
  });

  it('should handle logout error gracefully', async () => {
    const consoleErrorSpy = jest
      .spyOn(console, 'error')
      .mockImplementation(() => {});
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const signOutButton = screen.getByText('Sign out');
    fireEvent.click(signOutButton);

    await waitFor(() => {
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Logout error:',
        expect.any(Error)
      );
    });

    // Assert the error was handled/logged internally
    expect(consoleErrorSpy).toHaveBeenCalled();
    // Restore console.error to avoid hiding real errors in other tests
    consoleErrorSpy.mockRestore();
  });

  it('should render home link with correct href', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const brainIcon = screen.getByTestId('brain-icon');
    const homeLink = brainIcon.closest('a');
    expect(homeLink).not.toBeNull();
    if (homeLink) {
      expect(homeLink.getAttribute('href')).toBe('/');
    }
  });

  it('should apply outline variant to sign out button', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const signOutButton = screen.getByText('Sign out');
    expect(signOutButton.getAttribute('data-variant')).toBe('outline');
    expect(signOutButton.getAttribute('data-size')).toBe('sm');
  });

  it('should apply rounded-full class to sign out button', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const signOutButton = screen.getByText('Sign out');
    expect(signOutButton.className).toContain('rounded-full');
  });

  it('should render brain icon with correct styling', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const brainIcon = screen.getByTestId('brain-icon');
    expect(brainIcon.className).toContain('h-6');
    expect(brainIcon.className).toContain('w-6');
    expect(brainIcon.className).toContain('text-orange-500');
  });

  it('should have backdrop-blur styling on header', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    const { container } = render(<DashboardHeader />);

    const header = container.querySelector('header');
    expect(header).not.toBeNull();
    if (header) {
      expect(header.className).toContain('backdrop-blur');
      expect(header.className).toContain('border-b');
      expect(header.className).toContain('border-gray-200');
    }
  });

  it('should render all navigation links in order', async () => {
    const { DashboardHeader } = await import(
      '@/components/layout/dashboard-header'
    );
    render(<DashboardHeader />);

    const links = screen.getAllByRole('link');
    const navLinks = links.filter(
      (link) =>
        link.textContent === 'Overview' || link.textContent === 'Predict'
    );

    expect(navLinks).toHaveLength(2);
    expect(navLinks[0].textContent).toBe('Overview');
    expect(navLinks[1].textContent).toBe('Predict');
  });
});
