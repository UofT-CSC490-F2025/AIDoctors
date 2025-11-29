/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

const mockPathname = '/dashboard';

// Mock dependencies BEFORE any imports
jest.mock('next/link', () => {
  const Link = ({ children, href, passHref, className, ...props }: any) => (
    <a href={href} className={className} {...props}>
      {children}
    </a>
  );
  return {
    __esModule: true,
    default: Link,
  };
});

jest.mock('next/navigation', () => ({
  usePathname: () => mockPathname,
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, variant, className, ...props }: any) => (
    <button
      onClick={onClick}
      data-variant={variant}
      className={className}
      {...props}
    >
      {children}
    </button>
  ),
}));

jest.mock('lucide-react', () => ({
  Activity: ({ className, ...props }: any) => (
    <span data-testid="activity-icon" className={className} {...props} />
  ),
  Menu: ({ className, ...props }: any) => (
    <span data-testid="menu-icon" className={className} {...props} />
  ),
  Sparkles: ({ className, ...props }: any) => (
    <span data-testid="sparkles-icon" className={className} {...props} />
  ),
}));

jest.mock('@/utils/general', () => ({
  pathname_equal: (path1: string, path2: string) => path1 === path2,
}));

describe('DashboardLayout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render children', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Dashboard Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
  });

  it('should render navigation items', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Predict')).toBeInTheDocument();
  });

  it('should render correct icons for nav items', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByTestId('activity-icon')).toBeInTheDocument();
    expect(screen.getByTestId('sparkles-icon')).toBeInTheDocument();
  });

  it('should render menu toggle button', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByTestId('menu-icon')).toBeInTheDocument();
  });

  it('should toggle sidebar visibility on menu click', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const menuButton = screen.getByTestId('menu-icon').closest('button');
    const sidebar = container.querySelector('aside');

    // Initially should have hidden class on mobile
    expect(sidebar).toHaveClass('hidden');

    // Click to open
    if (menuButton) {
      fireEvent.click(menuButton);
    }

    // Should now have block class
    expect(sidebar).toHaveClass('block');

    // Click to close
    if (menuButton) {
      fireEvent.click(menuButton);
    }

    // Should be hidden again
    expect(sidebar).toHaveClass('hidden');
  });

  it('should render navigation links with correct hrefs', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const overviewLink = screen.getByText('Overview').closest('a');
    const predictLink = screen.getByText('Predict').closest('a');

    expect(overviewLink).toHaveAttribute('href', '/dashboard');
    expect(predictLink).toHaveAttribute('href', '/dashboard/predict');
  });

  it('should apply active styling to current page', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const overviewButton = screen.getByText('Overview').closest('button');
    expect(overviewButton).toHaveAttribute('data-variant', 'secondary');
  });

  it('should close sidebar when nav item is clicked', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const menuButton = screen.getByTestId('menu-icon').closest('button');
    const sidebar = container.querySelector('aside');

    // Open sidebar
    if (menuButton) {
      fireEvent.click(menuButton);
    }
    expect(sidebar).toHaveClass('block');

    // Click nav item
    const overviewButton = screen.getByText('Overview').closest('button');
    if (overviewButton) {
      fireEvent.click(overviewButton);
    }

    // Sidebar should close
    expect(sidebar).toHaveClass('hidden');
  });

  it('should render screen reader text for menu button', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Toggle sidebar')).toHaveClass('sr-only');
  });

  it('should render Dashboard text in mobile header', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('should apply correct container classes', async () => {
    const { default: DashboardLayout } = await import(
      '@/app/(dashboard)/dashboard/layout'
    );

    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    );

    const mainContainer = container.querySelector(
      '.flex.flex-col.min-h-\\[calc\\(100dvh-68px\\)\\]'
    );
    expect(mainContainer).toBeInTheDocument();
  });
});
