/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock dependencies
jest.mock('@/components/features/auth/auth-required', () => ({
  AuthRequired: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="auth-required">{children}</div>
  ),
}));

jest.mock('@/components/layout/dashboard-header', () => ({
  DashboardHeader: () => <header data-testid="dashboard-header">Dashboard Header</header>,
}));

describe('Dashboard Layout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render children within AuthRequired wrapper', async () => {
    const { default: Layout } = await import('@/app/(dashboard)/layout');
    
    render(
      <Layout>
        <div>Dashboard Content</div>
      </Layout>
    );

    expect(screen.getByTestId('auth-required')).toBeInTheDocument();
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
  });

  it('should render the DashboardHeader', async () => {
    const { default: Layout } = await import('@/app/(dashboard)/layout');
    
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    expect(screen.getByTestId('dashboard-header')).toBeInTheDocument();
  });

  it('should apply flex layout classes', async () => {
    const { default: Layout } = await import('@/app/(dashboard)/layout');
    
    const { container } = render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('flex');
    expect(section).toHaveClass('flex-col');
    expect(section).toHaveClass('min-h-screen');
  });

  it('should render multiple children correctly', async () => {
    const { default: Layout } = await import('@/app/(dashboard)/layout');
    
    render(
      <Layout>
        <div>Child 1</div>
        <div>Child 2</div>
        <span>Child 3</span>
      </Layout>
    );

    expect(screen.getByText('Child 1')).toBeInTheDocument();
    expect(screen.getByText('Child 2')).toBeInTheDocument();
    expect(screen.getByText('Child 3')).toBeInTheDocument();
  });

  it('should protect content with AuthRequired', async () => {
    const { default: Layout } = await import('@/app/(dashboard)/layout');
    
    render(
      <Layout>
        <div>Protected Content</div>
      </Layout>
    );

    const authRequired = screen.getByTestId('auth-required');
    expect(authRequired).toBeInTheDocument();
    expect(authRequired).toContainElement(screen.getByText('Protected Content'));
  });
});
