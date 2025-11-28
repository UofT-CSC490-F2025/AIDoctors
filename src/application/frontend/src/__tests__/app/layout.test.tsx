/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';

// Mock UserProvider
jest.mock('@/components/features/auth/user-context', () => ({
  UserProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="user-provider">{children}</div>
  ),
}));

// Mock next/font/google
jest.mock('next/font/google', () => ({
  Manrope: () => ({
    className: 'mock-manrope-font',
  }),
}));

describe('RootLayout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render children within UserProvider', async () => {
    const { default: RootLayout } = await import('@/app/layout');
    
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    );

    expect(screen.getByTestId('user-provider')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should apply correct HTML attributes', async () => {
    const { default: RootLayout } = await import('@/app/layout');
    
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    );

    // RTL renders the component tree, so html/body are at the document level
    const html = container.closest('html');
    expect(html).not.toBeNull();
    if (html) {
      expect(html.getAttribute('lang')).toBe('en');
      expect(html.className).toContain('mock-manrope-font');
    }
  });

  it('should apply correct body classes', async () => {
    const { default: RootLayout } = await import('@/app/layout');
    
    const { container } = render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    );

    // RTL renders the component tree, so body is at the document level
    const body = container.closest('body');
    expect(body).not.toBeNull();
    if (body) {
      expect(body.className).toContain('min-h-[100dvh]');
      expect(body.className).toContain('bg-gray-50');
    }
  });

  it('should render multiple children correctly', async () => {
    const { default: RootLayout } = await import('@/app/layout');
    
    render(
      <RootLayout>
        <div>First Child</div>
        <div>Second Child</div>
        <span>Third Child</span>
      </RootLayout>
    );

    expect(screen.getByText('First Child')).toBeInTheDocument();
    expect(screen.getByText('Second Child')).toBeInTheDocument();
    expect(screen.getByText('Third Child')).toBeInTheDocument();
  });

  it('should have correct metadata exports', async () => {
    const layoutModule = await import('@/app/layout');
    
    expect(layoutModule.metadata).toBeDefined();
    expect(layoutModule.metadata.title).toBe('AI Doctors');
    expect(layoutModule.metadata.description).toContain('medication interaction');
  });

  it('should have correct viewport exports', async () => {
    const layoutModule = await import('@/app/layout');
    
    expect(layoutModule.viewport).toBeDefined();
    expect(layoutModule.viewport.maximumScale).toBe(1);
  });
});
