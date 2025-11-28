/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  it('should render a button', () => {
    render(<Button>Click me</Button>);

    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should apply default variant styling', () => {
    render(<Button>Default Button</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-primary');
  });

  it('should apply destructive variant styling', () => {
    render(<Button variant="destructive">Delete</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-destructive');
  });

  it('should apply outline variant styling', () => {
    render(<Button variant="outline">Outline</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('border');
  });

  it('should apply secondary variant styling', () => {
    render(<Button variant="secondary">Secondary</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('bg-secondary');
  });

  it('should apply ghost variant styling', () => {
    render(<Button variant="ghost">Ghost</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('hover:bg-accent');
  });

  it('should apply link variant styling', () => {
    render(<Button variant="link">Link</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('underline-offset-4');
  });

  it('should apply default size styling', () => {
    render(<Button>Default Size</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('h-9');
  });

  it('should apply small size styling', () => {
    render(<Button size="sm">Small</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('h-8');
  });

  it('should apply large size styling', () => {
    render(<Button size="lg">Large</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('h-10');
  });

  it('should apply icon size styling', () => {
    render(<Button size="icon">Icon</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('size-9');
  });

  it('should apply custom className', () => {
    render(<Button className="custom-class">Custom</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('custom-class');
  });

  it('should handle onClick event', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button');
    button.click();

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('should apply disabled styling', () => {
    render(<Button disabled>Disabled</Button>);

    const button = screen.getByRole('button');
    expect(button.className).toContain('disabled:opacity-50');
  });

  it('should support button type attribute', () => {
    render(<Button type="submit">Submit</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'submit');
  });

  it('should render as child when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    );

    const link = screen.getByRole('link');
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/test');
  });

  it('should have data-slot attribute', () => {
    render(<Button>Test</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('data-slot', 'button');
  });

  it('should pass through additional props', () => {
    render(<Button data-testid="custom-button">Test</Button>);

    expect(screen.getByTestId('custom-button')).toBeInTheDocument();
  });

  it('should render with multiple variants and sizes', () => {
    const { rerender } = render(
      <Button variant="outline" size="sm">
        Test
      </Button>
    );

    let button = screen.getByRole('button');
    expect(button.className).toContain('border');
    expect(button.className).toContain('h-8');

    rerender(
      <Button variant="destructive" size="lg">
        Test
      </Button>
    );

    button = screen.getByRole('button');
    expect(button.className).toContain('bg-destructive');
    expect(button.className).toContain('h-10');
  });
});
