/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import React from 'react';
import { Alert } from '@/components/ui/alert';
import { AlertResult } from '@/types/predict-types';

const mockAlertInfo: AlertResult = {
  drug1: 'Aspirin',
  drug2: 'Warfarin',
  known_severity: 'major',
  model_path: 'model-v1.0',
  reasoning: 'Test reasoning for the interaction',
  severity: 'severe',
  content: {
    predicted_severity: 'severe',
    comparison_to_known_ddi: {
      known_interaction_exists: true,
      alignment_with_knowledge: 'high',
      explanation: 'Known interaction matches predicted severity',
    },
    historical_cases_analysis: {
      cases_reviewed: '50',
      risk_assessment: 'high risk',
      confidence: 'high',
      reasoning: 'Multiple historical cases show similar patterns',
    },
    clinical_concern_assessment: {
      should_be_concerned: true,
      concern_level: 'critical',
      primary_reason: 'High risk of bleeding complications',
      recommendations: [
        'Close monitoring required',
        'Consider alternative medication',
        'Monitor for signs of bleeding',
      ],
    },
    summary: 'This is a critical drug interaction that requires attention',
  },
};

describe('Alert Component', () => {
  it('should render the alert component', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Alert')).toBeInTheDocument();
  });

  it('should display drug names', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Aspirin + Warfarin')).toBeInTheDocument();
  });

  it('should display model path when provided', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Model: model-v1.0')).toBeInTheDocument();
  });

  it('should not display model path when not provided', () => {
    const infoWithoutModel = { ...mockAlertInfo, model_path: undefined };
    render(<Alert info={infoWithoutModel} />);

    expect(screen.queryByText(/Model:/)).not.toBeInTheDocument();
  });

  it('should display known severity badge', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Known: major')).toBeInTheDocument();
  });

  it('should display predicted severity badge', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Predicted: severe')).toBeInTheDocument();
  });

  it('should not display known severity when not provided', () => {
    const infoWithoutKnown = { ...mockAlertInfo, known_severity: undefined };
    render(<Alert info={infoWithoutKnown} />);

    expect(screen.queryByText(/Known:/)).not.toBeInTheDocument();
  });

  it('should display summary section', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Summary')).toBeInTheDocument();
    expect(
      screen.getByText(
        'This is a critical drug interaction that requires attention'
      )
    ).toBeInTheDocument();
  });

  it('should display reasoning text', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(
      screen.getByText('Test reasoning for the interaction')
    ).toBeInTheDocument();
  });

  it('should display known DDI section', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Known DDI')).toBeInTheDocument();
    expect(screen.getByText('Known interaction')).toBeInTheDocument();
    expect(screen.getByText('Alignment: high')).toBeInTheDocument();
  });

  it('should display "No known interaction" when appropriate', () => {
    const infoNoKnown = {
      ...mockAlertInfo,
      content: {
        ...mockAlertInfo.content,
        comparison_to_known_ddi: {
          ...mockAlertInfo.content.comparison_to_known_ddi,
          known_interaction_exists: false,
        },
      },
    };
    render(<Alert info={infoNoKnown} />);

    expect(screen.getByText('No known interaction')).toBeInTheDocument();
  });

  it('should display historical cases section', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Historical cases')).toBeInTheDocument();
    expect(screen.getByText('50 cases · high risk')).toBeInTheDocument();
    expect(screen.getByText('Confidence: high')).toBeInTheDocument();
  });

  it('should display clinical concern section', () => {
    render(<Alert info={mockAlertInfo} />);

    expect(screen.getByText('Clinical concern')).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <Alert info={mockAlertInfo} className="custom-class" />
    );

    const alert = container.firstChild as HTMLElement;
    expect(alert.className).toContain('custom-class');
  });

  it('should apply preview mode styling when isPreview is true', () => {
    const { container } = render(<Alert info={mockAlertInfo} isPreview />);

    const gridDiv = container.querySelector('.grid');
    expect(gridDiv?.className).not.toContain('md:grid-cols-3');
  });

  it('should apply default grid styling when isPreview is false', () => {
    const { container } = render(
      <Alert info={mockAlertInfo} isPreview={false} />
    );

    const gridDiv = container.querySelector('.grid');
    expect(gridDiv?.className).toContain('md:grid-cols-3');
  });

  it('should pass through additional props', () => {
    render(<Alert info={mockAlertInfo} data-testid="custom-alert" />);

    expect(screen.getByTestId('custom-alert')).toBeInTheDocument();
  });

  it('should display "Low concern" when should_be_concerned is false', () => {
    const infoLowConcern = {
      ...mockAlertInfo,
      content: {
        ...mockAlertInfo.content,
        clinical_concern_assessment: {
          ...mockAlertInfo.content.clinical_concern_assessment,
          should_be_concerned: false,
        },
      },
    };
    render(<Alert info={infoLowConcern} />);

    // This assertion covers the 'Low concern' branch (Line 104)
    expect(screen.getByText(/Low concern/)).toBeInTheDocument();

    // Check for the combined text to ensure context
    expect(screen.getByText(/Low concern · critical/)).toBeInTheDocument();
  });
});
