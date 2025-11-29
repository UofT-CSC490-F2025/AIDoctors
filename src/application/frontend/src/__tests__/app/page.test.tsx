/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock useUser hook BEFORE other imports
jest.mock('@/hooks/useUser', () => ({
  useUser: () => ({
    user: null,
    isLoading: false,
  }),
}));

// Mock next/link
jest.mock('next/link', () => ({
  __esModule: true,
  default: ({ children, href, className, ...props }: any) => (
    <a href={href} className={className} {...props}>
      {children}
    </a>
  ),
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  ArrowRight: ({ className }: any) => (
    <span data-testid="arrow-right-icon" className={className} />
  ),
  ShieldCheck: ({ className }: any) => (
    <span data-testid="shield-check-icon" className={className} />
  ),
  Activity: ({ className }: any) => (
    <span data-testid="activity-icon" className={className} />
  ),
  Sparkles: ({ className }: any) => (
    <span data-testid="sparkles-icon" className={className} />
  ),
  Brain: ({ className }: any) => (
    <span data-testid="brain-icon" className={className} />
  ),
}));

// Mock UI components
jest.mock('@/components/ui/button', () => ({
  Button: ({ children, asChild, variant, size, className, ...props }: any) => (
    <button
      data-variant={variant}
      data-size={size}
      className={className}
      {...props}
    >
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/alert', () => ({
  Alert: ({ info, isPreview, className }: any) => (
    <div data-testid="alert" data-preview={isPreview} className={className}>
      Alert Component
    </div>
  ),
}));

describe('HomePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the header with logo', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    const aiDoctorsText = screen.getByText('AI Doctors');
    const brainIcon = screen.getByTestId('brain-icon');

    expect(aiDoctorsText).toBeInTheDocument();
    expect(brainIcon).toBeInTheDocument();
  });

  it('should render the main heading', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(screen.getByText('Catch drug interactions')).toBeInTheDocument();
    expect(screen.getByText('before they become harmful')).toBeInTheDocument();
  });

  it('should render call-to-action buttons', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    const getStartedLink = screen.getByText('Get started').closest('a');
    const loginLinks = screen.getAllByText('Log in');

    expect(getStartedLink).not.toBeNull();
    if (getStartedLink) {
      expect(getStartedLink.getAttribute('href')).toBe('/signup');
    }
    expect(loginLinks.length).toBeGreaterThanOrEqual(1);
    // Check the main CTA button has login link
    const loginLink = loginLinks[0].closest('a');
    expect(loginLink).not.toBeNull();
    if (loginLink) {
      expect(loginLink.getAttribute('href')).toBe('/login');
    }
  });

  it('should render the alert preview', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    const alert = screen.getByTestId('alert');
    expect(alert).toBeInTheDocument();
  });

  it('should render all feature cards', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(screen.getByText('Patient-aware alerts')).toBeInTheDocument();
    expect(screen.getByText('Learn from real outcomes')).toBeInTheDocument();
    expect(screen.getByText('Explainable outputs')).toBeInTheDocument();
  });

  it('should render feature card descriptions', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(
      screen.getByText(/Age, sex, comorbidities, and current meds/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Historical cases from similar patients/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Each alert ships with the evidence/)
    ).toBeInTheDocument();
  });

  it('should render feature card icons', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    // Feature icons in cards
    const shieldIcons = screen.getAllByTestId('shield-check-icon');
    const activityIcons = screen.getAllByTestId('activity-icon');
    const sparklesIcons = screen.getAllByTestId('sparkles-icon');

    expect(shieldIcons.length).toBeGreaterThan(0);
    expect(activityIcons.length).toBeGreaterThan(0);
    expect(sparklesIcons.length).toBeGreaterThan(0);
  });

  it('should render the bottom CTA section', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(screen.getByText('Built for safer prescribing')).toBeInTheDocument();
    const dashboardLink = screen.getByText('Go to dashboard').closest('a');
    expect(dashboardLink).not.toBeNull();
    if (dashboardLink) {
      expect(dashboardLink.getAttribute('href')).toBe('/dashboard');
    }
  });

  it('should render the clinical safety badge', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(screen.getByText('Clinical safety, ML-first')).toBeInTheDocument();
  });

  it('should render the description text', async () => {
    const { default: HomePage } = await import('@/app/page');
    render(<HomePage />);

    expect(
      screen.getByText(/AI Doctors blends trusted DDI tables/)
    ).toBeInTheDocument();
  });
});
