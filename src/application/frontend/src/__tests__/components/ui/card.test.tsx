/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardAction,
  CardContent,
  CardFooter,
} from '@/components/ui/card';

describe('Card Components', () => {
  describe('Card', () => {
    it('should render a card', () => {
      render(<Card>Card content</Card>);

      expect(screen.getByText('Card content')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<Card>Test</Card>);

      const card = container.querySelector('[data-slot="card"]');
      expect(card).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(<Card className="custom-class">Test</Card>);

      const card = container.querySelector('[data-slot="card"]');
      expect(card?.className).toContain('custom-class');
    });

    it('should apply default styling', () => {
      const { container } = render(<Card>Test</Card>);

      const card = container.querySelector('[data-slot="card"]');
      expect(card?.className).toContain('rounded-xl');
      expect(card?.className).toContain('border');
      expect(card?.className).toContain('shadow-sm');
    });
  });

  describe('CardHeader', () => {
    it('should render card header', () => {
      render(<CardHeader>Header content</CardHeader>);

      expect(screen.getByText('Header content')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardHeader>Test</CardHeader>);

      const header = container.querySelector('[data-slot="card-header"]');
      expect(header).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardHeader className="custom-class">Test</CardHeader>
      );

      const header = container.querySelector('[data-slot="card-header"]');
      expect(header?.className).toContain('custom-class');
    });
  });

  describe('CardTitle', () => {
    it('should render card title', () => {
      render(<CardTitle>Title text</CardTitle>);

      expect(screen.getByText('Title text')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardTitle>Test</CardTitle>);

      const title = container.querySelector('[data-slot="card-title"]');
      expect(title).toBeInTheDocument();
    });

    it('should apply font styling', () => {
      const { container } = render(<CardTitle>Test</CardTitle>);

      const title = container.querySelector('[data-slot="card-title"]');
      expect(title?.className).toContain('font-semibold');
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardTitle className="custom-class">Test</CardTitle>
      );

      const title = container.querySelector('[data-slot="card-title"]');
      expect(title?.className).toContain('custom-class');
    });
  });

  describe('CardDescription', () => {
    it('should render card description', () => {
      render(<CardDescription>Description text</CardDescription>);

      expect(screen.getByText('Description text')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardDescription>Test</CardDescription>);

      const description = container.querySelector(
        '[data-slot="card-description"]'
      );
      expect(description).toBeInTheDocument();
    });

    it('should apply text styling', () => {
      const { container } = render(<CardDescription>Test</CardDescription>);

      const description = container.querySelector(
        '[data-slot="card-description"]'
      );
      expect(description?.className).toContain('text-sm');
      expect(description?.className).toContain('text-muted-foreground');
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardDescription className="custom-class">Test</CardDescription>
      );

      const description = container.querySelector(
        '[data-slot="card-description"]'
      );
      expect(description?.className).toContain('custom-class');
    });
  });

  describe('CardAction', () => {
    it('should render card action', () => {
      render(<CardAction>Action content</CardAction>);

      expect(screen.getByText('Action content')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardAction>Test</CardAction>);

      const action = container.querySelector('[data-slot="card-action"]');
      expect(action).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardAction className="custom-class">Test</CardAction>
      );

      const action = container.querySelector('[data-slot="card-action"]');
      expect(action?.className).toContain('custom-class');
    });
  });

  describe('CardContent', () => {
    it('should render card content', () => {
      render(<CardContent>Content text</CardContent>);

      expect(screen.getByText('Content text')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardContent>Test</CardContent>);

      const content = container.querySelector('[data-slot="card-content"]');
      expect(content).toBeInTheDocument();
    });

    it('should apply padding', () => {
      const { container } = render(<CardContent>Test</CardContent>);

      const content = container.querySelector('[data-slot="card-content"]');
      expect(content?.className).toContain('px-6');
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardContent className="custom-class">Test</CardContent>
      );

      const content = container.querySelector('[data-slot="card-content"]');
      expect(content?.className).toContain('custom-class');
    });
  });

  describe('CardFooter', () => {
    it('should render card footer', () => {
      render(<CardFooter>Footer text</CardFooter>);

      expect(screen.getByText('Footer text')).toBeInTheDocument();
    });

    it('should have data-slot attribute', () => {
      const { container } = render(<CardFooter>Test</CardFooter>);

      const footer = container.querySelector('[data-slot="card-footer"]');
      expect(footer).toBeInTheDocument();
    });

    it('should apply flex styling', () => {
      const { container } = render(<CardFooter>Test</CardFooter>);

      const footer = container.querySelector('[data-slot="card-footer"]');
      expect(footer?.className).toContain('flex');
      expect(footer?.className).toContain('items-center');
    });

    it('should apply custom className', () => {
      const { container } = render(
        <CardFooter className="custom-class">Test</CardFooter>
      );

      const footer = container.querySelector('[data-slot="card-footer"]');
      expect(footer?.className).toContain('custom-class');
    });
  });

  describe('Card Composition', () => {
    it('should render complete card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
            <CardDescription>Card Description</CardDescription>
            <CardAction>Action</CardAction>
          </CardHeader>
          <CardContent>Card Content</CardContent>
          <CardFooter>Card Footer</CardFooter>
        </Card>
      );

      expect(screen.getByText('Card Title')).toBeInTheDocument();
      expect(screen.getByText('Card Description')).toBeInTheDocument();
      expect(screen.getByText('Action')).toBeInTheDocument();
      expect(screen.getByText('Card Content')).toBeInTheDocument();
      expect(screen.getByText('Card Footer')).toBeInTheDocument();
    });
  });
});
