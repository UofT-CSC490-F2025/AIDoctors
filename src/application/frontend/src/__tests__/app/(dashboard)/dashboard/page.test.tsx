/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock dependencies BEFORE any imports
jest.mock('next/link', () => {
  const Link = ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  );
  return {
    __esModule: true,
    default: Link,
  };
});

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, asChild, className, ...props }: any) => (
    <button className={className} {...props}>
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/card', () => ({
  Card: ({ children, ...props }: any) => (
    <div data-testid="card" {...props}>
      {children}
    </div>
  ),
  CardHeader: ({ children, className, ...props }: any) => (
    <div data-testid="card-header" className={className} {...props}>
      {children}
    </div>
  ),
  CardTitle: ({ children, ...props }: any) => (
    <h3 data-testid="card-title" {...props}>
      {children}
    </h3>
  ),
  CardDescription: ({ children, className, ...props }: any) => (
    <p data-testid="card-description" className={className} {...props}>
      {children}
    </p>
  ),
}));

jest.mock('lucide-react', () => ({
  ArrowRight: ({ className, ...props }: any) => (
    <span data-testid="arrow-right-icon" className={className} {...props} />
  ),
  Database: ({ className, ...props }: any) => (
    <span data-testid="database-icon" className={className} {...props} />
  ),
  ShieldCheck: ({ className, ...props }: any) => (
    <span data-testid="shield-check-icon" className={className} {...props} />
  ),
  Sparkles: ({ className, ...props }: any) => (
    <span data-testid="sparkles-icon" className={className} {...props} />
  ),
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the page heading', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(
      screen.getByText('Patient-aware drug interaction alerts')
    ).toBeInTheDocument();
  });

  it('should render the Dashboard label', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('should render the description text', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(
      screen.getByText(/Enable safer prescribing by surfacing patient-specific/)
    ).toBeInTheDocument();
  });

  it('should render the Run a prediction button', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    const link = screen.getByText('Run a prediction').closest('a');
    expect(link).not.toBeNull();
    if (link) {
      expect(link.getAttribute('href')).toBe('/dashboard/predict');
    }
  });

  it('should render all three step cards', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(screen.getByText('Collect context')).toBeInTheDocument();
    expect(screen.getByText('Blend evidence')).toBeInTheDocument();
    expect(screen.getByText('Deliver the top alerts')).toBeInTheDocument();
  });

  it('should render step card descriptions', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(
      screen.getByText(/Age, sex, comorbidities, and current medications/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Combine curated DDI tables with outcomes/)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Return only the most critical, explainable warnings/)
    ).toBeInTheDocument();
  });

  it('should render step icons', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(screen.getByTestId('database-icon')).toBeInTheDocument();
    expect(screen.getByTestId('sparkles-icon')).toBeInTheDocument();
    expect(screen.getByTestId('shield-check-icon')).toBeInTheDocument();
  });

  it('should render arrow icon in button', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    expect(screen.getByTestId('arrow-right-icon')).toBeInTheDocument();
  });

  it('should render three cards', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    render(<DashboardPage />);

    const cards = screen.getAllByTestId('card');
    expect(cards).toHaveLength(3);
  });

  it('should apply correct grid layout classes', async () => {
    const { default: DashboardPage } = await import(
      '@/app/(dashboard)/dashboard/page'
    );

    const { container } = render(<DashboardPage />);

    const grid = container.querySelector('.grid');
    expect(grid).not.toBeNull();
    if (grid) {
      expect(grid.className).toContain('md:grid-cols-3');
    }
  });
});
