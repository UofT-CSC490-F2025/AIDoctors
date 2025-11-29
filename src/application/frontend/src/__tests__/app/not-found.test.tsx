/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock dependencies BEFORE any imports
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
  CircleIcon: ({ className, ...props }: any) => (
    <span data-testid="circle-icon" className={className} {...props} />
  ),
}));

describe('NotFound Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the 404 page heading', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    render(<NotFound />);

    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  });

  it('should render the CircleIcon', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    render(<NotFound />);

    const icon = screen.getByTestId('circle-icon');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveClass('size-12');
    expect(icon).toHaveClass('text-orange-500');
  });

  it('should render the description text', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    render(<NotFound />);

    expect(
      screen.getByText(/The page you are looking for might have been removed/)
    ).toBeInTheDocument();
  });

  it('should render the Back to Home link', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    render(<NotFound />);

    const link = screen.getByText('Back to Home');
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', '/');
  });

  it('should apply correct styling classes', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    const { container } = render(<NotFound />);

    const mainDiv = container.querySelector(
      '.flex.items-center.justify-center'
    );
    expect(mainDiv).toBeInTheDocument();
  });

  it('should center the content vertically', async () => {
    const { default: NotFound } = await import('@/app/not-found');
    const { container } = render(<NotFound />);

    const mainDiv = container.querySelector('.min-h-\\[100dvh\\]');
    expect(mainDiv).toBeInTheDocument();
  });
});
