/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Label } from '@/components/ui/label';

// Mock radix-ui Label
jest.mock('radix-ui', () => ({
  Label: {
    Root: ({ children, className, ...props }: any) => (
      <label className={className} {...props}>
        {children}
      </label>
    ),
  },
}));

describe('Label Component', () => {
  it('should render a label', () => {
    render(<Label>Test Label</Label>);

    expect(screen.getByText('Test Label')).toBeInTheDocument();
  });

  it('should have data-slot attribute', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label).toBeInTheDocument();
  });

  it('should apply default styling', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('text-sm');
    expect(label?.className).toContain('font-medium');
    expect(label?.className).toContain('flex');
    expect(label?.className).toContain('items-center');
  });

  it('should apply custom className', () => {
    const { container } = render(<Label className="custom-class">Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('custom-class');
  });

  it('should handle htmlFor attribute', () => {
    render(<Label htmlFor="input-id">Test Label</Label>);

    const label = screen.getByText('Test Label');
    expect(label).toHaveAttribute('for', 'input-id');
  });

  it('should render with child elements', () => {
    render(
      <Label>
        <span>Label with</span> <strong>child elements</strong>
      </Label>
    );

    expect(screen.getByText('Label with')).toBeInTheDocument();
    expect(screen.getByText('child elements')).toBeInTheDocument();
  });

  it('should apply gap styling for children', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('gap-2');
  });

  it('should apply select-none styling', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('select-none');
  });

  it('should apply disabled styling when in disabled group', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('group-data-[disabled=true]:opacity-50');
  });

  it('should apply peer-disabled styling', () => {
    const { container } = render(<Label>Test</Label>);

    const label = container.querySelector('[data-slot="label"]');
    expect(label?.className).toContain('peer-disabled:opacity-50');
  });

  it('should pass through additional props', () => {
    render(<Label data-testid="custom-label">Test</Label>);

    expect(screen.getByTestId('custom-label')).toBeInTheDocument();
  });

  it('should render as accessible label element', () => {
    render(<Label>Accessible Label</Label>);

    const label = screen.getByText('Accessible Label');
    expect(label.tagName).toBe('LABEL');
  });
});
