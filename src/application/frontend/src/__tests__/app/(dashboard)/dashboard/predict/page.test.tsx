/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it, jest, beforeEach } from '@jest/globals';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import React from 'react';

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

const mockSetResults = jest.fn();

// Mock dependencies
jest.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: any) => (
    <div data-testid="card" className={className}>
      {children}
    </div>
  ),
  CardContent: React.forwardRef(({ children, className }: any, ref: any) => (
    <div data-testid="card-content" className={className} ref={ref}>
      {children}
    </div>
  )),
  CardHeader: ({ children }: any) => (
    <div data-testid="card-header">{children}</div>
  ),
  CardTitle: ({ children }: any) => (
    <h3 data-testid="card-title">{children}</h3>
  ),
  CardDescription: ({ children }: any) => (
    <p data-testid="card-description">{children}</p>
  ),
}));

jest.mock('@/components/ui/alert', () => ({
  Alert: ({ info }: any) => (
    <div data-testid="alert">Alert: {info?.drug1_name}</div>
  ),
}));

jest.mock('@/components/forms/prediction-form', () => ({
  PredictionForm: ({ setResults }: any) => {
    // Expose setResults to tests via a button
    return (
      <div data-testid="prediction-form">
        <button
          data-testid="trigger-results"
          onClick={() =>
            setResults({
              drug1: 'Aspirin',
              drug2: 'Warfarin',
              severity: 'major',
              reasoning: 'Test interaction',
              content: {
                predicted_severity: 'Major',
                comparison_to_known_ddi: {
                  known_interaction_exists: true,
                  alignment_with_knowledge: 'aligned',
                  explanation: 'Test',
                },
                historical_cases_analysis: {
                  cases_reviewed: '50',
                  risk_assessment: 'increased_risk',
                  confidence: 'high',
                  reasoning: 'Test',
                },
                clinical_concern_assessment: {
                  should_be_concerned: true,
                  concern_level: 'high',
                  primary_reason: 'severity_level',
                  recommendations: [],
                },
                summary: 'Test',
              },
            })
          }
        >
          Trigger Results
        </button>
        Prediction Form
      </div>
    );
  },
}));

describe('PredictPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the page heading', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(
      screen.getByText('Compare two medications for DDI risk')
    ).toBeInTheDocument();
  });

  it('should render the Predict label', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(screen.getByText('Predict')).toBeInTheDocument();
  });

  it('should render the description text', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(
      screen.getByText(/Submit the patient context plus a current and a new medication/)
    ).toBeInTheDocument();
  });

  it('should render PredictionForm component', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(screen.getByTestId('prediction-form')).toBeInTheDocument();
  });

  it('should render two cards', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    const cards = screen.getAllByTestId('card');
    expect(cards.length).toBeGreaterThanOrEqual(2);
  });

  it('should render Patient & medication details card title', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(screen.getByText('Patient & medication details')).toBeInTheDocument();
  });

  it('should render Alerts card title', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(screen.getByText('Alerts')).toBeInTheDocument();
  });

  it('should render placeholder text when no results', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(screen.getByText('Predictions will appear here.')).toBeInTheDocument();
  });

  it('should render Alert component when results are set', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    const user = userEvent.setup();
    render(<PredictPage />);

    // Click button to trigger results
    const triggerButton = screen.getByTestId('trigger-results');
    await user.click(triggerButton);

    await waitFor(() => {
      expect(screen.getByTestId('alert')).toBeInTheDocument();
    });
  });

  it('should call scrollIntoView when results are set', async () => {
    const scrollIntoViewMock = jest.fn();
    
    // Must set up mock before importing component
    const originalScrollIntoView = Element.prototype.scrollIntoView;
    Element.prototype.scrollIntoView = scrollIntoViewMock;

    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    const user = userEvent.setup();
    render(<PredictPage />);

    // Verify the card-content with ref is rendered
    const cardContents = screen.getAllByTestId('card-content');
    expect(cardContents.length).toBeGreaterThan(0);

    // Click button to trigger results and scroll
    const triggerButton = screen.getByTestId('trigger-results');
    await user.click(triggerButton);

    await waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' });
    });

    // Restore original
    Element.prototype.scrollIntoView = originalScrollIntoView;
  });

  it('should render card descriptions', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    render(<PredictPage />);

    expect(
      screen.getByText(/All fields help the model find similar cohorts/)
    ).toBeInTheDocument();
    expect(
      screen.getByText('Structured output from the prediction service.')
    ).toBeInTheDocument();
  });

  it('should initially not display Alert component', async () => {
    const { default: PredictPage } = await import(
      '@/app/(dashboard)/dashboard/predict/page'
    );
    
    const { container } = render(<PredictPage />);

    // Should show placeholder, not alert
    expect(screen.getByText('Predictions will appear here.')).toBeInTheDocument();
  });
});
