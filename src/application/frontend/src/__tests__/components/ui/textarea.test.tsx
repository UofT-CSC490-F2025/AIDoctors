/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Textarea } from '@/components/ui/textarea';

describe('Textarea Component', () => {
  it('should render a textarea', () => {
    render(<Textarea placeholder="Enter text" />);

    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('should apply default styling', () => {
    const { container } = render(<Textarea />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('rounded-md');
    expect(textarea?.className).toContain('border');
    expect(textarea?.className).toContain('min-h-[80px]');
  });

  it('should apply custom className', () => {
    const { container } = render(<Textarea className="custom-class" />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('custom-class');
  });

  it('should handle placeholder', () => {
    render(<Textarea placeholder="Test placeholder" />);

    expect(screen.getByPlaceholderText('Test placeholder')).toBeInTheDocument();
  });

  it('should handle value prop', () => {
    render(<Textarea value="Test value" readOnly />);

    const textarea = screen.getByDisplayValue('Test value');
    expect(textarea).toBeInTheDocument();
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Textarea disabled data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeDisabled();
  });

  it('should apply disabled styling', () => {
    const { container } = render(<Textarea disabled />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('disabled:opacity-50');
  });

  it('should handle name attribute', () => {
    render(<Textarea name="description" data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('name', 'description');
  });

  it('should handle required attribute', () => {
    render(<Textarea required data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeRequired();
  });

  it('should handle readOnly attribute', () => {
    render(<Textarea readOnly data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('readOnly');
  });

  it('should handle rows attribute', () => {
    render(<Textarea rows={5} data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('rows', '5');
  });

  it('should handle maxLength attribute', () => {
    render(<Textarea maxLength={100} data-testid="textarea" />);

    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('maxLength', '100');
  });

  it('should forward ref correctly', () => {
    const ref = React.createRef<HTMLTextAreaElement>();
    render(<Textarea ref={ref} />);

    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('should pass through additional props', () => {
    render(
      <Textarea data-testid="custom-textarea" aria-label="Custom textarea" />
    );

    const textarea = screen.getByTestId('custom-textarea');
    expect(textarea).toHaveAttribute('aria-label', 'Custom textarea');
  });

  it('should handle focus-visible styling', () => {
    const { container } = render(<Textarea />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('focus-visible:border-ring');
    expect(textarea?.className).toContain('focus-visible:ring-ring/50');
  });

  it('should handle aria-invalid styling', () => {
    const { container } = render(<Textarea />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('aria-invalid:border-destructive');
  });

  it('should apply shadow styling', () => {
    const { container } = render(<Textarea />);

    const textarea = container.querySelector('textarea');
    expect(textarea?.className).toContain('shadow-xs');
  });
});
