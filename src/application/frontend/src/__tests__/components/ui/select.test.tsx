/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Select } from '@/components/ui/select';

describe('Select Component', () => {
  it('should render a select element', () => {
    render(
      <Select>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
      </Select>
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
  });

  it('should have data-slot attribute', () => {
    const { container } = render(
      <Select>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select).toBeInTheDocument();
  });

  it('should render options', () => {
    render(
      <Select>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
        <option value="3">Option 3</option>
      </Select>
    );

    expect(screen.getByText('Option 1')).toBeInTheDocument();
    expect(screen.getByText('Option 2')).toBeInTheDocument();
    expect(screen.getByText('Option 3')).toBeInTheDocument();
  });

  it('should apply default styling', () => {
    const { container } = render(
      <Select>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select?.className).toContain('rounded-md');
    expect(select?.className).toContain('border');
    expect(select?.className).toContain('h-9');
  });

  it('should apply custom className', () => {
    const { container } = render(
      <Select className="custom-class">
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select?.className).toContain('custom-class');
  });

  it('should handle value prop', () => {
    render(
      <Select value="2" readOnly>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
      </Select>
    );

    const select = screen.getByRole('combobox') as HTMLSelectElement;
    expect(select.value).toBe('2');
  });

  it('should handle onChange event', () => {
    const handleChange = jest.fn();
    render(
      <Select onChange={handleChange}>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
      </Select>
    );

    const select = screen.getByRole('combobox') as HTMLSelectElement;
    select.value = '2';
    select.dispatchEvent(new Event('change', { bubbles: true }));

    expect(handleChange).toHaveBeenCalled();
  });

  it('should be disabled when disabled prop is true', () => {
    render(
      <Select disabled>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeDisabled();
  });

  it('should apply disabled styling', () => {
    const { container } = render(
      <Select disabled>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select?.className).toContain('disabled:opacity-50');
  });

  it('should handle name attribute', () => {
    render(
      <Select name="category">
        <option value="1">Option 1</option>
      </Select>
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveAttribute('name', 'category');
  });

  it('should handle required attribute', () => {
    render(
      <Select required>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeRequired();
  });

  it('should pass through additional props', () => {
    render(
      <Select data-testid="custom-select" aria-label="Custom select">
        <option value="1">Option 1</option>
      </Select>
    );

    const select = screen.getByTestId('custom-select');
    expect(select).toHaveAttribute('aria-label', 'Custom select');
  });

  it('should handle focus-visible styling', () => {
    const { container } = render(
      <Select>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select?.className).toContain('focus-visible:border-ring');
    expect(select?.className).toContain('focus-visible:ring-ring/50');
  });

  it('should handle aria-invalid styling', () => {
    const { container } = render(
      <Select>
        <option value="1">Option 1</option>
      </Select>
    );

    const select = container.querySelector('[data-slot="select"]');
    expect(select?.className).toContain('aria-invalid:border-destructive');
  });

  it('should render with default option', () => {
    render(
      <Select>
        <option value="">Select an option</option>
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
      </Select>
    );

    expect(screen.getByText('Select an option')).toBeInTheDocument();
  });

  it('should handle multiple options with same value', () => {
    render(
      <Select>
        <option value="1">Option 1</option>
        <option value="1">Duplicate Option 1</option>
      </Select>
    );

    const options = screen.getAllByText(/Option 1/);
    expect(options.length).toBeGreaterThan(0);
  });
});
