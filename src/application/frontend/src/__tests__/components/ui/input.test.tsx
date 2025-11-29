/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Input } from '@/components/ui/input';

describe('Input Component', () => {
  it('should render an input field', () => {
    render(<Input placeholder="Enter text" />);

    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('should have data-slot attribute', () => {
    const { container } = render(<Input />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input).toBeInTheDocument();
  });

  it('should apply custom type', () => {
    render(<Input type="email" data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('type', 'email');
  });

  it('should apply custom className', () => {
    const { container } = render(<Input className="custom-class" />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input?.className).toContain('custom-class');
  });

  it('should apply default styling', () => {
    const { container } = render(<Input />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input?.className).toContain('rounded-md');
    expect(input?.className).toContain('border');
    expect(input?.className).toContain('h-9');
  });

  it('should handle placeholder', () => {
    render(<Input placeholder="Test placeholder" />);

    expect(screen.getByPlaceholderText('Test placeholder')).toBeInTheDocument();
  });

  it('should handle value prop', () => {
    render(<Input value="Test value" readOnly />);

    const input = screen.getByDisplayValue('Test value');
    expect(input).toBeInTheDocument();
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Input disabled data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toBeDisabled();
  });

  it('should apply disabled styling', () => {
    const { container } = render(<Input disabled />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input?.className).toContain('disabled:opacity-50');
  });

  it('should handle name attribute', () => {
    render(<Input name="username" data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('name', 'username');
  });

  it('should handle required attribute', () => {
    render(<Input required data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toBeRequired();
  });

  it('should handle readOnly attribute', () => {
    render(<Input readOnly data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('readOnly');
  });

  it('should handle maxLength attribute', () => {
    render(<Input maxLength={10} data-testid="input" />);

    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('maxLength', '10');
  });

  it('should pass through additional props', () => {
    render(<Input data-testid="custom-input" aria-label="Custom input" />);

    const input = screen.getByTestId('custom-input');
    expect(input).toHaveAttribute('aria-label', 'Custom input');
  });

  it('should handle focus-visible styling', () => {
    const { container } = render(<Input />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input?.className).toContain('focus-visible:border-ring');
    expect(input?.className).toContain('focus-visible:ring-ring/50');
  });

  it('should handle aria-invalid styling', () => {
    const { container } = render(<Input />);

    const input = container.querySelector('[data-slot="input"]');
    expect(input?.className).toContain('aria-invalid:border-destructive');
  });
});
