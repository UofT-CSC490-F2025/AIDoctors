/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { LoadingScreen } from '@/components/ui/loading-screen';

describe('LoadingScreen Component', () => {
  it('should render the loading screen', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv).toBeInTheDocument();
  });

  it('should have fixed positioning', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv?.className).toContain('fixed');
    expect(loadingDiv?.className).toContain('top-0');
    expect(loadingDiv?.className).toContain('left-0');
  });

  it('should have full screen dimensions', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv?.className).toContain('w-screen');
    expect(loadingDiv?.className).toContain('h-screen');
  });

  it('should center content', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv?.className).toContain('flex');
    expect(loadingDiv?.className).toContain('items-center');
    expect(loadingDiv?.className).toContain('justify-center');
  });

  it('should have white background', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv?.className).toContain('bg-white');
  });

  it('should have z-index for overlay', () => {
    const { container } = render(<LoadingScreen />);

    const loadingDiv = container.querySelector('.fixed');
    expect(loadingDiv?.className).toContain('z-50');
  });

  it('should render spinner element', () => {
    const { container } = render(<LoadingScreen />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('should have rounded spinner', () => {
    const { container } = render(<LoadingScreen />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner?.className).toContain('rounded-full');
  });

  it('should have spinner dimensions', () => {
    const { container } = render(<LoadingScreen />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner?.className).toContain('h-16');
    expect(spinner?.className).toContain('w-16');
  });

  it('should have spinner border styling', () => {
    const { container } = render(<LoadingScreen />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner?.className).toContain('border-4');
    expect(spinner?.className).toContain('border-gray-300');
    expect(spinner?.className).toContain('border-t-transparent');
  });

  it('should have animate-spin class', () => {
    const { container } = render(<LoadingScreen />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner?.className).toContain('animate-spin');
  });
});
